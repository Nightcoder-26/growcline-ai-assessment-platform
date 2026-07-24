"""
Unit Test Suite for Aptitude Assessment API endpoints
Tests CRUD, generate, and submit operations under /api/aptitude.
"""

import unittest
from unittest.mock import patch, MagicMock
from bson import ObjectId
from fastapi.testclient import TestClient

from app import app


class TestAptitudeAPI(unittest.TestCase):
    """Test suite for /api/aptitude endpoints."""

    def setUp(self) -> None:
        self.client = TestClient(app)
        self.mock_db = MagicMock()
        self.mock_col = MagicMock()
        self.mock_db.aptitude_questions = self.mock_col

    @patch("app.config.database.Database.get_db")
    def test_create_question(self, mock_get_db: MagicMock) -> None:
        mock_get_db.return_value = self.mock_db
        fake_id = ObjectId()
        self.mock_col.insert_one.return_value = MagicMock(inserted_id=fake_id)

        payload = {
            "question": "What is 15 + 25?",
            "category": "Quantitative Aptitude",
            "difficulty": "Easy",
            "options": ["35", "40", "45", "50"],
            "correctAnswer": "40",
            "explanation": "15 + 25 = 40",
            "marks": 2
        }

        res = self.client.post("/api/aptitude", json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["question_id"], str(fake_id))

    @patch("app.config.database.Database.get_db")
    def test_submit_assessment(self, mock_get_db: MagicMock) -> None:
        mock_get_db.return_value = self.mock_db
        qid = ObjectId()

        self.mock_col.find_one.return_value = {
            "_id": qid,
            "question": "What is 15 + 25?",
            "correctAnswer": "40",
            "marks": 2
        }

        payload = {
            "assessmentId": "sample_assessment",
            "answers": [
                {
                    "questionId": str(qid),
                    "selectedAnswer": "40"
                }
            ]
        }

        res = self.client.post("/api/aptitude/submit", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["score"], 2)
        self.assertEqual(data["percentage"], 100)


if __name__ == "__main__":
    unittest.main()
