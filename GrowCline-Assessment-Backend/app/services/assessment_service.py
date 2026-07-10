"""
Assessment Service Module
Responsible for:
- Creating custom and automated random assessments
- Managing question assignments (aptitude, technical, coding)
- Managing assessment lifecycles: Start, Submit, Save, Update Status
- Retrieving candidate assessments and paginated listings
- Enforcing strict assessment state validation and expiration rules

Architecture: Controller -> Service -> Model -> MongoDB
"""

import logging
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime
from bson import ObjectId
from pymongo.errors import PyMongoError

try:
    from config.database import Database
except ImportError:
    from app.config.database import Database

try:
    from models.assessment_model import Assessment
    from services.question_service import QuestionService, QUESTION_TYPE_APTITUDE, QUESTION_TYPE_TECHNICAL, QUESTION_TYPE_CODING
    from services.scoring_service import ScoringService
except ImportError:
    from app.models.assessment_model import Assessment
    from app.services.question_service import QuestionService, QUESTION_TYPE_APTITUDE, QUESTION_TYPE_TECHNICAL, QUESTION_TYPE_CODING
    from app.services.scoring_service import ScoringService

logger = logging.getLogger(__name__)

# Assessment State Constants
STATUS_PENDING = "Pending"
STATUS_IN_PROGRESS = "In Progress"
STATUS_SUBMITTED = "Submitted"
STATUS_COMPLETED = "Completed"
STATUS_EXPIRED = "Expired"
STATUS_CANCELLED = "Cancelled"

VALID_STATUSES = {
    STATUS_PENDING,
    STATUS_IN_PROGRESS,
    STATUS_SUBMITTED,
    STATUS_COMPLETED,
    STATUS_EXPIRED,
    STATUS_CANCELLED
}


