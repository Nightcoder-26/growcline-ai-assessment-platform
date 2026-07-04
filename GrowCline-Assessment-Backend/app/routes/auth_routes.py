from flask import Blueprint

from app.controllers.auth_controller import (
    register_user,
    login_user,
    get_profile,
    update_profile,
    change_password,
)

auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/api/auth"
)

# Register User
auth_bp.route(
    "/register",
    methods=["POST"]
)(register_user)

# Login User
auth_bp.route(
    "/login",
    methods=["POST"]
)(login_user)

# Get Logged-in User Profile
auth_bp.route(
    "/profile",
    methods=["GET"]
)(get_profile)

# Update User Profile
auth_bp.route(
    "/profile",
    methods=["PUT"]
)(update_profile)

# Change Password
auth_bp.route(
    "/change-password",
    methods=["PUT"]
)(change_password)