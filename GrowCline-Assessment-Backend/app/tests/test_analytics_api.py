"""
Unit Test Suite for Analytics API endpoints
Tests POST and GET on /api/analytics/dashboard/<user_id>.
"""

import unittest
from unittest.mock import patch, MagicMock
from bson import ObjectId
from fastapi.testclient import TestClient

from app import app


class TestAnalyticsAPI(unittest.TestCase):
    """Test suite for /api/analytics endpoints."""

    def setUp(self) -> None:
        self.client = TestClient(app)
        self.mock_db = MagicMock()
        self.mock_col = MagicMock()
        self.mock_db.analytics = self.mock_col
        self.mock_db.dashboard_analytics = self.mock_col

    @patch("app.config.database.Database.get_db")
    def test_post_user_dashboard_analytics(self, mock_get_db: MagicMock) -> None:
        """Test POST /api/analytics/dashboard/<user_id> returns 200 and saves analytics."""
        mock_get_db.return_value = self.mock_db
        fake_id = ObjectId()
        self.mock_col.insert_one.return_value = MagicMock(inserted_id=fake_id)

        user_id = "6a51063813a24c803f2d1246"
        payload = {
            "userId": user_id,
            "assessmentResultId": "6a5110ec9314939ae66d8e71",
            "strongestSkill": "Technical",
            "weakestSkill": "Coding",
            "averageScore": 88,
            "totalAssessments": 5,
            "improvementPercentage": 12,
            "recommendation": "Practice more coding challenges."
        }

        res = self.client.post(f"/api/analytics/dashboard/{user_id}", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["strongestSkill"], "Technical")


if __name__ == "__main__":
    unittest.main()
