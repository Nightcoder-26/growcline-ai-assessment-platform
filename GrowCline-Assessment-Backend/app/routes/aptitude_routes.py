from flask import Blueprint

from app.controllers.aptitude_controller import (
    create_question,
    get_all_questions,
    get_question_by_id,
    update_question,
    delete_question,
    generate_assessment,
    submit_assessment,
)

aptitude_bp = Blueprint(
    "aptitude",
    __name__,
    url_prefix="/api/aptitude"
)

# Create Question
aptitude_bp.route(
    "/questions",
    methods=["POST"]
)(create_question)

# Get All Questions
aptitude_bp.route(
    "/questions",
    methods=["GET"]
)(get_all_questions)

# Get Question By ID
aptitude_bp.route(
    "/questions/<string:question_id>",
    methods=["GET"]
)(get_question_by_id)

# Update Question
aptitude_bp.route(
    "/questions/<string:question_id>",
    methods=["PUT"]
)(update_question)

# Delete Question
aptitude_bp.route(
    "/questions/<string:question_id>",
    methods=["DELETE"]
)(delete_question)

# Generate Aptitude Assessment
aptitude_bp.route(
    "/generate",
    methods=["POST"]
)(generate_assessment)

# Submit Aptitude Assessment
aptitude_bp.route(
    "/submit",
    methods=["POST"]
)(submit_assessment)