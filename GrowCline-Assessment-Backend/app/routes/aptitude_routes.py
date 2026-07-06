from flask import Blueprint

try:
    from controllers.aptitude_controller import AptitudeController
except ImportError:
    from app.controllers.aptitude_controller import AptitudeController

aptitude_bp = Blueprint("aptitude", __name__, url_prefix="/api/aptitude")

# Create Question
aptitude_bp.route("/questions", methods=["POST"])(AptitudeController.create_question)

# Get All Questions
aptitude_bp.route("/questions", methods=["GET"])(AptitudeController.get_all_questions)

# Get Question By ID
aptitude_bp.route("/questions/<string:question_id>", methods=["GET"])(AptitudeController.get_question_by_id)

# Update Question
aptitude_bp.route("/questions/<string:question_id>", methods=["PUT"])(AptitudeController.update_question)

# Delete Question
aptitude_bp.route("/questions/<string:question_id>", methods=["DELETE"])(AptitudeController.delete_question)

# Generate Aptitude Assessment
aptitude_bp.route("/generate", methods=["POST"])(AptitudeController.generate_assessment)

# Submit Aptitude Assessment
aptitude_bp.route("/submit", methods=["POST"])(AptitudeController.submit_assessment)