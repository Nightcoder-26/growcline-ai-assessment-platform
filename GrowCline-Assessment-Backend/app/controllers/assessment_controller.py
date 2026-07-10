"""
Assessment Controller
Handles assessment lifecycle operations (Create, List, Get, Update, Delete, Start, Submit).
"""

from datetime import datetime, timezone
from bson import ObjectId
from flask import request, jsonify

try:
    from config.database import Database
    from services.assessment_service import AssessmentService
    from models.assessment_model import Assessment
except ImportError:
    from app.config.database import Database
    from app.services.assessment_service import AssessmentService
    from app.models.assessment_model import Assessment


class AssessmentController:
    """Assessment Controller"""

    @staticmethod
    def create_assessment():
        """
        POST /api/assessment
        Creates an assessment from provided user and question IDs.
        """
        try:
            payload = request.get_json(silent=True) or {}

            # Delegate to AssessmentService which handles full validation & DB insertion
            res = AssessmentService.create_assessment(payload)

            if not res.get("success"):
                return jsonify({
                    "success": False,
                    "message": res.get("message", "Failed to create assessment.")
                }), res.get("status_code", 400)

            data = res.get("data", {})
            return jsonify({
                "success": True,
                "message": "Assessment created successfully.",
                "assessment_id": data.get("id", data.get("_id")),
                "data": data
            }), 201

        except Exception as error:
            return jsonify({
                "success": False,
                "message": str(error)
            }), 500

    @staticmethod
    def get_all_assessments():
        """
        GET /api/assessment
        Retrieves all assessments.
        """
        try:
            db = Database.get_db()
            query = {}
            user_id = request.args.get("userId", request.args.get("user_id"))
            if user_id and ObjectId.is_valid(user_id):
                query["userId"] = ObjectId(user_id)

            assessments_cursor = db.assessments.find(query).sort("createdAt", -1)
            assessments = [Assessment.response(doc) for doc in assessments_cursor if doc]

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
    def get_assessment_by_id(assessment_id):
        """
        GET /api/assessment/<assessment_id>
        Retrieves an assessment by ID.
        """
        try:
            res = AssessmentService.get_assessment_by_id(assessment_id)
            if not res.get("success"):
                return jsonify({
                    "success": False,
                    "message": res.get("message", "Assessment not found.")
                }), res.get("status_code", 404)

            return jsonify({
                "success": True,
                "data": res.get("data")
            }), 200

        except Exception as error:
            return jsonify({
                "success": False,
                "message": str(error)
            }), 500

    @staticmethod
    def update_assessment(assessment_id):
        """
        PUT /api/assessment/<assessment_id>
        Updates assessment metadata or question assignments.
        """
        try:
            if not ObjectId.is_valid(assessment_id):
                return jsonify({
                    "success": False,
                    "message": "Invalid assessment ID format."
                }), 400

            data = request.get_json(silent=True) or {}
            db = Database.get_db()

            update_fields = {}
            if "title" in data:
                update_fields["title"] = data["title"]
            if "duration" in data:
                update_fields["duration"] = int(data["duration"])
            if "status" in data:
                update_fields["status"] = data["status"]

            update_fields["updatedAt"] = datetime.now(timezone.utc)

            result = db.assessments.update_one(
                {"_id": ObjectId(assessment_id)},
                {"$set": update_fields}
            )

            if result.matched_count == 0:
                return jsonify({
                    "success": False,
                    "message": "Assessment not found."
                }), 404

            doc = db.assessments.find_one({"_id": ObjectId(assessment_id)})

            return jsonify({
                "success": True,
                "message": "Assessment updated successfully.",
                "data": Assessment.response(doc)
            }), 200

        except Exception as error:
            return jsonify({
                "success": False,
                "message": str(error)
            }), 500

    @staticmethod
    def delete_assessment(assessment_id):
        """
        DELETE /api/assessment/<assessment_id>
        Deletes an assessment by ID.
        """
        try:
            if not ObjectId.is_valid(assessment_id):
                return jsonify({
                    "success": False,
                    "message": "Invalid assessment ID format."
                }), 400

            db = Database.get_db()
            result = db.assessments.delete_one({"_id": ObjectId(assessment_id)})

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
    def start_assessment(assessment_id):
        """
        POST /api/assessment/<assessment_id>/start
        Starts an assessment test session.
        """
        try:
            res = AssessmentService.start_assessment(assessment_id)
            if not res.get("success"):
                return jsonify({
                    "success": False,
                    "message": res.get("message", "Failed to start assessment.")
                }), res.get("status_code", 400)

            return jsonify({
                "success": True,
                "message": res.get("message", "Assessment started successfully."),
                "data": res.get("data")
            }), 200

        except Exception as error:
            return jsonify({
                "success": False,
                "message": str(error)
            }), 500

    @staticmethod
    def submit_assessment(assessment_id):
        """
        POST /api/assessment/<assessment_id>/submit
        Submits candidate answers for scoring.
        """
        try:
            payload = request.get_json(silent=True) or {}
            res = AssessmentService.submit_assessment(assessment_id, payload)

            if not res.get("success"):
                return jsonify({
                    "success": False,
                    "message": res.get("message", "Failed to submit assessment.")
                }), res.get("status_code", 400)

            return jsonify({
                "success": True,
                "message": res.get("message", "Assessment submitted successfully."),
                "data": res.get("data")
            }), 200

        except Exception as error:
            return jsonify({
                "success": False,
                "message": str(error)
            }), 500