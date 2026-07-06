from flask import Blueprint

try:
    from controllers.result_controller import ResultController
except ImportError:
    from app.controllers.result_controller import ResultController

result_bp = Blueprint("result", __name__, url_prefix="/api/results")

# Calculate Assessment Result
result_bp.route("/calculate", methods=["POST"])(ResultController.calculate_result)
result_bp.route("/", methods=["POST"])(ResultController.save_result)

# Get All Results
result_bp.route("/", methods=["GET"])(ResultController.get_all_results)

# Get Result By ID
result_bp.route("/<string:result_id>", methods=["GET"])(ResultController.get_result_by_id)

# Get Candidate Result History
result_bp.route("/candidate/<string:user_id>", methods=["GET"])(ResultController.get_candidate_results)

# Get Assessment Result
result_bp.route("/assessment/<string:assessment_id>", methods=["GET"])(ResultController.get_assessment_result)

# Delete Result
result_bp.route("/<string:result_id>", methods=["DELETE"])(ResultController.delete_result)