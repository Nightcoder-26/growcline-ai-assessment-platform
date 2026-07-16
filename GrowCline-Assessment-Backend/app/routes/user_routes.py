"""
User Routes Module
Registers endpoints for User Management CRUD under /api/users.
"""

from flask import Blueprint

try:
    from controllers.user_controller import UserController
    from middleware.auth_middleware import token_required
except ImportError:
    from app.controllers.user_controller import UserController
    from app.middleware.auth_middleware import token_required

user_bp = Blueprint("users", __name__, url_prefix="/api/users")

# 1. Create User (POST /api/users)
user_bp.route("", methods=["POST"], endpoint="create_user_root")(UserController.create_user)
user_bp.route("/", methods=["POST"], endpoint="create_user_slash")(UserController.create_user)

# 2. Get All Users (GET /api/users)
user_bp.route("", methods=["GET"], endpoint="get_all_users_root")(UserController.get_all_users)
user_bp.route("/", methods=["GET"], endpoint="get_all_users_slash")(UserController.get_all_users)

# 3. Get User By ID (GET /api/users/<user_id>)
user_bp.route("/<string:user_id>", methods=["GET"], endpoint="get_user_by_id")(UserController.get_user_by_id)

# 4. Update User (PUT /api/users/<user_id>) - Protected Route
user_bp.route("/<string:user_id>", methods=["PUT"], endpoint="update_user")(token_required(UserController.update_user))

# 5. Delete User (DELETE /api/users/<user_id>) - Protected Route
user_bp.route("/<string:user_id>", methods=["DELETE"], endpoint="delete_user")(token_required(UserController.delete_user))
