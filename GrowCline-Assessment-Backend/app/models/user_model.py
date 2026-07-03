from datetime import datetime
from bson import ObjectId


class User:
    @staticmethod
    def create_user(
        full_name,
        email,
        password,
        role="candidate"
    ):
        return {
            "_id": ObjectId(),
            "fullName": full_name,
            "email": email.lower(),
            "password": password,
            "role": role,
            "isActive": True,
            "isVerified": False,
            "profileImage": None,
            "phone": "",
            "college": "",
            "branch": "",
            "graduationYear": None,
            "skills": [],
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
        }

    @staticmethod
    def public_user(user):
        return {
            "id": str(user["_id"]),
            "fullName": user["fullName"],
            "email": user["email"],
            "role": user["role"],
            "isActive": user["isActive"],
            "isVerified": user["isVerified"],
            "profileImage": user.get("profileImage"),
            "phone": user.get("phone"),
            "college": user.get("college"),
            "branch": user.get("branch"),
            "graduationYear": user.get("graduationYear"),
            "skills": user.get("skills", []),
            "createdAt": user["createdAt"],
        }