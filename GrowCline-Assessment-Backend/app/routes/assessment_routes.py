from flask import Blueprint

try:
    from controllers.assessment_controller import AssessmentController
except ImportError:
    from app.controllers.assessment_controller import AssessmentController

assessment_bp = Blueprint("assessment", __name__, url_prefix="/api/assessments")

# Create Assessment
assessment_bp.route("/", methods=["POST"])(AssessmentController.create_assessment)

# Get All Assessments
assessment_bp.route("/", methods=["GET"])(AssessmentController.get_all_assessments)

# Get Assessment By ID
assessment_bp.route("/<string:assessment_id>", methods=["GET"])(AssessmentController.get_assessment_by_id)

# Update Assessment
assessment_bp.route("/<string:assessment_id>", methods=["PUT"])(AssessmentController.update_assessment)

# Delete Assessment
assessment_bp.route("/<string:assessment_id>", methods=["DELETE"])(AssessmentController.delete_assessment)

# Start Assessment
assessment_bp.route("/<string:assessment_id>/start", methods=["POST"])(AssessmentController.start_assessment)

# Submit Assessment
assessment_bp.route("/<string:assessment_id>/submit", methods=["POST"])(AssessmentController.submit_assessment)