class AssessmentService:
    """
    Service class responsible for managing assessment lifecycles, random question assembly,
    secure test-paper generation (stripping answers), and evaluation delegation.
    """

    @classmethod
    def validate_assessment_state(
        cls,
        assessment_doc: Dict[str, Any],
        required_status: Union[str, List[str]],
        check_expiry: bool = True
    ) -> Tuple[bool, str]:
        """
        Enforces strict lifecycle state transition rules and checks expiration timestamps.

        Args:
            assessment_doc (Dict[str, Any]): MongoDB assessment document.
            required_status (Union[str, List[str]]): Status or list of statuses permitted for the action.
            check_expiry (bool): If True, validates whether the assessment has expired.

        Returns:
            Tuple[bool, str]: (Is Valid, Error Message if invalid)
        """
        if not assessment_doc:
            return False, "Assessment document is missing or not found."

        current_status = assessment_doc.get("status", STATUS_PENDING)

        # Check expiration timestamp
        if check_expiry and assessment_doc.get("expiresAt"):
            expires_at = assessment_doc["expiresAt"]
            if isinstance(expires_at, datetime) and datetime.utcnow() > expires_at:
                # Automatically mark as expired if not already completed/submitted
                if current_status not in {STATUS_SUBMITTED, STATUS_COMPLETED, STATUS_EXPIRED}:
                    try:
                        db = Database.get_db()
                        db.assessments.update_one(
                            {"_id": assessment_doc["_id"]},
                            {"$set": {"status": STATUS_EXPIRED, "updatedAt": datetime.utcnow()}}
                        )
                    except Exception as e:
                        logger.warning(f"Failed to auto-expire assessment {assessment_doc['_id']}: {str(e)}")
                return False, "Assessment time window has expired."

        # Check required status match
        permitted_set = {required_status} if isinstance(required_status, str) else set(required_status)
        if current_status not in permitted_set:
            return False, f"Invalid assessment state '{current_status}'. This action requires state: {', '.join(permitted_set)}."

        return True, ""

    @classmethod
    def _calculate_total_marks_from_questions(
        cls,
        aptitude_ids: List[ObjectId],
        technical_ids: List[ObjectId],
        coding_ids: List[ObjectId]
    ) -> float:
        """
        Helper to calculate total marks by querying assigned questions from DB.

        Args:
            aptitude_ids (List[ObjectId]): Aptitude question ObjectIds.
            technical_ids (List[ObjectId]): Technical question ObjectIds.
            coding_ids (List[ObjectId]): Coding question ObjectIds.

        Returns:
            float: Total marks sum across all sections.
        """
        db = Database.get_db()
        total_marks = 0.0

        if aptitude_ids:
            for q in db.aptitude_questions.find({"_id": {"$in": aptitude_ids}}, {"marks": 1}):
                total_marks += float(q.get("marks", 1.0))
        if technical_ids:
            for q in db.technical_questions.find({"_id": {"$in": technical_ids}}, {"marks": 1}):
                total_marks += float(q.get("marks", 1.0))
        if coding_ids:
            for q in db.coding_questions.find({"_id": {"$in": coding_ids}}, {"marks": 1}):
                total_marks += float(q.get("marks", 10.0))

        return total_marks

    @classmethod
    def create_assessment(cls, payload: Dict[str, Any], created_by: Optional[str] = None) -> Dict[str, Any]:
        """
        Creates a custom assessment from a specified list of question IDs.

        Args:
            payload (Dict[str, Any]): Attributes including title, userId, question ID lists, duration.
            created_by (Optional[str]): User ID of the creator.

        Returns:
            Dict[str, Any]: Standardized API response.
        """
        try:
            title = payload.get("title", "Untitled Assessment")
            assessment_type = payload.get("assessmentType") or payload.get("assessment_type", "General")
            user_id = payload.get("userId") or payload.get("user_id")

            if not user_id or not ObjectId.is_valid(user_id):
                return {"success": False, "status_code": 400, "message": "Valid 'userId' is required.", "error": "INVALID_USER_ID"}

            apt_raw = payload.get("aptitudeQuestions", payload.get("aptitudeQuestionIds", []))
            tech_raw = payload.get("technicalQuestions", payload.get("technicalQuestionIds", []))
            code_raw = payload.get("codingQuestions", payload.get("codingQuestionIds", []))
            aptitude_ids = [str(qid) for qid in apt_raw if ObjectId.is_valid(qid)]
            technical_ids = [str(qid) for qid in tech_raw if ObjectId.is_valid(qid)]
            coding_ids = [str(qid) for qid in code_raw if ObjectId.is_valid(qid)]

            duration = int(payload.get("duration", 60))
            passing_percentage = float(payload.get("passingPercentage", 40.0))
            instructions = payload.get("instructions", ["Read all questions carefully.", "Manage your time effectively."])
            scheduled_at = payload.get("scheduledAt")
            expires_at = payload.get("expiresAt")

            # Parse ISO date strings if provided
            if isinstance(scheduled_at, str):
                try: scheduled_at = datetime.fromisoformat(scheduled_at.replace("Z", "+00:00"))
                except Exception: scheduled_at = None
            if isinstance(expires_at, str):
                try: expires_at = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
                except Exception: expires_at = None

            # Compute total marks if not overridden
            total_marks = payload.get("totalMarks")
            if total_marks is None:
                total_marks = cls._calculate_total_marks_from_questions(
                    [ObjectId(qid) for qid in aptitude_ids],
                    [ObjectId(qid) for qid in technical_ids],
                    [ObjectId(qid) for qid in coding_ids]
                )

            doc = Assessment.create_assessment(
                title=title,
                assessment_type=assessment_type,
                user_id=user_id,
                aptitude_questions=aptitude_ids,
                technical_questions=technical_ids,
                coding_questions=coding_ids,
                duration=duration,
                total_marks=float(total_marks),
                created_by=created_by or payload.get("createdBy"),
                instructions=instructions,
                passing_percentage=passing_percentage,
                scheduled_at=scheduled_at,
                expires_at=expires_at
            )

            db = Database.get_db()
            res = db.assessments.insert_one(doc)
            logger.info(f"Created assessment ID {res.inserted_id} for user {user_id}")

            return {
                "success": True,
                "status_code": 201,
                "message": "Assessment created successfully.",
                "data": Assessment.response(doc)
            }

        except PyMongoError as db_err:
            logger.error(f"Database error in create_assessment: {str(db_err)}")
            return {"success": False, "status_code": 500, "message": "Database error saving assessment.", "error": "DATABASE_ERROR"}
        except Exception as err:
            logger.critical(f"Unexpected error in create_assessment: {str(err)}", exc_info=True)
            return {"success": False, "status_code": 500, "message": "Internal server error.", "error": "INTERNAL_SERVER_ERROR"}

    @classmethod
    def generate_random_assessment(cls, payload: Dict[str, Any], created_by: Optional[str] = None) -> Dict[str, Any]:
        """
        Automates assessment creation by sampling random active questions across categories.
        Scales cleanly without requiring manual question curation.

        Args:
            payload (Dict[str, Any]): Attributes including question counts, difficulty, technology, user_id.
            created_by (Optional[str]): Admin/creator ID.

        Returns:
            Dict[str, Any]: Standardized API response with assembled assessment details.
        """
        try:
            user_id = payload.get("userId") or payload.get("user_id")
            if not user_id or not ObjectId.is_valid(user_id):
                return {"success": False, "status_code": 400, "message": "Valid 'userId' is required.", "error": "INVALID_USER_ID"}

            apt_count = int(payload.get("aptitudeCount", 5))
            tech_count = int(payload.get("technicalCount", 10))
            cod_count = int(payload.get("codingCount", 2))

            difficulty = payload.get("difficulty")
            technology = payload.get("technology")
            category = payload.get("category")

            # Sample random questions using QuestionService
            apt_res = QuestionService.generate_random_questions(QUESTION_TYPE_APTITUDE, size=apt_count, difficulty=difficulty, category=category)
            tech_res = QuestionService.generate_random_questions(QUESTION_TYPE_TECHNICAL, size=tech_count, difficulty=difficulty, technology=technology, category=category)
            cod_res = QuestionService.generate_random_questions(QUESTION_TYPE_CODING, size=cod_count, difficulty=difficulty, category=category)

            apt_ids = [q["id"] for q in apt_res.get("data", []) if "id" in q]
            tech_ids = [q["id"] for q in tech_res.get("data", []) if "id" in q]
            cod_ids = [q["id"] for q in cod_res.get("data", []) if "id" in q]

            title = payload.get("title", f"AI Generated {technology or 'Full Stack'} Assessment")
            payload["aptitudeQuestions"] = apt_ids
            payload["technicalQuestions"] = tech_ids
            payload["codingQuestions"] = cod_ids
            payload["title"] = title

            return cls.create_assessment(payload, created_by=created_by)

        except Exception as err:
            logger.critical(f"Error in generate_random_assessment: {str(err)}", exc_info=True)
            return {"success": False, "status_code": 500, "message": "Internal server error.", "error": "INTERNAL_SERVER_ERROR"}

    @classmethod
    def assign_questions(
        cls,
        assessment_id: str,
        question_type: str,
        question_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Assigns or updates questions for a specific assessment section.
        Enforces state validation (must be Pending).

        Args:
            assessment_id (str): Assessment ObjectId.
            question_type (str): Section type ('aptitude', 'technical', 'coding').
            question_ids (List[str]): List of valid question ObjectId strings.

        Returns:
            Dict[str, Any]: Standardized API response.
        """
        try:
            if not ObjectId.is_valid(assessment_id):
                return {"success": False, "status_code": 400, "message": "Invalid assessment ID.", "error": "INVALID_OBJECT_ID"}

            db = Database.get_db()
            doc = db.assessments.find_one({"_id": ObjectId(assessment_id)})
            if not doc:
                return {"success": False, "status_code": 404, "message": "Assessment not found.", "error": "ASSESSMENT_NOT_FOUND"}

            is_valid, err_msg = cls.validate_assessment_state(doc, STATUS_PENDING)
            if not is_valid:
                return {"success": False, "status_code": 400, "message": err_msg, "error": "INVALID_STATE"}

            valid_qids = [ObjectId(qid) for qid in question_ids if ObjectId.is_valid(qid)]
            q_type_clean = question_type.lower().strip()

            if q_type_clean == QUESTION_TYPE_APTITUDE:
                field_name = "aptitudeQuestions"
            elif q_type_clean == QUESTION_TYPE_TECHNICAL:
                field_name = "technicalQuestions"
            elif q_type_clean == QUESTION_TYPE_CODING:
                field_name = "codingQuestions"
            else:
                return {"success": False, "status_code": 400, "message": "Invalid question type.", "error": "INVALID_QUESTION_TYPE"}

            # Update document array
            db.assessments.update_one(
                {"_id": ObjectId(assessment_id)},
                {"$set": {field_name: valid_qids, "updatedAt": datetime.utcnow()}}
            )

            # Re-fetch document and update totalQuestions and totalMarks
            updated_doc = db.assessments.find_one({"_id": ObjectId(assessment_id)})
            if updated_doc:
                apt_list = updated_doc.get("aptitudeQuestions", [])
                tech_list = updated_doc.get("technicalQuestions", [])
                cod_list = updated_doc.get("codingQuestions", [])

                total_q = len(apt_list) + len(tech_list) + len(cod_list)
                total_m = cls._calculate_total_marks_from_questions(apt_list, tech_list, cod_list)

                db.assessments.update_one(
                    {"_id": ObjectId(assessment_id)},
                    {"$set": {"totalQuestions": total_q, "totalMarks": total_m, "updatedAt": datetime.utcnow()}}
                )
                updated_doc["totalQuestions"] = total_q
                updated_doc["totalMarks"] = total_m

            logger.info(f"Assigned {len(valid_qids)} {question_type} questions to assessment {assessment_id}")
            return {
                "success": True,
                "status_code": 200,
                "message": f"{question_type.capitalize()} questions assigned successfully.",
                "data": Assessment.response(updated_doc) if updated_doc else {}
            }

        except PyMongoError as db_err:
            logger.error(f"Database error assigning questions: {str(db_err)}")
            return {"success": False, "status_code": 500, "message": "Database error.", "error": "DATABASE_ERROR"}
        except Exception as err:
            logger.critical(f"Unexpected error in assign_questions: {str(err)}", exc_info=True)
            return {"success": False, "status_code": 500, "message": "Internal server error.", "error": "INTERNAL_SERVER_ERROR"}

    @classmethod
    def assign_aptitude_questions(cls, assessment_id: str, question_ids: List[str]) -> Dict[str, Any]:
        return cls.assign_questions(assessment_id, QUESTION_TYPE_APTITUDE, question_ids)

    @classmethod
    def assign_technical_questions(cls, assessment_id: str, question_ids: List[str]) -> Dict[str, Any]:
        return cls.assign_questions(assessment_id, QUESTION_TYPE_TECHNICAL, question_ids)

    @classmethod
    def assign_coding_questions(cls, assessment_id: str, question_ids: List[str]) -> Dict[str, Any]:
        return cls.assign_questions(assessment_id, QUESTION_TYPE_CODING, question_ids)

    @classmethod
    def start_assessment(cls, assessment_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Initiates an assessment session. Transitions state from Pending to In Progress,
        records startedAt timestamp, and returns full question test paper with answers stripped.

        Args:
            assessment_id (str): Assessment ObjectId.
            user_id (Optional[str]): Verifies ownership if provided.

        Returns:
            Dict[str, Any]: Standardized API response containing test paper.
        """
        try:
            if not ObjectId.is_valid(assessment_id):
                return {"success": False, "status_code": 400, "message": "Invalid assessment ID.", "error": "INVALID_OBJECT_ID"}

            db = Database.get_db()
            doc = db.assessments.find_one({"_id": ObjectId(assessment_id)})
            if not doc:
                return {"success": False, "status_code": 404, "message": "Assessment not found.", "error": "ASSESSMENT_NOT_FOUND"}

            if user_id and ObjectId.is_valid(user_id) and str(doc.get("userId")) != str(user_id):
                return {"success": False, "status_code": 403, "message": "You are not authorized to start this assessment.", "error": "FORBIDDEN"}

            is_valid, err_msg = cls.validate_assessment_state(doc, [STATUS_PENDING, STATUS_IN_PROGRESS])
            if not is_valid:
                return {"success": False, "status_code": 400, "message": err_msg, "error": "INVALID_STATE"}

            now = datetime.utcnow()
            update_fields: Dict[str, Any] = {"status": STATUS_IN_PROGRESS, "updatedAt": now}
            if doc.get("status") == STATUS_PENDING or not doc.get("startedAt"):
                update_fields["startedAt"] = now

            db.assessments.update_one({"_id": ObjectId(assessment_id)}, {"$set": update_fields})
            doc.update(update_fields)

            # Assemble test paper by batch fetching questions and stripping answers
            apt_ids = doc.get("aptitudeQuestions", [])
            tech_ids = doc.get("technicalQuestions", [])
            cod_ids = doc.get("codingQuestions", [])

            apt_questions = []
            if apt_ids:
                for q in db.aptitude_questions.find({"_id": {"$in": apt_ids}}):
                    q["id"] = str(q["_id"])
                    q.pop("_id", None)
                    q.pop("correctAnswer", None)
                    q.pop("correct_answer", None)
                    apt_questions.append(q)

            tech_questions = []
            if tech_ids:
                for q in db.technical_questions.find({"_id": {"$in": tech_ids}}):
                    q["id"] = str(q["_id"])
                    q.pop("_id", None)
                    q.pop("correctAnswer", None)
                    q.pop("correct_answer", None)
                    tech_questions.append(q)

            cod_questions = []
            if cod_ids:
                for q in db.coding_questions.find({"_id": {"$in": cod_ids}}):
                    q["id"] = str(q["_id"])
                    q.pop("_id", None)
                    q.pop("hiddenTestCases", None)
                    cod_questions.append(q)

            test_paper = Assessment.response(doc)
            test_paper["aptitudeQuestionsList"] = apt_questions
            test_paper["technicalQuestionsList"] = tech_questions
            test_paper["codingQuestionsList"] = cod_questions

            logger.info(f"Started assessment {assessment_id} for user {user_id or doc.get('userId')}")
            return {
                "success": True,
                "status_code": 200,
                "message": "Assessment started successfully. Good luck!",
                "data": test_paper
            }

        except PyMongoError as db_err:
            logger.error(f"Database error in start_assessment: {str(db_err)}")
            return {"success": False, "status_code": 500, "message": "Database error.", "error": "DATABASE_ERROR"}
        except Exception as err:
            logger.critical(f"Unexpected error in start_assessment: {str(err)}", exc_info=True)
            return {"success": False, "status_code": 500, "message": "Internal server error.", "error": "INTERNAL_SERVER_ERROR"}

    @classmethod
    def submit_assessment(
        cls,
        assessment_id: str,
        user_id: str,
        submission_payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Submits candidate answers, validates state, calculates scores via ScoringService,
        and transitions status to Completed.

        Args:
            assessment_id (str): Assessment ObjectId.
            user_id (str): Candidate User ObjectId.
            submission_payload (Dict[str, Any]): Answer payloads and time tracking.

        Returns:
            Dict[str, Any]: Standardized API response with grading summary.
        """
        try:
            if not ObjectId.is_valid(assessment_id) or not ObjectId.is_valid(user_id):
                return {"success": False, "status_code": 400, "message": "Invalid IDs.", "error": "INVALID_OBJECT_ID"}

            db = Database.get_db()
            doc = db.assessments.find_one({"_id": ObjectId(assessment_id)})
            if not doc:
                return {"success": False, "status_code": 404, "message": "Assessment not found.", "error": "ASSESSMENT_NOT_FOUND"}

            if str(doc.get("userId")) != str(user_id):
                return {"success": False, "status_code": 403, "message": "Unauthorized assessment submission.", "error": "FORBIDDEN"}

            is_valid, err_msg = cls.validate_assessment_state(doc, [STATUS_IN_PROGRESS, STATUS_PENDING])
            if not is_valid:
                return {"success": False, "status_code": 400, "message": err_msg, "error": "INVALID_STATE"}

            # Delegate evaluation to ScoringService
            logger.info(f"Delegating assessment {assessment_id} submission evaluation to ScoringService.")
            eval_res = ScoringService.calculate_and_save_result(assessment_id, user_id, submission_payload)

            if eval_res.get("success"):
                db.assessments.update_one(
                    {"_id": ObjectId(assessment_id)},
                    {"$set": {"status": STATUS_COMPLETED, "submittedAt": datetime.utcnow(), "updatedAt": datetime.utcnow()}}
                )

            return eval_res

        except Exception as err:
            logger.critical(f"Unexpected error in submit_assessment: {str(err)}", exc_info=True)
            return {"success": False, "status_code": 500, "message": "Internal server error.", "error": "INTERNAL_SERVER_ERROR"}

    @classmethod
    def save_assessment(cls, assessment_id: str, save_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates assessment properties such as title, instructions, duration, or time window.
        Enforces state validation (must be Pending).

        Args:
            assessment_id (str): Assessment ObjectId.
            save_data (Dict[str, Any]): Fields to update.

        Returns:
            Dict[str, Any]: Standardized API response.
        """
        try:
            if not ObjectId.is_valid(assessment_id):
                return {"success": False, "status_code": 400, "message": "Invalid assessment ID.", "error": "INVALID_OBJECT_ID"}

            if not save_data:
                return {"success": False, "status_code": 400, "message": "No data provided to save.", "error": "EMPTY_PAYLOAD"}

            db = Database.get_db()
            doc = db.assessments.find_one({"_id": ObjectId(assessment_id)})
            if not doc:
                return {"success": False, "status_code": 404, "message": "Assessment not found.", "error": "ASSESSMENT_NOT_FOUND"}

            is_valid, err_msg = cls.validate_assessment_state(doc, STATUS_PENDING, check_expiry=False)
            if not is_valid:
                return {"success": False, "status_code": 400, "message": err_msg, "error": "INVALID_STATE"}

            fields_to_update = dict(save_data)
            for immutable in ["_id", "id", "userId", "createdAt", "startedAt", "submittedAt"]:
                fields_to_update.pop(immutable, None)
            fields_to_update["updatedAt"] = datetime.utcnow()

            db.assessments.update_one({"_id": ObjectId(assessment_id)}, {"$set": fields_to_update})
            updated_doc = db.assessments.find_one({"_id": ObjectId(assessment_id)})

            return {
                "success": True,
                "status_code": 200,
                "message": "Assessment saved successfully.",
                "data": Assessment.response(updated_doc) if updated_doc else {}
            }

        except PyMongoError as db_err:
            logger.error(f"Database error in save_assessment: {str(db_err)}")
            return {"success": False, "status_code": 500, "message": "Database update error.", "error": "DATABASE_ERROR"}
        except Exception as err:
            logger.critical(f"Unexpected error in save_assessment: {str(err)}", exc_info=True)
            return {"success": False, "status_code": 500, "message": "Internal server error.", "error": "INTERNAL_SERVER_ERROR"}

    @classmethod
    def update_assessment_status(cls, assessment_id: str, new_status: str) -> Dict[str, Any]:
        """
        Manually overrides or updates the assessment lifecycle status.

        Args:
            assessment_id (str): Assessment ObjectId.
            new_status (str): Target status string.

        Returns:
            Dict[str, Any]: Standardized API response.
        """
        try:
            if not ObjectId.is_valid(assessment_id):
                return {"success": False, "status_code": 400, "message": "Invalid assessment ID.", "error": "INVALID_OBJECT_ID"}

            clean_status = new_status.strip().title()
            if clean_status not in VALID_STATUSES:
                return {
                    "success": False,
                    "status_code": 400,
                    "message": f"Invalid status '{new_status}'. Must be one of: {', '.join(VALID_STATUSES)}",
                    "error": "INVALID_STATUS"
                }

            db = Database.get_db()
            res = db.assessments.update_one(
                {"_id": ObjectId(assessment_id)},
                {"$set": {"status": clean_status, "updatedAt": datetime.utcnow()}}
            )

            if res.matched_count == 0:
                return {"success": False, "status_code": 404, "message": "Assessment not found.", "error": "ASSESSMENT_NOT_FOUND"}

            logger.info(f"Updated status of assessment {assessment_id} to {clean_status}")
            updated_doc = db.assessments.find_one({"_id": ObjectId(assessment_id)})
            return {
                "success": True,
                "status_code": 200,
                "message": f"Assessment status updated to '{clean_status}'.",
                "data": Assessment.response(updated_doc) if updated_doc else {}
            }

        except PyMongoError as db_err:
            logger.error(f"Database error updating status: {str(db_err)}")
            return {"success": False, "status_code": 500, "message": "Database update error.", "error": "DATABASE_ERROR"}
        except Exception as err:
            logger.critical(f"Unexpected error in update_assessment_status: {str(err)}", exc_info=True)
            return {"success": False, "status_code": 500, "message": "Internal server error.", "error": "INTERNAL_SERVER_ERROR"}

    @classmethod
    def get_assessment_by_id(cls, assessment_id: str, include_questions: bool = False, strip_answers: bool = True) -> Dict[str, Any]:
        """
        Retrieves assessment details by ObjectId. Optionally populates assigned questions.

        Args:
            assessment_id (str): Assessment ObjectId.
            include_questions (bool): If True, queries question collections to attach full question data.
            strip_answers (bool): If True, masks correct answers and hidden test cases.

        Returns:
            Dict[str, Any]: Standardized API response.
        """
        try:
            if not ObjectId.is_valid(assessment_id):
                return {"success": False, "status_code": 400, "message": "Invalid assessment ID.", "error": "INVALID_OBJECT_ID"}

            db = Database.get_db()
            doc = db.assessments.find_one({"_id": ObjectId(assessment_id)})
            if not doc:
                return {"success": False, "status_code": 404, "message": "Assessment not found.", "error": "ASSESSMENT_NOT_FOUND"}

            formatted = Assessment.response(doc)

            if include_questions:
                apt_ids = doc.get("aptitudeQuestions", [])
                tech_ids = doc.get("technicalQuestions", [])
                cod_ids = doc.get("codingQuestions", [])

                if apt_ids:
                    formatted["aptitudeQuestionsList"] = []
                    for q in db.aptitude_questions.find({"_id": {"$in": apt_ids}}):
                        q["id"] = str(q["_id"]); q.pop("_id", None)
                        if strip_answers: q.pop("correctAnswer", None); q.pop("correct_answer", None)
                        formatted["aptitudeQuestionsList"].append(q)

                if tech_ids:
                    formatted["technicalQuestionsList"] = []
                    for q in db.technical_questions.find({"_id": {"$in": tech_ids}}):
                        q["id"] = str(q["_id"]); q.pop("_id", None)
                        if strip_answers: q.pop("correctAnswer", None); q.pop("correct_answer", None)
                        formatted["technicalQuestionsList"].append(q)

                if cod_ids:
                    formatted["codingQuestionsList"] = []
                    for q in db.coding_questions.find({"_id": {"$in": cod_ids}}):
                        q["id"] = str(q["_id"]); q.pop("_id", None)
                        if strip_answers: q.pop("hiddenTestCases", None)
                        formatted["codingQuestionsList"].append(q)

            return {
                "success": True,
                "status_code": 200,
                "message": "Assessment retrieved successfully.",
                "data": formatted
            }

        except PyMongoError as db_err:
            logger.error(f"Database error in get_assessment_by_id: {str(db_err)}")
            return {"success": False, "status_code": 500, "message": "Database query error.", "error": "DATABASE_ERROR"}
        except Exception as err:
            logger.critical(f"Unexpected error in get_assessment_by_id: {str(err)}", exc_info=True)
            return {"success": False, "status_code": 500, "message": "Internal server error.", "error": "INTERNAL_SERVER_ERROR"}

    @classmethod
    def get_user_assessments(cls, user_id: str, status: Optional[str] = None, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """
        Retrieves paginated list of assessments assigned to or created by a user.

        Args:
            user_id (str): User ObjectId.
            status (Optional[str]): Filter by status ('Pending', 'Completed', etc.).
            page (int): 1-indexed page number.
            limit (int): Items per page.

        Returns:
            Dict[str, Any]: Standardized API response with paginated items.
        """
        try:
            if not ObjectId.is_valid(user_id):
                return {"success": False, "status_code": 400, "message": "Invalid user ID.", "error": "INVALID_OBJECT_ID"}

            page = max(1, int(page))
            limit = min(100, max(1, int(limit)))
            skip = (page - 1) * limit

            query: Dict[str, Any] = {"userId": ObjectId(user_id), "isActive": True}
            if status and status.strip().title() in VALID_STATUSES:
                query["status"] = status.strip().title()

            db = Database.get_db()
            total_count = db.assessments.count_documents(query)
            cursor = db.assessments.find(query).sort("createdAt", -1).skip(skip).limit(limit)

            items = [Assessment.response(doc) for doc in cursor]
            total_pages = (total_count + limit - 1) // limit if total_count > 0 else 0

            return {
                "success": True,
                "status_code": 200,
                "message": f"Retrieved {len(items)} assessments for user.",
                "data": items,
                "meta": {
                    "total_items": total_count,
                    "current_page": page,
                    "items_per_page": limit,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_previous": page > 1
                }
            }

        except PyMongoError as db_err:
            logger.error(f"Database error in get_user_assessments: {str(db_err)}")
            return {"success": False, "status_code": 500, "message": "Database query error.", "error": "DATABASE_ERROR"}
        except Exception as err:
            logger.critical(f"Unexpected error in get_user_assessments: {str(err)}", exc_info=True)
            return {"success": False, "status_code": 500, "message": "Internal server error.", "error": "INTERNAL_SERVER_ERROR"}

    @classmethod
    def delete_assessment(cls, assessment_id: str, soft_delete: bool = True) -> Dict[str, Any]:
        """
        Deletes or deactivates an assessment.

        Args:
            assessment_id (str): Assessment ObjectId.
            soft_delete (bool): If True, sets isActive=False instead of removing document.

        Returns:
            Dict[str, Any]: Standardized API response.
        """
        try:
            if not ObjectId.is_valid(assessment_id):
                return {"success": False, "status_code": 400, "message": "Invalid assessment ID.", "error": "INVALID_OBJECT_ID"}

            db = Database.get_db()
            if soft_delete:
                res = db.assessments.update_one(
                    {"_id": ObjectId(assessment_id)},
                    {"$set": {"isActive": False, "updatedAt": datetime.utcnow()}}
                )
                modified = res.matched_count > 0
            else:
                res = db.assessments.delete_one({"_id": ObjectId(assessment_id)})
                modified = res.deleted_count > 0

            if not modified:
                return {"success": False, "status_code": 404, "message": "Assessment not found.", "error": "ASSESSMENT_NOT_FOUND"}

            logger.info(f"{'Soft' if soft_delete else 'Hard'} deleted assessment {assessment_id}")
            return {
                "success": True,
                "status_code": 200,
                "message": "Assessment deleted successfully."
            }

        except PyMongoError as db_err:
            logger.error(f"Database error deleting assessment: {str(db_err)}")
            return {"success": False, "status_code": 500, "message": "Database deletion error.", "error": "DATABASE_ERROR"}
        except Exception as err:
            logger.critical(f"Unexpected error in delete_assessment: {str(err)}", exc_info=True)
            return {"success": False, "status_code": 500, "message": "Internal server error.", "error": "INTERNAL_SERVER_ERROR"}
