from flask import Blueprint

from app.controllers.coding_controller import (
    create_question,
    get_all_questions,
    get_question_by_id,
    update_question,
    delete_question,
    generate_assessment,
    submit_code,
    get_submission_result,
)

coding_bp = Blueprint(
    "coding",
    __name__,
    url_prefix="/api/coding"
)

# Create Coding Question
coding_bp.route(
    "/questions",
    methods=["POST"]
)(create_question)

# Get All Coding Questions
coding_bp.route(
    "/questions",
    methods=["GET"]
)(get_all_questions)

# Get Coding Question By ID
coding_bp.route(
    "/questions/<string:question_id>",
    methods=["GET"]
)(get_question_by_id)

# Update Coding Question
coding_bp.route(
    "/questions/<string:question_id>",
    methods=["PUT"]
)(update_question)

# Delete Coding Question
coding_bp.route(
    "/questions/<string:question_id>",
    methods=["DELETE"]
)(delete_question)

# Generate Coding Assessment
coding_bp.route(
    "/generate",
    methods=["POST"]
)(generate_assessment)

# Submit Code
coding_bp.route(
    "/submit",
    methods=["POST"]
)(submit_code)

# Get Submission Result
coding_bp.route(
    "/result/<string:submission_id>",
    methods=["GET"]
)(get_submission_result)