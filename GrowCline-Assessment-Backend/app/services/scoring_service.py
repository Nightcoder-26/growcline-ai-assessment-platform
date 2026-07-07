"""
Scoring Service Module
Responsible for:
- Calculating aptitude, technical, and coding scores
- Calculating total score, percentage, and Pass/Fail determination
- Rank calculation among assessment participants
- Category-wise skill profiling (strongest and weakest areas)
- Storing final evaluation reports in the assessment_results collection

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
    from models.assessment_result_model import AssessmentResult
    from services.coding_service import CodingService
except ImportError:
    from app.models.assessment_result_model import AssessmentResult
    from app.services.coding_service import CodingService

logger = logging.getLogger(__name__)

# Constants for Evaluation Status
STATUS_PASSED = "Passed"
STATUS_FAILED = "Failed"
STATUS_COMPLETED = "Completed"


class ScoringService:
    """
    Service class responsible for automated grading, statistical ranking,
    and comprehensive result storage. Designed for high throughput using batch MongoDB querying.
    """

    @classmethod
    def _batch_evaluate_mcq_section(
        cls,
        collection: Any,
        submitted_answers: List[Dict[str, Any]],
        expected_question_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Helper method to evaluate MCQ answers in batch without N+1 database queries.

        Args:
            collection (Any): MongoDB collection (aptitude_questions or technical_questions).
            submitted_answers (List[Dict[str, Any]]): User's submitted answers.
            expected_question_ids (Optional[List[str]]): List of question IDs assigned to this assessment section.

        Returns:
            Dict[str, Any]: Aggregated section score, counts, category breakdown, and detailed answer logs.
        """
        # Map submitted answers by question ID
        answer_map: Dict[str, str] = {}
        for ans in submitted_answers:
            qid = str(ans.get("questionId") or ans.get("question_id") or "")
            selected = ans.get("selectedOption") or ans.get("selected_option") or ans.get("answer")
            if qid and ObjectId.is_valid(qid) and selected is not None:
                answer_map[qid] = str(selected)

        # Determine target question IDs to query
        target_ids_str = expected_question_ids if expected_question_ids is not None else list(answer_map.keys())
        valid_ids = [ObjectId(qid) for qid in target_ids_str if ObjectId.is_valid(qid)]

        if not valid_ids:
            return {
                "score": 0.0,
                "max_marks": 0.0,
                "correct_count": 0,
                "wrong_count": 0,
                "unanswered_count": 0,
                "total_questions": 0,
                "category_breakdown": {},
                "detailed_results": []
            }

        # Batch query all questions in one network call
        cursor = collection.find({"_id": {"$in": valid_ids}})
        questions_doc_map = {str(doc["_id"]): doc for doc in cursor}

        total_score = 0.0
        total_max_marks = 0.0
        correct_count = 0
        wrong_count = 0
        unanswered_count = 0
        category_breakdown: Dict[str, Dict[str, float]] = {}
        detailed_results = []

        for qid_str in target_ids_str:
            q_doc = questions_doc_map.get(qid_str)
            if not q_doc:
                continue

            q_marks = float(q_doc.get("marks", 1.0))
            total_max_marks += q_marks
            correct_val = str(q_doc.get("correctAnswer") or q_doc.get("correct_answer") or "").strip()
            category = str(q_doc.get("category") or q_doc.get("technology") or "General").strip()

            if category not in category_breakdown:
                category_breakdown[category] = {"obtained": 0.0, "total": 0.0, "correct": 0, "questions": 0}

            category_breakdown[category]["total"] += q_marks
            category_breakdown[category]["questions"] += 1

            selected_val = answer_map.get(qid_str)
            is_correct = False
            marks_obtained = 0.0

            if selected_val is None or selected_val.strip() == "":
                unanswered_count += 1
            else:
                if selected_val.strip().lower() == correct_val.lower():
                    is_correct = True
                    marks_obtained = q_marks
                    total_score += q_marks
                    correct_count += 1
                    category_breakdown[category]["obtained"] += q_marks
                    category_breakdown[category]["correct"] += 1
                else:
                    wrong_count += 1

            detailed_results.append({
                "question_id": qid_str,
                "question_text": q_doc.get("question", ""),
                "selected_option": selected_val,
                "correct_answer": correct_val,
                "is_correct": is_correct,
                "marks_obtained": marks_obtained,
                "max_marks": q_marks,
                "category": category
            })

        return {
            "score": round(total_score, 2),
            "max_marks": round(total_max_marks, 2),
            "correct_count": correct_count,
            "wrong_count": wrong_count,
            "unanswered_count": unanswered_count,
            "total_questions": len(target_ids_str),
            "category_breakdown": category_breakdown,
            "detailed_results": detailed_results
        }

    @classmethod
    def calculate_aptitude_score(
        cls,
        answers: List[Dict[str, Any]],
        expected_question_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Calculates score for aptitude assessment section.

        Args:
            answers (List[Dict[str, Any]]): Submitted answers.
            expected_question_ids (Optional[List[str]]): Assessment assigned aptitude question IDs.

        Returns:
            Dict[str, Any]: Section scoring metrics.
        """
        db = Database.get_db()
        return cls._batch_evaluate_mcq_section(db.aptitude_questions, answers, expected_question_ids)

    @classmethod
    def calculate_technical_score(
        cls,
        answers: List[Dict[str, Any]],
        expected_question_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Calculates score for technical assessment section.

        Args:
            answers (List[Dict[str, Any]]): Submitted answers.
            expected_question_ids (Optional[List[str]]): Assessment assigned technical question IDs.

        Returns:
            Dict[str, Any]: Section scoring metrics.
        """
        db = Database.get_db()
        return cls._batch_evaluate_mcq_section(db.technical_questions, answers, expected_question_ids)

    @classmethod
    def calculate_coding_score(
        cls,
        submissions: List[Dict[str, Any]],
        user_id: str,
        expected_question_ids: Optional[List[str]] = None,
        engine_type: str = "local"
    ) -> Dict[str, Any]:
        """
        Evaluates coding submissions by delegating to CodingService.

        Args:
            submissions (List[Dict[str, Any]]): User's submitted code payloads.
            user_id (str): ID of the student/candidate.
            expected_question_ids (Optional[List[str]]): Assessment assigned coding question IDs.
            engine_type (str): Sandbox engine type ('local', 'docker').

        Returns:
            Dict[str, Any]: Coding section metrics and test case logs.
        """
        sub_map: Dict[str, Dict[str, Any]] = {}
        for sub in submissions:
            qid = str(sub.get("questionId") or sub.get("question_id") or "")
            if qid and ObjectId.is_valid(qid):
                sub_map[qid] = sub

        target_ids_str = expected_question_ids if expected_question_ids is not None else list(sub_map.keys())
        total_score = 0.0
        total_max_marks = 0.0
        correct_count = 0
        wrong_count = 0
        unanswered_count = 0
        category_breakdown: Dict[str, Dict[str, float]] = {}
        detailed_results = []

        db = Database.get_db()
        valid_ids = [ObjectId(qid) for qid in target_ids_str if ObjectId.is_valid(qid)]
        cursor = db.coding_questions.find({"_id": {"$in": valid_ids}})
        questions_doc_map = {str(doc["_id"]): doc for doc in cursor}

        for qid_str in target_ids_str:
            q_doc = questions_doc_map.get(qid_str)
            if not q_doc:
                continue

            q_marks = float(q_doc.get("marks", 10.0))
            total_max_marks += q_marks
            category = str(q_doc.get("category") or "Algorithms").strip()

            if category not in category_breakdown:
                category_breakdown[category] = {"obtained": 0.0, "total": 0.0, "correct": 0, "questions": 0}

            category_breakdown[category]["total"] += q_marks
            category_breakdown[category]["questions"] += 1

            sub_data = sub_map.get(qid_str)
            if not sub_data or not sub_data.get("code"):
                unanswered_count += 1
                detailed_results.append({
                    "question_id": qid_str,
                    "status": "Unanswered",
                    "marks_obtained": 0.0,
                    "max_marks": q_marks,
                    "passed_tests": 0,
                    "total_tests": 0
                })
                continue

            # Execute evaluation engine via CodingService
            sub_payload = {
                "questionId": qid_str,
                "code": sub_data.get("code", ""),
                "programmingLanguage": sub_data.get("programmingLanguage") or sub_data.get("language", "python"),
                "userId": user_id
            }

            eval_report = CodingService.evaluate_submission(sub_payload, engine_type=engine_type)
            if eval_report.get("success") and eval_report.get("data"):
                res_data = eval_report["data"]
                obtained = float(res_data.get("marks_obtained", 0.0))
                status = res_data.get("status", "Runtime Error")
                passed_tests = res_data.get("passed_tests", 0)
                total_tests = res_data.get("total_tests", 0)

                total_score += obtained
                category_breakdown[category]["obtained"] += obtained

                if status == "Accepted" or (total_tests > 0 and passed_tests == total_tests):
                    correct_count += 1
                    category_breakdown[category]["correct"] += 1
                else:
                    wrong_count += 1

                detailed_results.append({
                    "question_id": qid_str,
                    "status": status,
                    "marks_obtained": obtained,
                    "max_marks": q_marks,
                    "passed_tests": passed_tests,
                    "total_tests": total_tests,
                    "test_results": res_data.get("test_results", [])
                })
            else:
                wrong_count += 1
                detailed_results.append({
                    "question_id": qid_str,
                    "status": "Execution Error",
                    "marks_obtained": 0.0,
                    "max_marks": q_marks,
                    "error": eval_report.get("message", "Evaluation failed.")
                })

        return {
            "score": round(total_score, 2),
            "max_marks": round(total_max_marks, 2),
            "correct_count": correct_count,
            "wrong_count": wrong_count,
            "unanswered_count": unanswered_count,
            "total_questions": len(target_ids_str),
            "category_breakdown": category_breakdown,
            "detailed_results": detailed_results
        }

    @classmethod
    def calculate_category_wise_score(
        cls,
        *category_maps: Dict[str, Dict[str, float]]
    ) -> Tuple[Dict[str, Dict[str, Any]], str, str]:
        """
        Aggregates category scores across sections to determine overall profile, strongest skill, and weakest skill.

        Args:
            *category_maps: Variable number of section category breakdown dictionaries.

        Returns:
            Tuple[Dict[str, Dict[str, Any]], str, str]: (Combined Category Profiler, Strongest Skill, Weakest Skill)
        """
        merged: Dict[str, Dict[str, float]] = {}

        for cat_map in category_maps:
            for cat_name, stats in cat_map.items():
                if cat_name not in merged:
                    merged[cat_name] = {"obtained": 0.0, "total": 0.0, "correct": 0, "questions": 0}
                merged[cat_name]["obtained"] += stats.get("obtained", 0.0)
                merged[cat_name]["total"] += stats.get("total", 0.0)
                merged[cat_name]["correct"] += stats.get("correct", 0)
                merged[cat_name]["questions"] += stats.get("questions", 0)

        strongest_skill = "General"
        weakest_skill = "General"
        max_pct = -1.0
        min_pct = 101.0

        formatted_profile: Dict[str, Dict[str, Any]] = {}
        for cat_name, stats in merged.items():
            tot = stats["total"]
            obt = stats["obtained"]
            pct = round((obt / tot) * 100, 2) if tot > 0 else 0.0

            formatted_profile[cat_name] = {
                "marks_obtained": round(obt, 2),
                "total_marks": round(tot, 2),
                "percentage": pct,
                "questions_count": int(stats["questions"]),
                "correct_count": int(stats["correct"])
            }

            if tot > 0:
                if pct > max_pct:
                    max_pct = pct
                    strongest_skill = cat_name
                if pct < min_pct:
                    min_pct = pct
                    weakest_skill = cat_name

        if not formatted_profile:
            strongest_skill = "None"
            weakest_skill = "None"

        return formatted_profile, strongest_skill, weakest_skill

    @classmethod
    def calculate_rank(cls, assessment_id: str, total_score: float) -> int:
        """
        Calculates user's rank for a specific assessment by counting peers with higher scores.
        Scales cleanly with indexed query on (assessmentId, totalScore).

        Args:
            assessment_id (str): Assessment ObjectId string.
            total_score (float): Candidate's total score.

        Returns:
            int: 1-indexed statistical rank.
        """
        try:
            db = Database.get_db()
            if not ObjectId.is_valid(assessment_id):
                return 1

            higher_scores_count = db.assessment_results.count_documents({
                "assessmentId": ObjectId(assessment_id),
                "totalScore": {"$gt": total_score}
            })

            return higher_scores_count + 1
        except PyMongoError as e:
            logger.error(f"Error computing rank: {str(e)}")
            return 1

    @classmethod
    def calculate_and_save_result(
        cls,
        assessment_id: str,
        user_id: str,
        submission_payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Orchestrates end-to-end evaluation of an assessment submission.
        Grades all sections, determines Pass/Fail status, computes ranks,
        saves to assessment_results collection, and triggers analytics/recommendations.

        Args:
            assessment_id (str): Assessment ObjectId.
            user_id (str): User ObjectId.
            submission_payload (Dict[str, Any]): Payload with submitted answers and timing.

        Returns:
            Dict[str, Any]: Standardized API response containing complete evaluation report.
        """
        try:
            if not ObjectId.is_valid(assessment_id) or not ObjectId.is_valid(user_id):
                return {
                    "success": False,
                    "status_code": 400,
                    "message": "Invalid assessment ID or user ID format.",
                    "error": "INVALID_OBJECT_ID"
                }

            db = Database.get_db()
            assessment_doc = db.assessments.find_one({"_id": ObjectId(assessment_id)})
            if not assessment_doc:
                return {
                    "success": False,
                    "status_code": 404,
                    "message": "Assessment not found.",
                    "error": "ASSESSMENT_NOT_FOUND"
                }

            # Extract expected question IDs from assessment document
            exp_aptitude = [str(qid) for qid in assessment_doc.get("aptitudeQuestions", [])]
            exp_technical = [str(qid) for qid in assessment_doc.get("technicalQuestions", [])]
            exp_coding = [str(qid) for qid in assessment_doc.get("codingQuestions", [])]

            # Grade individual sections
            aptitude_ans = submission_payload.get("aptitudeAnswers") or submission_payload.get("aptitude_answers", [])
            technical_ans = submission_payload.get("technicalAnswers") or submission_payload.get("technical_answers", [])
            coding_subs = submission_payload.get("codingSubmissions") or submission_payload.get("coding_submissions", [])
            engine_type = submission_payload.get("engineType", "local")

            aptitude_eval = cls.calculate_aptitude_score(aptitude_ans, exp_aptitude if exp_aptitude else None)
            technical_eval = cls.calculate_technical_score(technical_ans, exp_technical if exp_technical else None)
            coding_eval = cls.calculate_coding_score(coding_subs, user_id, exp_coding if exp_coding else None, engine_type=engine_type)

            # Aggregate scores and counts
            apt_score = aptitude_eval["score"]
            tech_score = technical_eval["score"]
            cod_score = coding_eval["score"]
            total_score = round(apt_score + tech_score + cod_score, 2)

            total_max_marks = float(assessment_doc.get("totalMarks") or (aptitude_eval["max_marks"] + technical_eval["max_marks"] + coding_eval["max_marks"]))
            percentage = round((total_score / total_max_marks) * 100, 2) if total_max_marks > 0 else 0.0

            passing_pct = float(assessment_doc.get("passingPercentage", 40.0))
            pass_status = STATUS_PASSED if percentage >= passing_pct else STATUS_FAILED

            total_questions = aptitude_eval["total_questions"] + technical_eval["total_questions"] + coding_eval["total_questions"]
            correct_answers = aptitude_eval["correct_count"] + technical_eval["correct_count"] + coding_eval["correct_count"]
            wrong_answers = aptitude_eval["wrong_count"] + technical_eval["wrong_count"] + coding_eval["wrong_count"]
            unanswered_questions = aptitude_eval["unanswered_count"] + technical_eval["unanswered_count"] + coding_eval["unanswered_count"]
            total_time = int(submission_payload.get("totalTimeSpent") or submission_payload.get("total_time") or 0)

            # Profile categories and skills
            cat_profile, strongest_skill, weakest_skill = cls.calculate_category_wise_score(
                aptitude_eval["category_breakdown"],
                technical_eval["category_breakdown"],
                coding_eval["category_breakdown"]
            )

            # Calculate rank
            rank = cls.calculate_rank(assessment_id, total_score)

            # Generate initial recommendation summary
            recommendation_text = f"Focus on improving {weakest_skill} to boost overall score." if weakest_skill != "None" and pass_status == STATUS_FAILED else "Great performance across key competencies!"

            # Build result document using model factory
            result_doc = AssessmentResult.create_result(
                assessment_id=assessment_id,
                user_id=user_id,
                aptitude_answers=aptitude_eval["detailed_results"],
                technical_answers=technical_eval["detailed_results"],
                coding_submissions=coding_eval["detailed_results"],
                aptitude_score=apt_score,
                technical_score=tech_score,
                coding_score=cod_score,
                total_score=total_score,
                percentage=percentage,
                rank=rank,
                total_questions=total_questions,
                correct_answers=correct_answers,
                wrong_answers=wrong_answers,
                unanswered_questions=unanswered_questions,
                total_time=total_time,
                strongest_skill=strongest_skill,
                weakest_skill=weakest_skill,
                recommendation=recommendation_text,
                status=pass_status
            )

            # Attach category breakdown to result doc for analytics
            result_doc["categoryProfile"] = cat_profile

            # Save to assessment_results collection
            res_insert = db.assessment_results.insert_one(result_doc)
            result_id = str(res_insert.inserted_id)
            logger.info(f"Saved assessment result ID {result_id} for user {user_id} on assessment {assessment_id}")

            # Update assessment status to completed/submitted
            db.assessments.update_one(
                {"_id": ObjectId(assessment_id)},
                {"$set": {"status": STATUS_COMPLETED, "submittedAt": datetime.utcnow(), "updatedAt": datetime.utcnow()}}
            )

            # Asynchronously trigger Analytics and Recommendation modules
            try:
                try:
                    from services.analytics_service import AnalyticsService
                    from services.recommendation_service import RecommendationService
                except ImportError:
                    from app.services.analytics_service import AnalyticsService
                    from app.services.recommendation_service import RecommendationService

                AnalyticsService.record_assessment_analytics(user_id, assessment_id, result_doc)
                RecommendationService.generate_recommendations_for_user(user_id, weak_skills=[weakest_skill] if weakest_skill != "None" else [])
            except Exception as trigger_err:
                logger.warning(f"Non-fatal error triggering analytics/recommendations: {str(trigger_err)}")

            formatted_res = AssessmentResult.response(result_doc)
            formatted_res["categoryProfile"] = cat_profile
            formatted_res["passStatus"] = pass_status

            return {
                "success": True,
                "status_code": 201,
                "message": f"Assessment evaluated successfully: {pass_status} ({percentage}%).",
                "data": formatted_res
            }

        except PyMongoError as db_err:
            logger.error(f"Database error saving result: {str(db_err)}")
            return {"success": False, "status_code": 500, "message": "Database error saving results.", "error": "DATABASE_ERROR"}
        except Exception as err:
            logger.critical(f"Unexpected error in calculate_and_save_result: {str(err)}", exc_info=True)
            return {"success": False, "status_code": 500, "message": "Internal server error.", "error": "INTERNAL_SERVER_ERROR"}
