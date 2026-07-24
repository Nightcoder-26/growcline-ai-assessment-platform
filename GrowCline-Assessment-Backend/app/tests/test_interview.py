"""
Unit and integration tests for AI interview features (/api/interviews).
"""

import unittest
from unittest.mock import patch, MagicMock
from bson import ObjectId
from fastapi.testclient import TestClient
from fastapi.responses import JSONResponse

from app import app
from app.utils.jwt_utils import generate_token


class TestInterviewAPI(unittest.TestCase):
    """Test suite for /api/interviews endpoints."""

    def setUp(self):
        self.client = TestClient(app)
        self.mock_db = MagicMock()
        self.test_user_id = str(ObjectId())
        self.test_interview_id = str(ObjectId())
        self.auth_token = generate_token({"id": self.test_user_id, "role": "candidate"})
        self.headers = {"Authorization": f"Bearer {self.auth_token}"}

    @patch("app.routes.interview_routes.Database.get_db")
    @patch("app.controllers.interview_controller.InterviewController.start_interview")
    def test_start_interview(self, mock_controller, mock_get_db):
        mock_get_db.return_value = self.mock_db
        mock_controller.return_value = JSONResponse(
            status_code=201,
            content={"success": True, "data": {"interview_id": self.test_interview_id}}
        )

        payload = {
            "jobRole": "Backend Engineer",
            "interviewType": "TECHNICAL",
            "difficulty": "MEDIUM"
        }

        res = self.client.post("/api/interviews/start", json=payload, headers=self.headers)
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertTrue(data["success"])

    @patch("app.routes.interview_routes.Database.get_db")
    @patch("app.controllers.interview_controller.InterviewController.get_interview")
    def test_get_interview_by_id(self, mock_controller, mock_get_db):
        mock_get_db.return_value = self.mock_db
        mock_controller.return_value = JSONResponse(
            status_code=200,
            content={"success": True, "data": {"_id": self.test_interview_id, "jobRole": "Backend Engineer"}}
        )

        res = self.client.get(f"/api/interviews/{self.test_interview_id}", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])


if __name__ == "__main__":
    unittest.main()
