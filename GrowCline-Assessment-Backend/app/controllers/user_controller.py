"""
User Controller Module
Handles User Management CRUD HTTP request parsing, validation formatting, and responses.
Architecture: Controller -> Service -> Model
"""

from flask import request, jsonify
from marshmallow import ValidationError

try:
    from services.user_service import UserService
except ImportError:
    from app.services.user_service import UserService


def _format_validation_error(error: ValidationError) -> str:
    """Extract a user-friendly error string from Marshmallow ValidationError."""
    messages = error.messages
    if isinstance(messages, dict):
        for field, errs in messages.items():
            if isinstance(errs, list) and errs:
                return str(errs[0])
            return str(errs)
    elif isinstance(messages, list) and messages:
        return str(messages[0])
    return str(messages)


class UserController:
    """User Management Controller for complete CRUD HTTP endpoints."""

    @staticmethod
    def create_user():
        """
        POST /api/users
        Create a new user.
        """
        try:
            payload = request.get_json(silent=True) or {}
            user_data = UserService.create_user(payload)
            return jsonify({
                "success": True,
                "message": "User created successfully.",
                "data": user_data
            }), 201
        except ValidationError as error:
            return jsonify({
                "success": False,
                "message": _format_validation_error(error)
            }), 400
        except ValueError as error:
            return jsonify({
                "success": False,
                "message": str(error)
            }), 400
        except Exception as error:
            return jsonify({
                "success": False,
                "message": str(error)
            }), 500

    @staticmethod
    def get_all_users():
        """
        GET /api/users
        Retrieve all users.
        """
        try:
            users_list = UserService.get_all_users()
            return jsonify({
                "success": True,
                "data": users_list
            }), 200
        except Exception as error:
            return jsonify({
                "success": False,
                "message": str(error)
            }), 500

    @staticmethod
    def get_user_by_id(user_id: str):
        """
        GET /api/users/<user_id>
        Retrieve a user by ID.
        """
        try:
            user_data = UserService.get_user_by_id(user_id)
            if not user_data:
                return jsonify({
                    "success": False,
                    "message": "User not found."
                }), 404
            return jsonify({
                "success": True,
                "data": user_data
            }), 200
        except ValueError as error:
            return jsonify({
                "success": False,
                "message": str(error)
            }), 400
        except Exception as error:
            return jsonify({
                "success": False,
                "message": str(error)
            }), 500

    @staticmethod
    def update_user(user_id: str):
        """
        PUT /api/users/<user_id>
        Update a user by ID (Protected Route).
        """
        try:
            payload = request.get_json(silent=True) or {}
            updated_data = UserService.update_user(user_id, payload)
            if not updated_data:
                return jsonify({
                    "success": False,
                    "message": "User not found."
                }), 404
            return jsonify({
                "success": True,
                "message": "User updated successfully.",
                "data": updated_data
            }), 200
        except ValidationError as error:
            return jsonify({
                "success": False,
                "message": _format_validation_error(error)
            }), 400
        except ValueError as error:
            return jsonify({
                "success": False,
                "message": str(error)
            }), 400
        except Exception as error:
            return jsonify({
                "success": False,
                "message": str(error)
            }), 500

    @staticmethod
    def delete_user(user_id: str):
        """
        DELETE /api/users/<user_id>
        Delete a user by ID (Protected Route).
        """
        try:
            deleted = UserService.delete_user(user_id)
            if not deleted:
                return jsonify({
                    "success": False,
                    "message": "User not found."
                }), 404
            return jsonify({
                "success": True,
                "message": "User deleted successfully."
            }), 200
        except ValueError as error:
            return jsonify({
                "success": False,
                "message": str(error)
            }), 400
        except Exception as error:
            return jsonify({
                "success": False,
                "message": str(error)
            }), 500
