"""
Result Controller
Handles saving, retrieving, updating, and evaluating assessment results and leaderboards.
"""

from bson import ObjectId
from typing import Optional

try:
    from config.database import Database
except ImportError:
    from app.config.database import Database

try:
    from models.assessment_result_model import AssessmentResult
except ImportError:
    from app.models.assessment_result_model import AssessmentResult


class ResultController:
    """Assessment Result Controller"""

    @staticmethod
    def save_result(data: dict) -> tuple[dict, int]:
        try:
            db = Database.get_db()

            if not data:
                return {
                    "success": False,
                    "message": "No result data provided."
                }, 400

            assessment_id = data.get("assessmentId", data.get("assessment_id"))
            user_id = data.get("userId", data.get("user_id"))

            if not assessment_id or not user_id:
                return {
                    "success": False,
                    "message": "assessmentId and userId are required."
                }, 400

            aptitude_answers = data.get("aptitudeAnswers", data.get("aptitude_answers", []))
            technical_answers = data.get("technicalAnswers", data.get("technical_answers", []))
            coding_submissions = data.get("codingSubmissions", data.get("coding_submissions", []))

            aptitude_score = data.get("aptitudeScore", data.get("aptitude_score", 0))
            technical_score = data.get("technicalScore", data.get("technical_score", 0))
            coding_score = data.get("codingScore", data.get("coding_score", 0))
            total_score = data.get("totalScore", data.get("total_score", aptitude_score + technical_score + coding_score))
            percentage = data.get("percentage", 0.0)
            rank = data.get("rank")

            total_questions = data.get("totalQuestions", data.get("total_questions", 0))
            correct_answers = data.get("correctAnswers", data.get("correct_answers", 0))
            wrong_answers = data.get("wrongAnswers", data.get("wrong_answers", 0))
            unanswered_questions = data.get("unansweredQuestions", data.get("unanswered_questions", 0))
            total_time = data.get("totalTime", data.get("total_time", 0))

            strongest_skill = data.get("strongestSkill", data.get("strongest_skill", ""))
            weakest_skill = data.get("weakestSkill", data.get("weakest_skill", ""))
            recommendation = data.get("recommendation", "")
            status = data.get("status", "Completed")

            result_doc = AssessmentResult.create_result(
                assessment_id=assessment_id,
                user_id=user_id,
                aptitude_answers=aptitude_answers,
                technical_answers=technical_answers,
                coding_submissions=coding_submissions,
                aptitude_score=aptitude_score,
                technical_score=technical_score,
                coding_score=coding_score,
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
                recommendation=recommendation,
                status=status
            )

            res = db.assessment_results.insert_one(result_doc)

            # Update assessment status if needed
            try:
                db.assessments.update_one(
                    {"_id": ObjectId(assessment_id)},
                    {"$set": {"status": "Completed"}}
                )
            except Exception:
                pass

            return {
                "success": True,
                "message": "Assessment result saved successfully.",
                "result_id": str(res.inserted_id)
            }, 201

        except Exception as error:
            return {
                "success": False,
                "message": str(error)
            }, 500

    @staticmethod
    def create_result(data: dict) -> tuple[dict, int]:
        """Alias for save_result to support multiple route conventions."""
        return ResultController.save_result(data)

    @staticmethod
    def get_results(
        user_id: Optional[str] = None,
        assessment_id: Optional[str] = None,
    ) -> tuple[dict, int]:
        try:
            db = Database.get_db()

            query = {}
            if user_id:
                try:
                    query["$or"] = [{"userId": ObjectId(user_id)}, {"userId": str(user_id)}, {"user_id": str(user_id)}]
                except Exception:
                    query["userId"] = str(user_id)
            if assessment_id:
                try:
                    query["$or"] = [{"assessmentId": ObjectId(assessment_id)}, {"assessmentId": str(assessment_id)}, {"assessment_id": str(assessment_id)}]
                except Exception:
                    query["assessmentId"] = str(assessment_id)

            results = list(db.assessment_results.find(query).sort("createdAt", -1))

            formatted_results = []
            for res in results:
                try:
                    formatted = AssessmentResult.response(res)
                except Exception:
                    res["_id"] = str(res.get("_id", ""))
                    if "assessmentId" in res and res["assessmentId"]:
                        res["assessmentId"] = str(res["assessmentId"])
                    if "userId" in res and res["userId"]:
                        res["userId"] = str(res["userId"])
                    formatted = res
                formatted_results.append(formatted)

            return {
                "success": True,
                "count": len(formatted_results),
                "data": formatted_results
            }, 200

        except Exception as error:
            return {
                "success": False,
                "message": str(error)
            }, 500

    @staticmethod
    def get_result(result_id: str) -> tuple[dict, int]:
        try:
            db = Database.get_db()

            result = db.assessment_results.find_one({
                "_id": ObjectId(result_id)
            })

            if not result:
                return {
                    "success": False,
                    "message": "Assessment result not found."
                }, 404

            try:
                formatted = AssessmentResult.response(result)
            except Exception:
                result["_id"] = str(result.get("_id", ""))
                if "assessmentId" in result and result["assessmentId"]:
                    result["assessmentId"] = str(result["assessmentId"])
                if "userId" in result and result["userId"]:
                    result["userId"] = str(result["userId"])
                formatted = result

            return {
                "success": True,
                "data": formatted
            }, 200

        except Exception as error:
            return {
                "success": False,
                "message": str(error)
            }, 500

    @staticmethod
    def get_user_results(user_id: str) -> tuple[dict, int]:
        try:
            db = Database.get_db()

            try:
                user_query = {"$or": [{"userId": ObjectId(user_id)}, {"userId": str(user_id)}, {"user_id": str(user_id)}]}
            except Exception:
                user_query = {"$or": [{"userId": str(user_id)}, {"user_id": str(user_id)}]}

            results = list(db.assessment_results.find(user_query).sort("createdAt", -1))

            formatted_results = []
            for res in results:
                try:
                    formatted = AssessmentResult.response(res)
                except Exception:
                    res["_id"] = str(res.get("_id", ""))
                    if "assessmentId" in res and res["assessmentId"]:
                        res["assessmentId"] = str(res["assessmentId"])
                    if "userId" in res and res["userId"]:
                        res["userId"] = str(res["userId"])
                    formatted = res
                formatted_results.append(formatted)

            return {
                "success": True,
                "count": len(formatted_results),
                "data": formatted_results
            }, 200

        except Exception as error:
            return {
                "success": False,
                "message": str(error)
            }, 500

    @staticmethod
    def get_assessment_results(assessment_id: str) -> tuple[dict, int]:
        try:
            db = Database.get_db()

            try:
                assessment_query = {"$or": [{"assessmentId": ObjectId(assessment_id)}, {"assessmentId": str(assessment_id)}, {"assessment_id": str(assessment_id)}]}
            except Exception:
                assessment_query = {"$or": [{"assessmentId": str(assessment_id)}, {"assessment_id": str(assessment_id)}]}

            results = list(db.assessment_results.find(assessment_query).sort("totalScore", -1))

            formatted_results = []
            for res in results:
                try:
                    formatted = AssessmentResult.response(res)
                except Exception:
                    res["_id"] = str(res.get("_id", ""))
                    if "assessmentId" in res and res["assessmentId"]:
                        res["assessmentId"] = str(res["assessmentId"])
                    if "userId" in res and res["userId"]:
                        res["userId"] = str(res["userId"])
                    formatted = res
                formatted_results.append(formatted)

            return {
                "success": True,
                "count": len(formatted_results),
                "data": formatted_results
            }, 200

        except Exception as error:
            return {
                "success": False,
                "message": str(error)
            }, 500

    @staticmethod
    def update_result(result_id: str, data: dict) -> tuple[dict, int]:
        try:
            db = Database.get_db()

            if not data:
                return {
                    "success": False,
                    "message": "No update data provided."
                }, 400

            update_fields = dict(data)
            update_fields.pop("_id", None)
            update_fields.pop("id", None)

            result = db.assessment_results.update_one(
                {"_id": ObjectId(result_id)},
                {"$set": update_fields}
            )

            if result.matched_count == 0:
                return {
                    "success": False,
                    "message": "Assessment result not found."
                }, 404

            return {
                "success": True,
                "message": "Assessment result updated successfully."
            }, 200

        except Exception as error:
            return {
                "success": False,
                "message": str(error)
            }, 500

    @staticmethod
    def delete_result(result_id: str) -> tuple[dict, int]:
        try:
            db = Database.get_db()

            result = db.assessment_results.delete_one({
                "_id": ObjectId(result_id)
            })

            if result.deleted_count == 0:
                return {
                    "success": False,
                    "message": "Assessment result not found."
                }, 404

            return {
                "success": True,
                "message": "Assessment result deleted successfully."
            }, 200

        except Exception as error:
            return {
                "success": False,
                "message": str(error)
            }, 500

    @staticmethod
    def get_leaderboard(assessment_id: Optional[str] = None, limit: int = 10) -> tuple[dict, int]:
        try:
            db = Database.get_db()

            query = {}
            if assessment_id:
                try:
                    query["$or"] = [{"assessmentId": ObjectId(assessment_id)}, {"assessmentId": str(assessment_id)}, {"assessment_id": str(assessment_id)}]
                except Exception:
                    query["assessmentId"] = str(assessment_id)

            results = list(db.assessment_results.find(query).sort([("totalScore", -1), ("percentage", -1), ("totalTime", 1)]).limit(limit))

            leaderboard = []
            for rank, res in enumerate(results, 1):
                user_name = "Anonymous"
                user_id_str = str(res.get("userId", res.get("user_id", "")))
                try:
                    if user_id_str:
                        user = db.users.find_one({"_id": ObjectId(user_id_str)})
                        if user:
                            user_name = user.get("fullName", user.get("name", "Anonymous"))
                except Exception:
                    pass

                leaderboard.append({
                    "rank": rank,
                    "result_id": str(res.get("_id", "")),
                    "user_id": user_id_str,
                    "user_name": user_name,
                    "total_score": res.get("totalScore", res.get("total_score", 0)),
                    "percentage": res.get("percentage", 0.0),
                    "total_time": res.get("totalTime", res.get("total_time", 0)),
                    "submitted_at": res.get("createdAt", res.get("submittedAt", res.get("submitted_at", "")))
                })

            return {
                "success": True,
                "count": len(leaderboard),
                "data": leaderboard
            }, 200

        except Exception as error:
            return {
                "success": False,
                "message": str(error)
            }, 500

    # Alias methods matching route names
    @staticmethod
    def calculate_result(data: dict) -> tuple[dict, int]:
        return ResultController.save_result(data)

    @staticmethod
    def get_all_results(user_id: Optional[str] = None, assessment_id: Optional[str] = None) -> tuple[dict, int]:
        return ResultController.get_results(user_id=user_id, assessment_id=assessment_id)

    @staticmethod
    def get_result_by_id(result_id: str) -> tuple[dict, int]:
        return ResultController.get_result(result_id)

    @staticmethod
    def get_candidate_results(user_id: str) -> tuple[dict, int]:
        return ResultController.get_user_results(user_id)

    @staticmethod
    def get_assessment_result(assessment_id: str) -> tuple[dict, int]:
        return ResultController.get_assessment_results(assessment_id)
