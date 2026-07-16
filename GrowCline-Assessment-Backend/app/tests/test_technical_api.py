"""
Unit Test Suite for Technical Assessment API endpoints
Tests CRUD, generate, and submit operations under /api/technical.
"""

import unittest
from unittest.mock import patch, MagicMock
from bson import ObjectId
from flask import Flask

try:
    from routes.technical_routes import technical_bp
except ImportError:
    from app.routes.technical_routes import technical_bp


class TestTechnicalAPI(unittest.TestCase):
    """Test suite for /api/technical endpoints."""

    def setUp(self) -> None:
        self.app = Flask(__name__)
        self.app.register_blueprint(technical_bp, url_prefix="/api/technical")
        self.client = self.app.test_client()

        self.mock_db = MagicMock()
        self.mock_col = MagicMock()
        self.mock_db.technical_questions = self.mock_col

    @patch("app.config.database.Database.get_db")
    def test_create_technical_question(self, mock_get_db: MagicMock) -> None:
        mock_get_db.return_value = self.mock_db
        fake_id = ObjectId()
        self.mock_col.insert_one.return_value = MagicMock(inserted_id=fake_id)

        payload = {
            "technology": "Python",
            "question": "Which keyword is used to define a function in Python?",
            "questionType": "MCQ",
            "options": ["function", "define", "def", "func"],
            "correctAnswer": "def",
            "explanation": "The def keyword defines a function.",
            "difficulty": "Easy",
            "marks": 2
        }

        res = self.client.post("/api/technical", json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["question_id"], str(fake_id))

    @patch("app.config.database.Database.get_db")
    def test_submit_technical_assessment(self, mock_get_db: MagicMock) -> None:
        mock_get_db.return_value = self.mock_db
        qid = ObjectId()

        self.mock_col.find_one.return_value = {
            "_id": qid,
            "technology": "Python",
            "question": "Which keyword is used to define a function in Python?",
            "correctAnswer": "def",
            "marks": 2
        }

        payload = {
            "assessmentId": "tech_assessment_1",
            "answers": [
                {
                    "questionId": str(qid),
                    "selectedAnswer": "def"
                }
            ]
        }

        res = self.client.post("/api/technical/submit", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["score"], 2)
        self.assertEqual(data["percentage"], 100)


if __name__ == "__main__":
    unittest.main()
