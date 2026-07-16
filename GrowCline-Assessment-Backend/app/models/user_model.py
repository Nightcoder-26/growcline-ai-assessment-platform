from datetime import datetime, timezone
from bson import ObjectId


class User:
    """User Model representing MongoDB users collection documents."""

    @staticmethod
    def create_user(
        full_name,
        email,
        password,
        role="candidate"
    ):
        now = datetime.now(timezone.utc)
        return {
            "_id": ObjectId(),
            "fullName": full_name,
            "email": email.lower(),
            "password": password,
            "role": role or "candidate",
            "isActive": True,
            "isVerified": False,
            "profileImage": None,
            "phone": "",
            "college": "",
            "branch": "",
            "graduationYear": None,
            "skills": [],
            "createdAt": now,
            "updatedAt": now,
        }

    @staticmethod
    def public_user(user):
        if not user:
            return None

        created_at = user.get("createdAt")
        if isinstance(created_at, datetime):
            created_at = created_at.isoformat()

        updated_at = user.get("updatedAt")
        if isinstance(updated_at, datetime):
            updated_at = updated_at.isoformat()

        return {
            "_id": str(user["_id"]),
            "id": str(user["_id"]),
            "fullName": user.get("fullName", user.get("name", "")),
            "email": user.get("email", ""),
            "role": user.get("role", "candidate"),
            "isActive": user.get("isActive", True),
            "isVerified": user.get("isVerified", False),
            "profileImage": user.get("profileImage"),
            "phone": user.get("phone"),
            "college": user.get("college"),
            "branch": user.get("branch"),
            "graduationYear": user.get("graduationYear"),
            "skills": user.get("skills", []),
            "createdAt": created_at,
            "updatedAt": updated_at,
        }