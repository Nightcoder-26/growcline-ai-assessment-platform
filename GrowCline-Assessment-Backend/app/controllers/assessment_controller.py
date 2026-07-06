"""
Assessment Controller
Handles assessment lifecycle operations.
"""

from datetime import datetime
from bson import ObjectId
from flask import request, jsonify

try:
    from config.database import Database
except ImportError:
    from app.config.database import Database


class AssessmentController:
    """Assessment Controller"""

    @staticmethod
    def create_assessment():
        try:
            db = Database.get_db()

            data = request.get_json()

            assessment = {
                "title": data.get("title"),
                "description": data.get("description"),
                "job_role": data.get("job_role"),
                "duration": data.get("duration"),
                "total_questions": data.get("total_questions"),
                "status": "Draft",
                "created_at": datetime.utcnow(),
            }

            result = db.assessments.insert_one(assessment)

            return jsonify({
                "success": True,
                "message": "Assessment created successfully.",
                "assessment_id": str(result.inserted_id)
            }), 201

        except Exception as error:
            return jsonify({
                "success": False,
                "message": str(error)
            }), 500

    @staticmethod
    def get_assessments():
        try:
            db = Database.get_db()

            assessments = list(
                db.assessments.find().sort("created_at", -1)
            )

            for assessment in assessments:
                assessment["_id"] = str(assessment["_id"])

            return jsonify({
                "success": True,
                "count": len(assessments),
                "data": assessments
            }), 200

        except Exception as error:
            return jsonify({
                "success": False,
                "message": str(error)
            }), 500

    @staticmethod
    def get_assessment(assessment_id):
        try:
            db = Database.get_db()

            assessment = db.assessments.find_one({
                "_id": ObjectId(assessment_id)
            })

            if not assessment:
                return jsonify({
                    "success": False,
                    "message": "Assessment not found."
                }), 404

            assessment["_id"] = str(assessment["_id"])

            return jsonify({
                "success": True,
                "data": assessment
            }), 200

        except Exception as error:
            return jsonify({
                "success": False,
                "message": str(error)
            }), 500

    @staticmethod
    def update_assessment(assessment_id):
        try:
            db = Database.get_db()
            data = request.get_json()
            if not data:
                return jsonify({"success": False, "message": "No data provided"}), 400

            update_fields = {}
            for field in ["title", "description", "job_role", "duration", "total_questions", "status"]:
                if field in data:
                    update_fields[field] = data[field]
            if "jobRole" in data:
                update_fields["job_role"] = data["jobRole"]
            if "totalQuestions" in data:
                update_fields["total_questions"] = data["totalQuestions"]

            if not update_fields:
                return jsonify({"success": False, "message": "No valid fields to update"}), 400

            update_fields["updated_at"] = datetime.utcnow()
            result = db.assessments.update_one({"_id": ObjectId(assessment_id)}, {"$set": update_fields})
            if result.matched_count == 0:
                return jsonify({"success": False, "message": "Assessment not found."}), 404

            return jsonify({"success": True, "message": "Assessment updated successfully."}), 200
        except Exception as error:
            return jsonify({"success": False, "message": str(error)}), 500

    @staticmethod
    def start_assessment(assessment_id):
        try:
            db = Database.get_db()

            result = db.assessments.update_one(
                {
                    "_id": ObjectId(assessment_id)
                },
                {
                    "$set": {
                        "status": "In Progress",
                        "started_at": datetime.utcnow()
                    }
                }
            )

            if result.matched_count == 0:
                return jsonify({
                    "success": False,
                    "message": "Assessment not found."
                }), 404

            return jsonify({
                "success": True,
                "message": "Assessment started successfully."
            }), 200

        except Exception as error:
            return jsonify({
                "success": False,
                "message": str(error)
            }), 500

    @staticmethod
    def submit_assessment(assessment_id):
        try:
            db = Database.get_db()

            result = db.assessments.update_one(
                {
                    "_id": ObjectId(assessment_id)
                },
                {
                    "$set": {
                        "status": "Completed",
                        "submitted_at": datetime.utcnow()
                    }
                }
            )

            if result.matched_count == 0:
                return jsonify({
                    "success": False,
                    "message": "Assessment not found."
                }), 404

            return jsonify({
                "success": True,
                "message": "Assessment submitted successfully."
            }), 200

        except Exception as error:
            return jsonify({
                "success": False,
                "message": str(error)
            }), 500

    @staticmethod
    def delete_assessment(assessment_id):
        try:
            db = Database.get_db()

            result = db.assessments.delete_one({
                "_id": ObjectId(assessment_id)
            })

            if result.deleted_count == 0:
                return jsonify({
                    "success": False,
                    "message": "Assessment not found."
                }), 404

            return jsonify({
                "success": True,
                "message": "Assessment deleted successfully."
            }), 200

        except Exception as error:
            return jsonify({
                "success": False,
                "message": str(error)
            }), 500

    @staticmethod
    def assessment_history(user_id):
        try:
            db = Database.get_db()

            history = list(
                db.assessment_results.find({
                    "user_id": user_id
                }).sort("submitted_at", -1)
            )

            for item in history:
                item["_id"] = str(item["_id"])

            return jsonify({
                "success": True,
                "count": len(history),
                "data": history
            }), 200

        except Exception as error:
            return jsonify({
                "success": False,
                "message": str(error)
            }), 500

    @staticmethod
    def get_all_assessments():
        return AssessmentController.get_assessments()

    @staticmethod
    def get_assessment_by_id(assessment_id):
        return AssessmentController.get_assessment(assessment_id)