from flask import Blueprint

try:
    from controllers.auth_controller import AuthController
except ImportError:
    from app.controllers.auth_controller import AuthController

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# Register User
auth_bp.route("/register", methods=["POST"])(AuthController.register)

# Login User
auth_bp.route("/login", methods=["POST"])(AuthController.login)

# Get Profile
auth_bp.route("/profile", methods=["GET"])(AuthController.get_profile)
auth_bp.route("/profile/<string:user_id>", methods=["GET"])(AuthController.get_profile)

# Update Profile
auth_bp.route("/profile", methods=["PUT"])(AuthController.update_profile)
auth_bp.route("/profile/<string:user_id>", methods=["PUT"])(AuthController.update_profile)

# Change Password
auth_bp.route("/change-password", methods=["PUT"])(AuthController.change_password)