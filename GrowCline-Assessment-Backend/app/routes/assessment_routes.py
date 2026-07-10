"""
Assessment Routes Module
Registers endpoints for Assessment creation, listing, retrieval, starting, and submitting.
Supports both /api/assessment (singular) and /api/assessments (plural).
"""

from flask import Blueprint

try:
    from controllers.assessment_controller import AssessmentController
except ImportError:
    from app.controllers.assessment_controller import AssessmentController

assessment_bp = Blueprint("assessment", __name__, url_prefix="/api/assessment")
assessments_plural_bp = Blueprint("assessments_plural", __name__, url_prefix="/api/assessments")

for bp in [assessment_bp, assessments_plural_bp]:
    prefix = bp.name
    # Create Assessment & Get All Assessments
    bp.route("", methods=["POST"], endpoint=f"create_assessment_root_{prefix}")(AssessmentController.create_assessment)
    bp.route("/", methods=["POST"], endpoint=f"create_assessment_root_slash_{prefix}")(AssessmentController.create_assessment)
    bp.route("", methods=["GET"], endpoint=f"get_all_assessments_root_{prefix}")(AssessmentController.get_all_assessments)
    bp.route("/", methods=["GET"], endpoint=f"get_all_assessments_root_slash_{prefix}")(AssessmentController.get_all_assessments)

    # Single Assessment by ID
    bp.route("/<string:assessment_id>", methods=["GET"], endpoint=f"get_assessment_by_id_{prefix}")(AssessmentController.get_assessment_by_id)
    bp.route("/<string:assessment_id>", methods=["PUT"], endpoint=f"update_assessment_{prefix}")(AssessmentController.update_assessment)
    bp.route("/<string:assessment_id>", methods=["DELETE"], endpoint=f"delete_assessment_{prefix}")(AssessmentController.delete_assessment)

    # Start and Submit Assessment
    bp.route("/<string:assessment_id>/start", methods=["POST"], endpoint=f"start_assessment_{prefix}")(AssessmentController.start_assessment)
    bp.route("/<string:assessment_id>/submit", methods=["POST"], endpoint=f"submit_assessment_{prefix}")(AssessmentController.submit_assessment)