"""
Coding Routes Module
Registers endpoints for Coding Assessment CRUD, test generation, and submission.
"""

from flask import Blueprint

try:
    from controllers.coding_controller import CodingController
except ImportError:
    from app.controllers.coding_controller import CodingController

coding_bp = Blueprint("coding", __name__, url_prefix="/api/coding")

# Root /api/coding CRUD routes (must return 201 Created directly on POST /api/coding per prompt requirements)
coding_bp.route("", methods=["POST"], endpoint="create_coding_question_root")(CodingController.create_question)
coding_bp.route("/", methods=["POST"], endpoint="create_coding_question_root_slash")(CodingController.create_question)
coding_bp.route("", methods=["GET"], endpoint="get_all_coding_questions_root")(CodingController.get_all_questions)
coding_bp.route("/", methods=["GET"], endpoint="get_all_coding_questions_root_slash")(CodingController.get_all_questions)

# Single Question by ID under /api/coding/<question_id>
coding_bp.route("/<string:question_id>", methods=["GET"], endpoint="get_coding_question_by_id")(CodingController.get_question_by_id)
coding_bp.route("/<string:question_id>", methods=["PUT"], endpoint="update_coding_question")(CodingController.update_question)
coding_bp.route("/<string:question_id>", methods=["DELETE"], endpoint="delete_coding_question")(CodingController.delete_question)

# Backward-compatible routes under /api/coding/questions
coding_bp.route("/questions", methods=["POST"], endpoint="create_coding_question_sub")(CodingController.create_question)
coding_bp.route("/questions", methods=["GET"], endpoint="get_all_coding_questions_sub")(CodingController.get_all_questions)
coding_bp.route("/questions/<string:question_id>", methods=["GET"], endpoint="get_coding_question_by_id_sub")(CodingController.get_question_by_id)
coding_bp.route("/questions/<string:question_id>", methods=["PUT"], endpoint="update_coding_question_sub")(CodingController.update_question)
coding_bp.route("/questions/<string:question_id>", methods=["DELETE"], endpoint="delete_coding_question_sub")(CodingController.delete_question)

# Assessment Generation & Submission
coding_bp.route("/generate", methods=["POST"], endpoint="generate_coding_assessment")(CodingController.generate_assessment)
coding_bp.route("/submit", methods=["POST"], endpoint="submit_coding_assessment")(CodingController.submit_assessment)