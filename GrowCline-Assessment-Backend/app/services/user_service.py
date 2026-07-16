"""
User Service Module
Implements business logic and database interactions for User Management CRUD.
Architecture: Controller -> Service -> Model
"""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from bson import ObjectId
from marshmallow import ValidationError

try:
    from config.database import Database
except ImportError:
    from app.config.database import Database

try:
    from models.user_model import User
except ImportError:
    from app.models.user_model import User

try:
    from schemas.user_schema import UserCreateSchema, UserUpdateSchema
except ImportError:
    from app.schemas.user_schema import UserCreateSchema, UserUpdateSchema

try:
    from utils.password_utils import hash_password
except ImportError:
    from app.utils.password_utils import hash_password


class UserService:
    """User Management Service implementing complete CRUD operations."""

    @staticmethod
    def create_user(payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new user document after validation, duplicate email check, and password hashing.
        """
        schema = UserCreateSchema()
        validated_data = schema.load(payload or {})

        email = validated_data["email"].strip().lower()
        full_name = validated_data.get("fullName", validated_data.get("name", "")).strip()
        password = validated_data["password"]
        role = validated_data.get("role", "candidate")

        db = Database.get_db()

        # Check if email already exists
        existing_user = db.users.find_one({"email": email})
        if existing_user:
            raise ValueError("Email already exists.")

        # Hash password using bcrypt
        hashed_password = hash_password(password)

        # Create user document
        user_doc = User.create_user(
            full_name=full_name,
            email=email,
            password=hashed_password,
            role=role
        )

        db.users.insert_one(user_doc)

        return User.public_user(user_doc)

    @staticmethod
    def get_all_users() -> List[Dict[str, Any]]:
        """
        Retrieve all users from MongoDB users collection.
        """
        db = Database.get_db()
        users_cursor = db.users.find({})
        users_list = []
        for user_doc in users_cursor:
            public_doc = User.public_user(user_doc)
            if public_doc:
                users_list.append(public_doc)
        return users_list

    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a user by ObjectId.
        """
        if not ObjectId.is_valid(user_id):
            raise ValueError("Invalid ObjectId format.")

        db = Database.get_db()
        user_doc = db.users.find_one({"_id": ObjectId(user_id)})
        if not user_doc:
            return None

        return User.public_user(user_doc)

    @staticmethod
    def update_user(user_id: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update an existing user by ObjectId.
        """
        if not ObjectId.is_valid(user_id):
            raise ValueError("Invalid ObjectId format.")

        schema = UserUpdateSchema()
        validated_data = schema.load(payload or {})

        db = Database.get_db()
        existing_user = db.users.find_one({"_id": ObjectId(user_id)})
        if not existing_user:
            return None

        update_fields: Dict[str, Any] = {
            "updatedAt": datetime.now(timezone.utc)
        }

        if "fullName" in validated_data:
            update_fields["fullName"] = validated_data["fullName"].strip()
        elif "name" in validated_data:
            update_fields["fullName"] = validated_data["name"].strip()

        if "email" in validated_data:
            new_email = validated_data["email"].strip().lower()
            if new_email != existing_user.get("email", "").lower():
                duplicate = db.users.find_one({
                    "email": new_email,
                    "_id": {"$ne": ObjectId(user_id)}
                })
                if duplicate:
                    raise ValueError("Email already exists.")
            update_fields["email"] = new_email

        if "password" in validated_data and validated_data["password"]:
            update_fields["password"] = hash_password(validated_data["password"])

        if "role" in validated_data:
            update_fields["role"] = validated_data["role"]

        db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_fields}
        )

        updated_doc = db.users.find_one({"_id": ObjectId(user_id)})
        return User.public_user(updated_doc)

    @staticmethod
    def delete_user(user_id: str) -> bool:
        """
        Delete a user by ObjectId.
        """
        if not ObjectId.is_valid(user_id):
            raise ValueError("Invalid ObjectId format.")

        db = Database.get_db()
        existing_user = db.users.find_one({"_id": ObjectId(user_id)})
        if not existing_user:
            return False

        db.users.delete_one({"_id": ObjectId(user_id)})
        return True
