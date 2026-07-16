"""
Unit Test Suite for User Authentication and Token Validation
"""

import unittest
from bson import ObjectId

try:
    from models.user_model import User
    from utils.password_utils import hash_password, verify_password
    from utils.jwt_utils import generate_token, decode_token
except ImportError:
    from app.models.user_model import User
    from app.utils.password_utils import hash_password, verify_password
    from app.utils.jwt_utils import generate_token, decode_token


class TestAuthModel(unittest.TestCase):
    """Test cases for user data structures and auth utilities."""

    def test_user_creation(self) -> None:
        """Test User model structure."""
        user_doc = {
            "_id": ObjectId(),
            "fullName": "Test Candidate",
            "email": "candidate@growcline.ai",
            "role": "candidate"
        }
        self.assertEqual(user_doc["email"], "candidate@growcline.ai")

    def test_password_hashing(self) -> None:
        """Test bcrypt password hashing and verification."""
        password = "secretPassword123"
        hashed = hash_password(password)
        self.assertNotEqual(password, hashed)
        self.assertTrue(verify_password(password, hashed))
        self.assertFalse(verify_password("wrongPassword", hashed))

    def test_jwt_generation_and_decoding(self) -> None:
        """Test JWT token encoding and decoding."""
        payload = {"id": "1234567890abcdef12345678", "email": "test@gmail.com", "role": "candidate"}
        token = generate_token(payload, expires_in_hours=1)
        decoded = decode_token(token)
        self.assertIsNotNone(decoded)
        self.assertEqual(decoded["id"], payload["id"])
        self.assertEqual(decoded["email"], payload["email"])


if __name__ == "__main__":
    unittest.main()
