"""
Unit Test Suite for Coding Assessment API endpoints
Tests CRUD, generate, and submit operations under /api/coding.
"""

import unittest
from unittest.mock import patch, MagicMock
from bson import ObjectId
from flask import Flask

try:
    from routes.coding_routes import coding_bp
except ImportError:
    from app.routes.coding_routes import coding_bp


class TestCodingAPI(unittest.TestCase):
    """Test suite for /api/coding endpoints."""

    def setUp(self) -> None:
        self.app = Flask(__name__)
        self.app.register_blueprint(coding_bp, url_prefix="/api/coding")
        self.client = self.app.test_client()

        self.mock_db = MagicMock()
        self.mock_col = MagicMock()
        self.mock_db.coding_questions = self.mock_col

    @patch("app.config.database.Database.get_db")
    def test_create_coding_question_returns_201(self, mock_get_db: MagicMock) -> None:
        """Test POST /api/coding returns 201 Created instead of 404."""
        mock_get_db.return_value = self.mock_db
        fake_id = ObjectId()
        self.mock_col.insert_one.return_value = MagicMock(inserted_id=fake_id)

        payload = {
            "title": "Two Sum",
            "programmingLanguage": "Python",
            "difficulty": "Easy",
            "problemStatement": "Find two numbers whose sum equals target.",
            "inputFormat": "nums,target",
            "outputFormat": "indices",
            "constraints": "2 <= n <= 1000",
            "sampleInput": "[2,7,11,15],9",
            "sampleOutput": "[0,1]",
            "testCases": [
                {"input": "[2,7,11,15],9", "output": "[0,1]"}
            ],
            "hiddenTestCases": [
                {"input": "[3,2,4],6", "output": "[1,2]"}
            ],
            "marks": 10
        }

        res = self.client.post("/api/coding", json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["question_id"], str(fake_id))

    @patch("app.config.database.Database.get_db")
    def test_submit_coding_assessment(self, mock_get_db: MagicMock) -> None:
        """Test POST /api/coding/submit returns score and percentage."""
        mock_get_db.return_value = self.mock_db
        qid = ObjectId()

        self.mock_col.find_one.return_value = {
            "_id": qid,
            "title": "Two Sum",
            "marks": 10
        }

        payload = {
            "assessmentId": "coding_assessment_1",
            "answers": [
                {
                    "questionId": str(qid),
                    "code": "def twoSum(nums, target): return [0, 1]"
                }
            ]
        }

        res = self.client.post("/api/coding/submit", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["score"], 10)
        self.assertEqual(data["percentage"], 100)


if __name__ == "__main__":
    unittest.main()
