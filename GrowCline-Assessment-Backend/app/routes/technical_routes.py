from flask import Blueprint

try:
    from controllers.technical_controller import TechnicalController
except ImportError:
    from app.controllers.technical_controller import TechnicalController

technical_bp = Blueprint("technical", __name__, url_prefix="/api/technical")

# Create Technical Question
technical_bp.route("/questions", methods=["POST"])(TechnicalController.create_question)

# Get All Technical Questions
technical_bp.route("/questions", methods=["GET"])(TechnicalController.get_all_questions)

# Get Technical Question By ID
technical_bp.route("/questions/<string:question_id>", methods=["GET"])(TechnicalController.get_question_by_id)

# Update Technical Question
technical_bp.route("/questions/<string:question_id>", methods=["PUT"])(TechnicalController.update_question)

# Delete Technical Question
technical_bp.route("/questions/<string:question_id>", methods=["DELETE"])(TechnicalController.delete_question)

# Generate Technical Assessment
technical_bp.route("/generate", methods=["POST"])(TechnicalController.generate_assessment)

# Submit Technical Assessment
technical_bp.route("/submit", methods=["POST"])(TechnicalController.submit_assessment)