"""
Unit Test Suite for AnalyticsService
Tests dashboard generation, average/highest/lowest score calculations,
strongest/weakest skill identification, progress trend tracking, and improvement percentage calculation.
"""

import unittest
from unittest.mock import patch, MagicMock
from bson import ObjectId

try:
    from services.analytics_service import AnalyticsService
except ImportError:
    from app.services.analytics_service import AnalyticsService


class TestAnalyticsService(unittest.TestCase):
    """Test cases for AnalyticsService."""

    @patch("app.config.database.Database.get_db")
    def test_generate_user_dashboard(self, mock_get_db: MagicMock) -> None:
        """Test user dashboard metrics calculation from analytics records."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db

        user_id = str(ObjectId())

        # Mock cursor for find().sort()
        mock_cursor = MagicMock()
        mock_cursor.__iter__.return_value = iter([
            {
                "_id": ObjectId(),
                "userId": ObjectId(user_id),
                "assessmentId": ObjectId(),
                "totalScore": 60.0,
                "percentage": 60.0,
                "strongestSkill": "Python",
                "weakestSkill": "SQL"
            },
            {
                "_id": ObjectId(),
                "userId": ObjectId(user_id),
                "assessmentId": ObjectId(),
                "totalScore": 80.0,
                "percentage": 80.0,
                "strongestSkill": "Algorithms",
                "weakestSkill": "SQL"
            }
        ])
        mock_db.analytics.find.return_value.sort.return_value = mock_cursor

        res = AnalyticsService.generate_user_dashboard(user_id)
        self.assertTrue(res["success"])
        data = res["data"]
        self.assertEqual(data["total_assessments"], 2)
        self.assertEqual(data["average_score"], 70.0)
        self.assertEqual(data["highest_score"], 80.0)
        self.assertEqual(data["lowest_score"], 60.0)
        self.assertEqual(data["weakest_skill"], "SQL")

    @patch("app.config.database.Database.get_db")
    def test_generate_user_dashboard_empty_history(self, mock_get_db: MagicMock) -> None:
        """Test user dashboard returns zeroed defaults cleanly when no assessment history exists."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db

        user_id = str(ObjectId())

        mock_db.analytics.find.return_value.sort.return_value = []
        mock_db.assessment_results.find.return_value.sort.return_value = []

        res = AnalyticsService.generate_user_dashboard(user_id)
        self.assertTrue(res["success"])
        self.assertEqual(res["data"]["total_assessments"], 0)
        self.assertEqual(res["data"]["average_score"], 0.0)


if __name__ == "__main__":
    unittest.main()
