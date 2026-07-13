"""
Unit Test Suite for User Management CRUD APIs (/api/users)
Tests Controller -> Service -> Model layer integration and JWT authentication protection.
"""

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
from bson import ObjectId
from flask import Flask

try:
    from routes.user_routes import user_bp
    from models.user_model import User
    from utils.jwt_utils import generate_token
except ImportError:
    from app.routes.user_routes import user_bp
    from app.models.user_model import User
    from app.utils.jwt_utils import generate_token


class TestUserCRUDAPI(unittest.TestCase):
    """Test suite for User Management CRUD API endpoints."""

    def setUp(self):
        self.app = Flask(__name__)
        self.app.register_blueprint(user_bp, url_prefix="/api/users")
        self.client = self.app.test_client()


        self.mock_db = MagicMock()
        self.users_collection = MagicMock()
        self.mock_db.users = self.users_collection

        self.test_user_id = str(ObjectId())
        self.test_user_doc = {
            "_id": ObjectId(self.test_user_id),
            "fullName": "Vasant Jevengekar",
            "email": "vasant@gmail.com",
            "password": "hashed_password",
            "role": "candidate",
            "createdAt": datetime.now(timezone.utc),
            "updatedAt": datetime.now(timezone.utc),
        }

        self.auth_token = generate_token({"id": self.test_user_id, "role": "candidate"})
        self.auth_headers = {
            "Authorization": f"Bearer {self.auth_token}"
        }

    @patch("app.services.user_service.Database.get_db")
    def test_01_create_user_success(self, mock_get_db):
        """Test POST /api/users successfully creates a user."""
        mock_get_db.return_value = self.mock_db
        self.users_collection.find_one.return_value = None  # No existing email

        payload = {
            "fullName": "Vasant",
            "email": "vasant@gmail.com",
            "password": "12345678",
            "role": "candidate"
        }

        response = self.client.post("/api/users", json=payload)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["message"], "User created successfully.")
        self.assertEqual(data["data"]["email"], "vasant@gmail.com")

    @patch("app.services.user_service.Database.get_db")
    def test_02_create_user_duplicate_email(self, mock_get_db):
        """Test POST /api/users fails when email is already registered."""
        mock_get_db.return_value = self.mock_db
        self.users_collection.find_one.return_value = self.test_user_doc

        payload = {
            "fullName": "Vasant",
            "email": "vasant@gmail.com",
            "password": "12345678",
            "role": "candidate"
        }

        response = self.client.post("/api/users", json=payload)
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data["success"])
        self.assertIn("Email already exists", data["message"])

    @patch("app.services.user_service.Database.get_db")
    def test_03_get_all_users(self, mock_get_db):
        """Test GET /api/users returns list of users."""
        mock_get_db.return_value = self.mock_db
        self.users_collection.find.return_value = [self.test_user_doc]

        response = self.client.get("/api/users")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertIsInstance(data["data"], list)
        self.assertEqual(len(data["data"]), 1)

    @patch("app.services.user_service.Database.get_db")
    def test_04_get_user_by_id_success(self, mock_get_db):
        """Test GET /api/users/<user_id> returns user details."""
        mock_get_db.return_value = self.mock_db
        self.users_collection.find_one.return_value = self.test_user_doc

        response = self.client.get(f"/api/users/{self.test_user_id}")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["id"], self.test_user_id)

    @patch("app.services.user_service.Database.get_db")
    def test_05_get_user_by_id_invalid_id(self, mock_get_db):
        """Test GET /api/users/<user_id> with invalid ObjectId returns 400."""
        response = self.client.get("/api/users/invalid_id")
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data["success"])

    @patch("app.middleware.auth_middleware.Database.get_db")
    @patch("app.services.user_service.Database.get_db")
    def test_06_update_user_protected(self, mock_svc_db, mock_auth_db):
        """Test PUT /api/users/<user_id> requires valid auth token and updates user."""
        mock_auth_db.return_value = self.mock_db
        mock_svc_db.return_value = self.mock_db
        self.users_collection.find_one.return_value = self.test_user_doc

        # Test unauthorized request without Authorization header
        response_unauth = self.client.put(
            f"/api/users/{self.test_user_id}",
            json={"fullName": "Updated Name"}
        )
        self.assertEqual(response_unauth.status_code, 401)

        # Test authorized request
        response_auth = self.client.put(
            f"/api/users/{self.test_user_id}",
            headers=self.auth_headers,
            json={"fullName": "Updated Name", "role": "admin"}
        )
        self.assertEqual(response_auth.status_code, 200)
        data = response_auth.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["message"], "User updated successfully.")

    @patch("app.middleware.auth_middleware.Database.get_db")
    @patch("app.services.user_service.Database.get_db")
    def test_07_delete_user_protected(self, mock_svc_db, mock_auth_db):
        """Test DELETE /api/users/<user_id> requires token and deletes user."""
        mock_auth_db.return_value = self.mock_db
        mock_svc_db.return_value = self.mock_db
        self.users_collection.find_one.return_value = self.test_user_doc

        # Test unauthorized request
        response_unauth = self.client.delete(f"/api/users/{self.test_user_id}")
        self.assertEqual(response_unauth.status_code, 401)

        # Test authorized request
        response_auth = self.client.delete(
            f"/api/users/{self.test_user_id}",
            headers=self.auth_headers
        )
        self.assertEqual(response_auth.status_code, 200)
        data = response_auth.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["message"], "User deleted successfully.")


if __name__ == "__main__":
    unittest.main()
