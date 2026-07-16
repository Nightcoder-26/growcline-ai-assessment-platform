"""
Technical Routes Module
Registers endpoints for Technical Assessment CRUD, test generation, and submission.
"""

from flask import Blueprint

try:
    from controllers.technical_controller import TechnicalController
except ImportError:
    from app.controllers.technical_controller import TechnicalController

technical_bp = Blueprint("technical", __name__, url_prefix="/api/technical")

# Root /api/technical CRUD routes (must work directly on POST /api/technical per prompt requirements)
technical_bp.route("", methods=["POST"], endpoint="create_tech_question_root")(TechnicalController.create_question)
technical_bp.route("/", methods=["POST"], endpoint="create_tech_question_root_slash")(TechnicalController.create_question)
technical_bp.route("", methods=["GET"], endpoint="get_all_tech_questions_root")(TechnicalController.get_all_questions)
technical_bp.route("/", methods=["GET"], endpoint="get_all_tech_questions_root_slash")(TechnicalController.get_all_questions)

# Single Question by ID under /api/technical/<question_id>
technical_bp.route("/<string:question_id>", methods=["GET"], endpoint="get_tech_question_by_id")(TechnicalController.get_question_by_id)
technical_bp.route("/<string:question_id>", methods=["PUT"], endpoint="update_tech_question")(TechnicalController.update_question)
technical_bp.route("/<string:question_id>", methods=["DELETE"], endpoint="delete_tech_question")(TechnicalController.delete_question)

# Backward-compatible routes under /api/technical/questions
technical_bp.route("/questions", methods=["POST"], endpoint="create_tech_question_sub")(TechnicalController.create_question)
technical_bp.route("/questions", methods=["GET"], endpoint="get_all_tech_questions_sub")(TechnicalController.get_all_questions)
technical_bp.route("/questions/<string:question_id>", methods=["GET"], endpoint="get_tech_question_by_id_sub")(TechnicalController.get_question_by_id)
technical_bp.route("/questions/<string:question_id>", methods=["PUT"], endpoint="update_tech_question_sub")(TechnicalController.update_question)
technical_bp.route("/questions/<string:question_id>", methods=["DELETE"], endpoint="delete_tech_question_sub")(TechnicalController.delete_question)

# Assessment Generation & Submission
technical_bp.route("/generate", methods=["POST"], endpoint="generate_tech_assessment")(TechnicalController.generate_assessment)
technical_bp.route("/submit", methods=["POST"], endpoint="submit_tech_assessment")(TechnicalController.submit_assessment)