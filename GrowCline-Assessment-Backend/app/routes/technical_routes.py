from flask import Blueprint

from app.controllers.technical_controller import (
    create_question,
    get_all_questions,
    get_question_by_id,
    update_question,
    delete_question,
    generate_assessment,
    submit_assessment,
)

technical_bp = Blueprint(
    "technical",
    __name__,
    url_prefix="/api/technical"
)

# Create Technical Question
technical_bp.route(
    "/questions",
    methods=["POST"]
)(create_question)

# Get All Technical Questions
technical_bp.route(
    "/questions",
    methods=["GET"]
)(get_all_questions)

# Get Technical Question By ID
technical_bp.route(
    "/questions/<string:question_id>",
    methods=["GET"]
)(get_question_by_id)

# Update Technical Question
technical_bp.route(
    "/questions/<string:question_id>",
    methods=["PUT"]
)(update_question)

# Delete Technical Question
technical_bp.route(
    "/questions/<string:question_id>",
    methods=["DELETE"]
)(delete_question)

# Generate Technical Assessment
technical_bp.route(
    "/generate",
    methods=["POST"]
)(generate_assessment)

# Submit Technical Assessment
technical_bp.route(
    "/submit",
    methods=["POST"]
)(submit_assessment)