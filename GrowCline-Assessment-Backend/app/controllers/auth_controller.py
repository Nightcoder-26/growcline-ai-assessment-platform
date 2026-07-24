"""
Authentication Controller Module
Handles user registration, login, profile management, and password updates.
"""

from datetime import datetime, timezone
from typing import Dict, Tuple, Optional, Any
from bson import ObjectId

from app.config.database import Database
from app.utils.password_utils import hash_password, verify_password
from app.utils.jwt_utils import generate_token


def serialize_user(user: dict) -> dict:
    """
    Serialize a user MongoDB document for JSON responses.
    Excludes sensitive fields like password.
    """
    serialized: Dict[str, Any] = {}
    for key, value in user.items():
        if key == "password":
            continue
        if key == "_id":
            serialized["_id"] = str(value)
        elif isinstance(value, ObjectId):
            serialized[key] = str(value)
        elif isinstance(value, datetime):
            serialized[key] = value.isoformat()
        else:
            serialized[key] = value

    if "fullName" not in serialized and "name" in serialized:
        serialized["fullName"] = serialized["name"]
    return serialized


class AuthController:
    """Authentication Controller"""

    @staticmethod
    def register(data: dict) -> Tuple[dict, int]:
        """
        POST /api/auth/register
        Registers a new candidate user with bcrypt password hashing.
        """
        try:
            full_name = data.get("fullName") or data.get("name")
            email = data.get("email")
            password = data.get("password")
            role = data.get("role", "candidate")

            if not full_name or not email or not password:
                return {
                    "success": False,
                    "message": "All fields are required."
                }, 400

            full_name = str(full_name).strip()
            email = str(email).strip().lower()
            password = str(password)

            if not full_name or not email or not password:
                return {
                    "success": False,
                    "message": "All fields are required."
                }, 400

            if len(password) < 8:
                return {
                    "success": False,
                    "message": "Password must be at least 8 characters long."
                }, 400

            db = Database.get_db()
            existing_user = db.users.find_one({"email": email})
            if existing_user:
                return {
                    "success": False,
                    "message": "Email already exists."
                }, 400

            hashed_password = hash_password(password)
            now = datetime.now(timezone.utc)

            user_doc = {
                "fullName": full_name,
                "name": full_name,
                "email": email,
                "password": hashed_password,
                "role": role,
                "createdAt": now,
            }

            db.users.insert_one(user_doc)

            return {
                "success": True,
                "message": "User registered successfully"
            }, 201

        except Exception as error:
            return {
                "success": False,
                "message": str(error)
            }, 500

    @staticmethod
    def login(data: dict) -> Tuple[dict, int]:
        """
        POST /api/auth/login
        Validates user credentials and returns a JWT access token.
        """
        try:
            email = data.get("email")
            password = data.get("password")

            if not email or not password:
                return {
                    "success": False,
                    "message": "All fields are required."
                }, 400

            email = str(email).strip().lower()
            password = str(password)

            db = Database.get_db()
            user = db.users.find_one({"email": email})

            if not user or not verify_password(password, user.get("password", "")):
                return {
                    "success": False,
                    "message": "Invalid email or password."
                }, 401

            token = generate_token({
                "id": str(user["_id"]),
                "email": user.get("email", ""),
                "role": user.get("role", "candidate")
            })

            full_name = user.get("fullName", user.get("name", ""))

            return {
                "success": True,
                "token": token,
                "user": {
                    "_id": str(user["_id"]),
                    "fullName": full_name,
                    "email": user.get("email", "")
                }
            }, 200

        except Exception as error:
            return {
                "success": False,
                "message": str(error)
            }, 500

    @staticmethod
    def get_profile(current_user: Optional[dict] = None, user_id: Optional[str] = None) -> Tuple[dict, int]:
        """
        GET /api/auth/profile
        Returns the profile of the currently authenticated user.
        """
        try:
            user = current_user

            if not user and user_id:
                db = Database.get_db()
                user = db.users.find_one({"_id": ObjectId(user_id)})

            if not user:
                return {
                    "success": False,
                    "message": "Unauthorized."
                }, 401

            serialized_user = serialize_user(user)

            return {
                "success": True,
                "user": serialized_user
            }, 200

        except Exception as error:
            return {
                "success": False,
                "message": str(error)
            }, 500

    @staticmethod
    def update_profile(data: dict, current_user: Optional[dict] = None, user_id: Optional[str] = None) -> Tuple[dict, int]:
        """
        PUT /api/auth/profile
        Updates candidate profile information.
        """
        try:
            if not user_id and current_user:
                user_id = str(current_user["_id"])
            if not user_id:
                user_id = data.get("user_id")

            if not user_id:
                return {
                    "success": False,
                    "message": "User ID is required."
                }, 400

            db = Database.get_db()
            update_fields = {}
            if "fullName" in data or "name" in data:
                update_fields["fullName"] = data.get("fullName", data.get("name"))
                update_fields["name"] = update_fields["fullName"]
            if "email" in data:
                update_fields["email"] = str(data["email"]).strip().lower()

            if not update_fields:
                return {
                    "success": False,
                    "message": "No fields to update."
                }, 400

            db.users.update_one({"_id": ObjectId(user_id)}, {"$set": update_fields})
            return {
                "success": True,
                "message": "Profile updated successfully."
            }, 200
        except Exception as error:
            return {
                "success": False,
                "message": str(error)
            }, 500

    @staticmethod
    def change_password(data: dict, current_user: Optional[dict] = None, user_id: Optional[str] = None) -> Tuple[dict, int]:
        """
        PUT /api/auth/change-password
        Changes the candidate password after verifying current password.
        """
        try:
            if not user_id and current_user:
                user_id = str(current_user["_id"])
            if not user_id:
                user_id = data.get("user_id")

            current_password = data.get("current_password", data.get("currentPassword"))
            new_password = data.get("new_password", data.get("newPassword"))

            if not user_id or not current_password or not new_password:
                return {
                    "success": False,
                    "message": "User ID, current password, and new password are required."
                }, 400

            db = Database.get_db()
            found_user = db.users.find_one({"_id": ObjectId(user_id)})
            if not found_user or not verify_password(current_password, found_user.get("password", "")):
                return {
                    "success": False,
                    "message": "Invalid current password."
                }, 401

            hashed_password = hash_password(new_password)
            db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"password": hashed_password}})
            return {
                "success": True,
                "message": "Password changed successfully."
            }, 200
        except Exception as error:
            return {
                "success": False,
                "message": str(error)
            }, 500