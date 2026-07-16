"""
Unit Test Suite for RecommendationService
Tests AI recommendation engine logic based on weak areas, ensuring structured return of
Recommended Topics, Learning Path, Difficulty Level, and Improvement Tips.
"""

import unittest
from unittest.mock import patch, MagicMock
from bson import ObjectId

try:
    from services.recommendation_service import RecommendationService, HeuristicRecommendationEngine
except ImportError:
    from app.services.recommendation_service import RecommendationService, HeuristicRecommendationEngine


class TestRecommendationService(unittest.TestCase):
    """Test cases for RecommendationService."""

    def test_generate_heuristic_recommendations_python(self) -> None:
        """Test rule-based heuristic recommendations for Python weak skill."""
        res = RecommendationService.generate_recommendations(weak_skills=["python"], provider_type="heuristic")
        self.assertTrue(res["success"])
        data = res["data"]
        self.assertIn("recommendedTopics", data)
        self.assertIn("learningPath", data)
        self.assertIn("difficultyLevel", data)
        self.assertIn("improvementTips", data)
        self.assertGreater(len(data["recommendedTopics"]), 0)
        self.assertGreater(len(data["learningPath"]), 0)

    @patch("app.config.database.Database.get_db")
    def test_generate_recommendations_for_user(self, mock_get_db: MagicMock) -> None:
        """Test fetching weak skills from analytics and generating recommendations for a user."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        user_id = str(ObjectId())

        mock_db.analytics.find_one.return_value = {
            "userId": ObjectId(user_id),
            "weakestSkill": "SQL"
        }

        res = RecommendationService.generate_recommendations_for_user(user_id)
        self.assertTrue(res["success"])
        self.assertIn("recommendedTopics", res["data"])


if __name__ == "__main__":
    unittest.main()
