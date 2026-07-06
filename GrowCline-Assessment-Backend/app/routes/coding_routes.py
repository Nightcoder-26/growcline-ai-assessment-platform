from flask import Blueprint

try:
    from controllers.coding_controller import CodingController
except ImportError:
    from app.controllers.coding_controller import CodingController

coding_bp = Blueprint("coding", __name__, url_prefix="/api/coding")

# Create Coding Question
coding_bp.route("/questions", methods=["POST"])(CodingController.create_question)

# Get All Coding Questions
coding_bp.route("/questions", methods=["GET"])(CodingController.get_all_questions)

# Get Coding Question By ID
coding_bp.route("/questions/<string:question_id>", methods=["GET"])(CodingController.get_question_by_id)

# Update Coding Question
coding_bp.route("/questions/<string:question_id>", methods=["PUT"])(CodingController.update_question)

# Delete Coding Question
coding_bp.route("/questions/<string:question_id>", methods=["DELETE"])(CodingController.delete_question)

# Generate Coding Assessment
coding_bp.route("/generate", methods=["POST"])(CodingController.generate_assessment)

# Submit Code
coding_bp.route("/submit", methods=["POST"])(CodingController.submit_code)

# Get Submission Result
coding_bp.route("/result/<string:submission_id>", methods=["GET"])(CodingController.get_submission_result)