"""
Password Utility Module
Provides secure password hashing and verification using bcrypt.
"""

import bcrypt


def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt.

    Args:
        password (str): Plain text password.

    Returns:
        str: Hashed password string.
    """
    if not password:
        raise ValueError("Password cannot be empty.")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a bcrypt hash.

    Args:
        password (str): Plain text password.
        hashed_password (str): Stored bcrypt password hash.

    Returns:
        bool: True if password matches hash, False otherwise.
    """
    if not password or not hashed_password:
        return False
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except Exception:
        return False
