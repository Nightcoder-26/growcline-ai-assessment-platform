"""
Authentication Routes Module
Registers endpoints for registration, login, and profile operations under /api/auth.
"""

from flask import Blueprint

try:
    from controllers.auth_controller import AuthController
    from middleware.auth_middleware import token_required
except ImportError:
    from app.controllers.auth_controller import AuthController
    from app.middleware.auth_middleware import token_required

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# Register User
auth_bp.route("/register", methods=["POST"], endpoint="register")(AuthController.register)

# Login User
auth_bp.route("/login", methods=["POST"], endpoint="login")(AuthController.login)

# Get Profile (Protected Route)
auth_bp.route("/profile", methods=["GET"], endpoint="get_profile_protected")(token_required(AuthController.get_profile))
auth_bp.route("/profile/<string:user_id>", methods=["GET"], endpoint="get_profile_by_id")(AuthController.get_profile)

# Update Profile (Protected Route)
auth_bp.route("/profile", methods=["PUT"], endpoint="update_profile_protected")(token_required(AuthController.update_profile))
auth_bp.route("/profile/<string:user_id>", methods=["PUT"], endpoint="update_profile_by_id")(AuthController.update_profile)

# Change Password (Protected Route)
auth_bp.route("/change-password", methods=["PUT"], endpoint="change_password")(token_required(AuthController.change_password))