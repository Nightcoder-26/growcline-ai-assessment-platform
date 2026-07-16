"""
Analytics Controller Module
Handles dashboard statistics, user performance dashboards, and saving/retrieving analytics.
"""

from datetime import datetime, timezone
from flask import request, jsonify
from bson import ObjectId

try:
    from config.database import Database
    from services.analytics_service import AnalyticsService
except ImportError:
    from app.config.database import Database
    from app.services.analytics_service import AnalyticsService


class AnalyticsController:
    """Analytics Controller"""

    @staticmethod
    def get_dashboard(user_id=None):
        """
        GET/POST /api/analytics/dashboard or /api/analytics/dashboard/<user_id>
        If POST: Saves/records user dashboard analytics.
        If GET: Fetches dashboard analytics.
        """
        try:
            db = Database.get_db()

            if request.method == "POST":
                payload = request.get_json(silent=True) or {}
                target_user_id = user_id or payload.get("userId", payload.get("user_id"))

                doc = dict(payload)
                if target_user_id:
                    doc["userId"] = target_user_id
                doc["createdAt"] = datetime.now(timezone.utc)
                doc["updatedAt"] = datetime.now(timezone.utc)

                if "_id" in doc:
                    doc.pop("_id", None)

                # Save record to both dashboard_analytics and analytics collections
                res = db.dashboard_analytics.insert_one(dict(doc))
                try:
                    db.analytics.insert_one(dict(doc))
                except Exception:
                    pass

                doc["_id"] = str(res.inserted_id)

                return jsonify({
                    "success": True,
                    "message": "Dashboard analytics saved successfully to dashboard_analytics collection.",
                    "collection": "dashboard_analytics",
                    "data": doc
                }), 200

            # GET request
            if user_id:
                # Check if a custom dashboard analytics document was saved in dashboard_analytics collection
                saved_doc = db.dashboard_analytics.find_one({"userId": user_id}, sort=[("updatedAt", -1)])
                if not saved_doc:
                    saved_doc = db.dashboard_analytics.find_one({"user_id": user_id}, sort=[("updatedAt", -1)])
                if saved_doc:
                    saved_doc["_id"] = str(saved_doc["_id"])
                    return jsonify({
                        "success": True,
                        "data": saved_doc
                    }), 200

                res = AnalyticsService.generate_user_dashboard(user_id)
                return jsonify(res), res.get("status_code", 200)

            # Global Dashboard Statistics
            users = db.users.count_documents({})
            assessments = db.assessments.count_documents({})
            results = db.assessment_results.count_documents({})
            aptitude_questions = db.aptitude_questions.count_documents({})
            technical_questions = db.technical_questions.count_documents({})
            coding_questions = db.coding_questions.count_documents({})

            average_score = 0
            pipeline = [
                {
                    "$group": {
                        "_id": None,
                        "average": {"$avg": "$overall_score"}
                    }
                }
            ]
            agg = list(db.assessment_results.aggregate(pipeline))
            if agg:
                average_score = round(agg[0]["average"], 2)

            analytics = {
                "total_users": users,
                "total_assessments": assessments,
                "total_results": results,
                "aptitude_questions": aptitude_questions,
                "technical_questions": technical_questions,
                "coding_questions": coding_questions,
                "average_score": average_score,
            }

            return jsonify({
                "success": True,
                "message": "Dashboard analytics fetched successfully.",
                "data": analytics,
            }), 200

        except Exception as error:
            return jsonify({
                "success": False,
                "message": str(error)
            }), 500

    @staticmethod
    def get_candidate_analytics(user_id):
        try:
            res = AnalyticsService.generate_user_dashboard(user_id)
            return jsonify(res), res.get("status_code", 200)
        except Exception as error:
            return jsonify({"success": False, "message": str(error)}), 500

    @staticmethod
    def get_assessment_analytics(assessment_id):
        try:
            db = Database.get_db()
            results = list(db.assessment_results.find({"assessment_id": assessment_id}))
            for r in results:
                r["_id"] = str(r["_id"])
            return jsonify({"success": True, "count": len(results), "data": results}), 200
        except Exception as error:
            return jsonify({"success": False, "message": str(error)}), 500

    @staticmethod
    def get_performance_trends():
        try:
            db = Database.get_db()
            total_users = db.users.count_documents({})
            total_assessments = db.assessments.count_documents({})
            completed_assessments = db.assessments.count_documents({"status": "Completed"})
            return jsonify({
                "success": True,
                "data": {
                    "total_users": total_users,
                    "total_assessments": total_assessments,
                    "completed_assessments": completed_assessments,
                }
            }), 200
        except Exception as error:
            return jsonify({"success": False, "message": str(error)}), 500

    @staticmethod
    def get_skill_analysis(user_id=None):
        try:
            if user_id:
                res = AnalyticsService.generate_user_dashboard(user_id)
                return jsonify(res), res.get("status_code", 200)

            db = Database.get_db()
            pipeline = [
                {
                    "$group": {
                        "_id": None,
                        "aptitude": {"$avg": "$aptitude_score"},
                        "technical": {"$avg": "$technical_score"},
                        "coding": {"$avg": "$coding_score"},
                        "overall": {"$avg": "$overall_score"},
                    }
                }
            ]
            agg = list(db.assessment_results.aggregate(pipeline))
            averages = agg[0] if agg else {}
            return jsonify({"success": True, "data": averages}), 200
        except Exception as error:
            return jsonify({"success": False, "message": str(error)}), 500