from flask import Blueprint

from app.controllers.assessment_controller import (
    create_assessment,
    get_all_assessments,
    get_assessment_by_id,
    update_assessment,
    delete_assessment,
    start_assessment,
    submit_assessment,
)

assessment_bp = Blueprint(
    "assessment",
    __name__,
    url_prefix="/api/assessments"
)

# Create Assessment
assessment_bp.route(
    "/",
    methods=["POST"]
)(create_assessment)

# Get All Assessments
assessment_bp.route(
    "/",
    methods=["GET"]
)(get_all_assessments)

# Get Assessment By ID
assessment_bp.route(
    "/<string:assessment_id>",
    methods=["GET"]
)(get_assessment_by_id)

# Update Assessment
assessment_bp.route(
    "/<string:assessment_id>",
    methods=["PUT"]
)(update_assessment)

# Delete Assessment
assessment_bp.route(
    "/<string:assessment_id>",
    methods=["DELETE"]
)(delete_assessment)

# Start Assessment
assessment_bp.route(
    "/<string:assessment_id>/start",
    methods=["POST"]
)(start_assessment)

# Submit Assessment
assessment_bp.route(
    "/<string:assessment_id>/submit",
    methods=["POST"]
)(submit_assessment)