
from flask import jsonify
try:
    from config.database import Database
except ImportError:
    from app.config.database import Database


class AnalyticsController:
    """Analytics Controller"""

    @staticmethod
    def get_dashboard():
        """
        Dashboard Statistics
        """

        try:
            db = Database.get_db()

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
                        "average": {
                            "$avg": "$overall_score"
                        }
                    }
                }
            ]

            result = list(
                db.assessment_results.aggregate(
                    pipeline
                )
            )

            if result:
                average_score = round(
                    result[0]["average"],
                    2
                )

            analytics = {
                "total_users": users,
                "total_assessments": assessments,
                "total_results": results,
                "aptitude_questions": aptitude_questions,
                "technical_questions": technical_questions,
                "coding_questions": coding_questions,
                "average_score": average_score,
            }

            return (
                jsonify(
                    {
                        "success": True,
                        "message": "Dashboard analytics fetched successfully.",
                        "data": analytics,
                    }
                ),
                200,
            )

        except Exception as error:

            return (
                jsonify(
                    {
                        "success": False,
                        "message": str(error),
                    }
                ),
                500,
            )

    @staticmethod
    def get_overall_statistics():
        """
        Overall Assessment Statistics
        """

        try:
            db = Database.get_db()

            total_users = db.users.count_documents({})

            total_assessments = db.assessments.count_documents({})

            completed_assessments = db.assessments.count_documents(
                {
                    "status": "Completed"
                }
            )

            statistics = {
                "total_users": total_users,
                "total_assessments": total_assessments,
                "completed_assessments": completed_assessments,
            }

            return (
                jsonify(
                    {
                        "success": True,
                        "data": statistics,
                    }
                ),
                200,
            )

        except Exception as error:

            return (
                jsonify(
                    {
                        "success": False,
                        "message": str(error),
                    }
                ),
                500,
            )

    @staticmethod
    def get_average_scores():
        """
        Calculate Average Scores
        """

        try:
            db = Database.get_db()

            pipeline = [
                {
                    "$group": {
                        "_id": None,
                        "aptitude": {
                            "$avg": "$aptitude_score"
                        },
                        "technical": {
                            "$avg": "$technical_score"
                        },
                        "coding": {
                            "$avg": "$coding_score"
                        },
                        "overall": {
                            "$avg": "$overall_score"
                        },
                    }
                }
            ]

            result = list(
                db.assessment_results.aggregate(
                    pipeline
                )
            )

            averages = result[0] if result else {}

            return (
                jsonify(
                    {
                        "success": True,
                        "data": averages,
                    }
                ),
                200,
            )

        except Exception as error:

            return (
                jsonify(
                    {
                        "success": False,
                        "message": str(error),
                    }
                ),
                500,
            )

    @staticmethod
    def get_candidate_analytics(user_id):
        try:
            db = Database.get_db()
            results = list(db.assessment_results.find({"user_id": user_id}))
            for r in results:
                r["_id"] = str(r["_id"])
            return jsonify({"success": True, "count": len(results), "data": results}), 200
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
        return AnalyticsController.get_overall_statistics()

    @staticmethod
    def get_skill_analysis(user_id):
        return AnalyticsController.get_average_scores()