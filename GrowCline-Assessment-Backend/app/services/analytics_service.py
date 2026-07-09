"""
Analytics Service Module
Responsible for:
- Generating comprehensive user and platform dashboards
- Calculating statistical metrics: Average, Highest, Lowest scores
- Identifying historical Strongest and Weakest skills
- Tracking progress trends over time
- Computing improvement percentages
- Storing and indexing data in the analytics collection

Architecture: Controller -> Service -> Model -> MongoDB
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from bson import ObjectId
from pymongo.errors import PyMongoError

try:
    from config.database import Database
except ImportError:
    from app.config.database import Database

try:
    from models.analytics_model import Analytics
except ImportError:
    from app.models.analytics_model import Analytics

logger = logging.getLogger(__name__)


class AnalyticsService:
    """
    Service class responsible for tracking student performance analytics,
    calculating long-term growth trajectories, and serving scalable aggregation dashboards.
    """

    @classmethod
    def record_assessment_analytics(
        cls,
        user_id: str,
        assessment_id: str,
        result_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Records analytical snapshot into the 'analytics' collection after assessment scoring.

        Args:
            user_id (str): User ObjectId string.
            assessment_id (str): Assessment ObjectId string.
            result_data (Dict[str, Any]): Scored result attributes.

        Returns:
            Dict[str, Any]: Standardized API response.
        """
        try:
            if not ObjectId.is_valid(user_id) or not ObjectId.is_valid(assessment_id):
                return {"success": False, "status_code": 400, "message": "Invalid IDs.", "error": "INVALID_OBJECT_ID"}

            db = Database.get_db()

            analytics_doc = Analytics.create_analytics(
                user_id=user_id,
                assessment_id=assessment_id,
                aptitude_score=float(result_data.get("aptitudeScore", 0.0)),
                technical_score=float(result_data.get("technicalScore", 0.0)),
                coding_score=float(result_data.get("codingScore", 0.0)),
                total_score=float(result_data.get("totalScore", 0.0)),
                percentage=float(result_data.get("percentage", 0.0)),
                rank=result_data.get("rank"),
                strongest_skill=str(result_data.get("strongestSkill", "")),
                weakest_skill=str(result_data.get("weakestSkill", "")),
                recommendation=str(result_data.get("recommendation", "")),
                total_questions=int(result_data.get("totalQuestions", 0)),
                correct_answers=int(result_data.get("correctAnswers", 0)),
                wrong_answers=int(result_data.get("wrongAnswers", 0)),
                unanswered_questions=int(result_data.get("unansweredQuestions", 0)),
                total_time=int(result_data.get("totalTime", 0))
            )

            res = db.analytics.insert_one(analytics_doc)
            logger.info(f"Recorded analytical entry ID {res.inserted_id} for user {user_id}")

            return {
                "success": True,
                "status_code": 201,
                "message": "Analytics entry recorded successfully.",
                "data": Analytics.analytics_response(analytics_doc)
            }

        except PyMongoError as db_err:
            logger.error(f"MongoDB error in record_assessment_analytics: {str(db_err)}")
            return {"success": False, "status_code": 500, "message": "Database error saving analytics.", "error": "DATABASE_ERROR"}
        except Exception as err:
            logger.critical(f"Unexpected error recording analytics: {str(err)}", exc_info=True)
            return {"success": False, "status_code": 500, "message": "Internal server error.", "error": "INTERNAL_SERVER_ERROR"}

    @classmethod
    def _compute_improvement_percentage(cls, sorted_records: List[Dict[str, Any]]) -> float:
        """
        Calculates user improvement percentage between early attempts and recent attempts.

        Args:
            sorted_records (List[Dict[str, Any]]): Chronologically ordered analytics records.

        Returns:
            float: Percentage improvement (positive or negative).
        """
        count = len(sorted_records)
        if count <= 1:
            return 0.0

        # Compare baseline (first attempt) against latest attempt
        first_score = float(sorted_records[0].get("percentage") or sorted_records[0].get("totalScore", 0.0))
        latest_score = float(sorted_records[-1].get("percentage") or sorted_records[-1].get("totalScore", 0.0))

        if first_score == 0.0:
            return 100.0 if latest_score > 0.0 else 0.0

        improvement = ((latest_score - first_score) / first_score) * 100.0
        return round(improvement, 2)

    @classmethod
    def _aggregate_historical_skills(cls, sorted_records: List[Dict[str, Any]]) -> Tuple[str, str, Dict[str, int]]:
        """
        Determines overall strongest and weakest skills across user's history using frequency aggregation.

        Args:
            sorted_records (List[Dict[str, Any]]): Analytics records.

        Returns:
            Tuple[str, str, Dict[str, int]]: (Strongest Skill, Weakest Skill, Skill Frequency Distribution)
        """
        skill_counts: Dict[str, int] = {}
        weak_counts: Dict[str, int] = {}

        for rec in sorted_records:
            strong = rec.get("strongestSkill")
            weak = rec.get("weakestSkill")
            if strong and strong != "None" and strong != "General":
                skill_counts[strong] = skill_counts.get(strong, 0) + 1
            if weak and weak != "None" and weak != "General":
                weak_counts[weak] = weak_counts.get(weak, 0) + 1

        overall_strong = max(skill_counts.items(), key=lambda x: x[1])[0] if skill_counts else (sorted_records[-1].get("strongestSkill", "N/A") if sorted_records else "N/A")
        overall_weak = max(weak_counts.items(), key=lambda x: x[1])[0] if weak_counts else (sorted_records[-1].get("weakestSkill", "N/A") if sorted_records else "N/A")

        return overall_strong, overall_weak, skill_counts

    @classmethod
    def generate_user_dashboard(cls, user_id: str) -> Dict[str, Any]:
        """
        Generates comprehensive analytical dashboard for a specific user.
        Calculates averages, extrema, progress trends, and improvement rates.

        Args:
            user_id (str): User ObjectId string.

        Returns:
            Dict[str, Any]: Standardized API response containing detailed dashboard metrics.
        """
        try:
            if not ObjectId.is_valid(user_id):
                return {"success": False, "status_code": 400, "message": "Invalid user ID.", "error": "INVALID_OBJECT_ID"}

            db = Database.get_db()
            cursor = db.analytics.find({"userId": ObjectId(user_id)}).sort("createdAt", 1)
            records = list(cursor)

            if not records:
                # Fallback check in assessment_results in case analytics collection was bypassed
                cursor_res = db.assessment_results.find({"userId": ObjectId(user_id)}).sort("createdAt", 1)
                records = list(cursor_res)

            total_assessments = len(records)
            if total_assessments == 0:
                return {
                    "success": True,
                    "status_code": 200,
                    "message": "User dashboard generated (no assessment history found).",
                    "data": {
                        "user_id": user_id,
                        "total_assessments": 0,
                        "average_score": 0.0,
                        "highest_score": 0.0,
                        "lowest_score": 0.0,
                        "strongest_skill": "N/A",
                        "weakest_skill": "N/A",
                        "improvement_percentage": 0.0,
                        "progress_trend": [],
                        "section_averages": {
                            "aptitude": 0.0,
                            "technical": 0.0,
                            "coding": 0.0
                        }
                    }
                }

            scores = [float(r.get("totalScore", 0.0)) for r in records]
            avg_score = round(sum(scores) / total_assessments, 2)
            highest_score = round(max(scores), 2)
            lowest_score = round(min(scores), 2)

            # Section-wise averages
            apt_scores = [float(r.get("aptitudeScore", 0.0)) for r in records]
            tech_scores = [float(r.get("technicalScore", 0.0)) for r in records]
            cod_scores = [float(r.get("codingScore", 0.0)) for r in records]

            section_averages = {
                "aptitude": round(sum(apt_scores) / total_assessments, 2),
                "technical": round(sum(tech_scores) / total_assessments, 2),
                "coding": round(sum(cod_scores) / total_assessments, 2)
            }

            # Progress trend time series
            progress_trend = []
            for idx, rec in enumerate(records):
                created_dt = rec.get("createdAt", datetime.utcnow())
                date_str = created_dt.strftime("%Y-%m-%d %H:%M") if isinstance(created_dt, datetime) else str(created_dt)
                progress_trend.append({
                    "attempt_number": idx + 1,
                    "date": date_str,
                    "total_score": float(rec.get("totalScore", 0.0)),
                    "percentage": float(rec.get("percentage", 0.0)),
                    "assessment_id": str(rec.get("assessmentId", "")),
                    "rank": rec.get("rank")
                })

            improvement_pct = cls._compute_improvement_percentage(records)
            strongest, weakest, skill_dist = cls._aggregate_historical_skills(records)

            dashboard_data = {
                "user_id": user_id,
                "total_assessments": total_assessments,
                "average_score": avg_score,
                "highest_score": highest_score,
                "lowest_score": lowest_score,
                "strongest_skill": strongest,
                "weakest_skill": weakest,
                "improvement_percentage": improvement_pct,
                "progress_trend": progress_trend,
                "section_averages": section_averages,
                "skill_distribution": skill_dist
            }

            return {
                "success": True,
                "status_code": 200,
                "message": "User analytics dashboard generated successfully.",
                "data": dashboard_data
            }

        except PyMongoError as db_err:
            logger.error(f"MongoDB error in generate_user_dashboard: {str(db_err)}")
            return {"success": False, "status_code": 500, "message": "Database query failure.", "error": "DATABASE_ERROR"}
        except Exception as err:
            logger.critical(f"Unexpected error in generate_user_dashboard: {str(err)}", exc_info=True)
            return {"success": False, "status_code": 500, "message": "Internal server error.", "error": "INTERNAL_SERVER_ERROR"}

    @classmethod
    def generate_platform_dashboard(cls) -> Dict[str, Any]:
        """
        Generates platform-wide analytics using scalable MongoDB aggregation pipelines.
        Calculates overall candidate volume, pass rates, and technology distribution.

        Returns:
            Dict[str, Any]: Standardized API response with platform telemetry.
        """
        try:
            db = Database.get_db()

            pipeline = [
                {
                    "$group": {
                        "_id": None,
                        "total_assessments": {"$sum": 1},
                        "avg_platform_score": {"$avg": "$totalScore"},
                        "avg_platform_percentage": {"$avg": "$percentage"},
                        "max_score": {"$max": "$totalScore"},
                        "min_score": {"$min": "$totalScore"},
                        "total_time_spent": {"$sum": "$totalTime"}
                    }
                }
            ]

            res_cursor = list(db.analytics.aggregate(pipeline))
            stats = res_cursor[0] if res_cursor else {
                "total_assessments": 0,
                "avg_platform_score": 0.0,
                "avg_platform_percentage": 0.0,
                "max_score": 0.0,
                "min_score": 0.0,
                "total_time_spent": 0
            }

            stats.pop("_id", None)
            if stats["total_assessments"] > 0:
                stats["avg_platform_score"] = round(stats["avg_platform_score"], 2)
                stats["avg_platform_percentage"] = round(stats["avg_platform_percentage"], 2)

            return {
                "success": True,
                "status_code": 200,
                "message": "Platform analytics generated successfully.",
                "data": stats
            }

        except PyMongoError as db_err:
            logger.error(f"MongoDB error in generate_platform_dashboard: {str(db_err)}")
            return {"success": False, "status_code": 500, "message": "Database aggregation failure.", "error": "DATABASE_ERROR"}
        except Exception as err:
            logger.critical(f"Unexpected error in generate_platform_dashboard: {str(err)}", exc_info=True)
            return {"success": False, "status_code": 500, "message": "Internal server error.", "error": "INTERNAL_SERVER_ERROR"}
