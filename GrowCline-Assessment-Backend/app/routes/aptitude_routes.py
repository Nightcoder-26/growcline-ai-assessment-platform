"""
Aptitude Routes Module
Registers endpoints for Aptitude CRUD, test generation, and submission.
"""

from flask import Blueprint

try:
    from controllers.aptitude_controller import AptitudeController
except ImportError:
    from app.controllers.aptitude_controller import AptitudeController

aptitude_bp = Blueprint("aptitude", __name__, url_prefix="/api/aptitude")

# Root /api/aptitude CRUD routes (must work directly on POST /api/aptitude per prompt requirements)
aptitude_bp.route("", methods=["POST"], endpoint="create_question_root")(AptitudeController.create_question)
aptitude_bp.route("/", methods=["POST"], endpoint="create_question_root_slash")(AptitudeController.create_question)
aptitude_bp.route("", methods=["GET"], endpoint="get_all_questions_root")(AptitudeController.get_all_questions)
aptitude_bp.route("/", methods=["GET"], endpoint="get_all_questions_root_slash")(AptitudeController.get_all_questions)

# Single Question by ID under /api/aptitude/<question_id>
aptitude_bp.route("/<string:question_id>", methods=["GET"], endpoint="get_question_by_id")(AptitudeController.get_question_by_id)
aptitude_bp.route("/<string:question_id>", methods=["PUT"], endpoint="update_question")(AptitudeController.update_question)
aptitude_bp.route("/<string:question_id>", methods=["DELETE"], endpoint="delete_question")(AptitudeController.delete_question)

# Backward-compatible routes under /api/aptitude/questions
aptitude_bp.route("/questions", methods=["POST"], endpoint="create_question_sub")(AptitudeController.create_question)
aptitude_bp.route("/questions", methods=["GET"], endpoint="get_all_questions_sub")(AptitudeController.get_all_questions)
aptitude_bp.route("/questions/<string:question_id>", methods=["GET"], endpoint="get_question_by_id_sub")(AptitudeController.get_question_by_id)
aptitude_bp.route("/questions/<string:question_id>", methods=["PUT"], endpoint="update_question_sub")(AptitudeController.update_question)
aptitude_bp.route("/questions/<string:question_id>", methods=["DELETE"], endpoint="delete_question_sub")(AptitudeController.delete_question)

# Assessment Generation & Submission
aptitude_bp.route("/generate", methods=["POST"], endpoint="generate_assessment")(AptitudeController.generate_assessment)
aptitude_bp.route("/submit", methods=["POST"], endpoint="submit_assessment")(AptitudeController.submit_assessment)