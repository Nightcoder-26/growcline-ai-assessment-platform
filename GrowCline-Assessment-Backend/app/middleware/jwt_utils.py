"""
JWT Utilities Middleware Wrapper
Re-exports JWT utilities from app.utils.jwt_utils.
"""

from app.utils.jwt_utils import generate_token, decode_token

__all__ = ["generate_token", "decode_token"]
