"""
Authentication Controller
Handles user registration, login, and profile retrieval.
"""

from flask import request, jsonify
from config.database import Database
from utils.password_utils import hash_password, verify_password
from utils.jwt_utils import generate_token, decode_token
from bson import ObjectId


class AuthController:
    """Authentication Controller"""

    @staticmethod
    def register():
        try:
            db = Database.get_db()

            data = request.get_json()

            name = data.get("name")
            email = data.get("email")
            password = data.get("password")
            role = data.get("role", "candidate")

            if not name or not email or not password:
                return jsonify({
                    "success": False,
                    "message": "All fields are required."
                }), 400

            existing_user = db.users.find_one({
                "email": email
            })

            if existing_user:
                return jsonify({
                    "success": False,
                    "message": "Email already exists."
                }), 409

            hashed_password = hash_password(password)

            user = {
                "name": name,
                "email": email,
                "password": hashed_password,
                "role": role
            }

            result = db.users.insert_one(user)

            return jsonify({
                "success": True,
                "message": "User registered successfully.",
                "user_id": str(result.inserted_id)
            }), 201

        except Exception as error:
            return jsonify({
                "success": False,
                "message": str(error)
            }), 500

    @staticmethod
    def login():
        try:
            db = Database.get_db()

            data = request.get_json()

            email = data.get("email")
            password = data.get("password")

            if not email or not password:
                return jsonify({
                    "success": False,
                    "message": "Email and password are required."
                }), 400

            user = db.users.find_one({
                "email": email
            })

            if not user:
                return jsonify({
                    "success": False,
                    "message": "Invalid credentials."
                }), 401

            if not verify_password(password, user["password"]):
                return jsonify({
                    "success": False,
                    "message": "Invalid credentials."
                }), 401

            token = generate_token({
                "id": str(user["_id"]),
                "email": user["email"],
                "role": user["role"]
            })

            return jsonify({
                "success": True,
                "message": "Login successful.",
                "token": token,
                "user": {
                    "id": str(user["_id"]),
                    "name": user["name"],
                    "email": user["email"],
                    "role": user["role"]
                }
            }), 200

        except Exception as error:
            return jsonify({
                "success": False,
                "message": str(error)
            }), 500

    @staticmethod
    def get_profile(user_id):
        try:
            db = Database.get_db()

            user = db.users.find_one({
                "_id": ObjectId(user_id)
            })

            if not user:
                return jsonify({
                    "success": False,
                    "message": "User not found."
                }), 404

            user.pop("password", None)

            user["_id"] = str(user["_id"])

            return jsonify({
                "success": True,
                "user": user
            }), 200

        except Exception as error:
            return jsonify({
                "success": False,
                "message": str(error)
            }), 500