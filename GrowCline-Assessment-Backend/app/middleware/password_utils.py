"""
Password Utilities Middleware Wrapper
Re-exports password utilities from app.utils.password_utils.
"""

from app.utils.password_utils import hash_password, verify_password

__all__ = ["hash_password", "verify_password"]
