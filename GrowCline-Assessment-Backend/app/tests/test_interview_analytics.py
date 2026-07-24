"""
Unit and integration tests for interview analytics and reporting calculations.
"""

import unittest
from unittest.mock import patch, MagicMock
from bson import ObjectId
from fastapi.testclient import TestClient
from fastapi.responses import JSONResponse

from app import app
from app.utils.jwt_utils import generate_token


class TestInterviewAnalyticsAPI(unittest.TestCase):
    """Test suite for interview analytics API endpoints."""

    def setUp(self):
        self.client = TestClient(app)
        self.mock_db = MagicMock()
        self.test_user_id = str(ObjectId())
        self.test_interview_id = str(ObjectId())
        self.auth_token = generate_token({"id": self.test_user_id, "role": "candidate"})
        self.headers = {"Authorization": f"Bearer {self.auth_token}"}

    @patch("app.routes.interview_analytics_routes.Database.get_db")
    @patch("app.controllers.interview_analytics_controller.InterviewAnalyticsController.get_analytics")
    def test_get_analytics_report(self, mock_controller, mock_get_db):
        mock_get_db.return_value = self.mock_db
        mock_controller.return_value = JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": {
                    "interviewId": self.test_interview_id,
                    "overallScore": 85.5,
                    "summary": "Strong performance"
                }
            }
        )

        res = self.client.get(f"/api/analytics/interview/{self.test_interview_id}", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["overallScore"], 85.5)


if __name__ == "__main__":
    unittest.main()
