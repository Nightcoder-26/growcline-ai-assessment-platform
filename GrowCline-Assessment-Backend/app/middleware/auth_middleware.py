"""
Authentication Middleware Module
Provides a FastAPI dependency to protect endpoints with JWT authentication.
"""

from typing import Optional
from fastapi import Header, HTTPException
from bson import ObjectId

from app.utils.jwt_utils import decode_token
from app.config.database import Database


async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """
    FastAPI dependency that validates a Bearer JWT token from the Authorization header.
    Extracts the token, validates it, and verifies the user still exists in MongoDB.
    Returns the authenticated user document dict.

    Raises:
        HTTPException 401: on missing, malformed, invalid, or expired token,
                           or if the user no longer exists.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized."
        )

    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized."
        )

    payload = decode_token(token)
    if not payload or not payload.get("id"):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized."
        )

    try:
        db = Database.get_db()
        user = db.users.find_one({"_id": ObjectId(payload["id"])})
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Unauthorized."
            )
        return user
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized."
        )
