from flask import Blueprint

from app.controllers.result_controller import (
    calculate_result,
    get_all_results,
    get_result_by_id,
    get_candidate_results,
    get_assessment_result,
    delete_result,
)

result_bp = Blueprint(
    "result",
    __name__,
    url_prefix="/api/results"
)

# Calculate Assessment Result
result_bp.route(
    "/calculate",
    methods=["POST"]
)(calculate_result)

# Get All Results
result_bp.route(
    "/",
    methods=["GET"]
)(get_all_results)

# Get Result By ID
result_bp.route(
    "/<string:result_id>",
    methods=["GET"]
)(get_result_by_id)

# Get Candidate Result History
result_bp.route(
    "/candidate/<string:user_id>",
    methods=["GET"]
)(get_candidate_results)

# Get Assessment Result
result_bp.route(
    "/assessment/<string:assessment_id>",
    methods=["GET"]
)(get_assessment_result)

# Delete Result
result_bp.route(
    "/<string:result_id>",
    methods=["DELETE"]
)(delete_result)