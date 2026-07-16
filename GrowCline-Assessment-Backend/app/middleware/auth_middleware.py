"""
Authentication Middleware Module
Provides route decorators to protect endpoints with JWT authentication.
"""

from functools import wraps
from flask import request, jsonify, g
from bson import ObjectId

try:
    from utils.jwt_utils import decode_token
except ImportError:
    from app.utils.jwt_utils import decode_token

try:
    from config.database import Database
except ImportError:
    from app.config.database import Database


def token_required(f):
    """
    Decorator to protect routes requiring a valid JWT bearer token.
    Extracts the token from the Authorization header, validates it,
    and attaches the authenticated user document to flask.g.current_user.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({
                "success": False,
                "message": "Unauthorized."
            }), 401

        token = auth_header.split(" ", 1)[1].strip()
        if not token:
            return jsonify({
                "success": False,
                "message": "Unauthorized."
            }), 401

        payload = decode_token(token)
        if not payload or not payload.get("id"):
            return jsonify({
                "success": False,
                "message": "Unauthorized."
            }), 401

        try:
            db = Database.get_db()
            user = db.users.find_one({"_id": ObjectId(payload["id"])})
            if not user:
                return jsonify({
                    "success": False,
                    "message": "Unauthorized."
                }), 401

            g.current_user = user
        except Exception:
            return jsonify({
                "success": False,
                "message": "Unauthorized."
            }), 401

        return f(*args, **kwargs)

    return decorated
