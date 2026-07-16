"""
JWT Utility Module
Provides functions to generate and decode JSON Web Tokens (JWT).
"""

import datetime
import os
import jwt

JWT_SECRET = os.environ.get("JWT_SECRET", os.environ.get("JWT_SECRET_KEY", "growcline-super-secret-key"))
JWT_ALGORITHM = "HS256"


def generate_token(payload: dict, expires_in_hours: int = 24) -> str:
    """
    Generate a JWT token for a given payload.

    Args:
        payload (dict): Data dictionary to encode inside token.
        expires_in_hours (int): Token expiration time in hours.

    Returns:
        str: Encoded JWT token string.
    """
    token_data = payload.copy()
    now = datetime.datetime.now(datetime.timezone.utc)
    token_data["iat"] = now
    token_data["exp"] = now + datetime.timedelta(hours=expires_in_hours)
    return jwt.encode(token_data, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict | None:
    """
    Decode and validate a JWT token.

    Args:
        token (str): JWT token string.

    Returns:
        dict | None: Decoded payload dictionary if valid, None otherwise.
    """
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except Exception:
        return None
