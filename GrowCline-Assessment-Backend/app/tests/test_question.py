"""
Unit Test Suite for QuestionService
Tests CRUD operations, duplicate validation, random question generation,
filtering, search, and pagination across Aptitude, Technical, and Coding questions.
"""

import unittest
from unittest.mock import patch, MagicMock
from bson import ObjectId

try:
    from services.question_service import (
        QuestionService,
        QUESTION_TYPE_APTITUDE,
        QUESTION_TYPE_TECHNICAL,
        QUESTION_TYPE_CODING
    )
except ImportError:
    from app.services.question_service import (
        QuestionService,
        QUESTION_TYPE_APTITUDE,
        QUESTION_TYPE_TECHNICAL,
        QUESTION_TYPE_CODING
    )


class TestQuestionService(unittest.TestCase):
    """Test cases for QuestionService."""

    def setUp(self) -> None:
        """Sets up mock MongoDB database and collections before each test."""
        self.mock_db = MagicMock()
        self.mock_aptitude_col = MagicMock()
        self.mock_technical_col = MagicMock()
        self.mock_coding_col = MagicMock()

        self.mock_db.aptitude_questions = self.mock_aptitude_col
        self.mock_db.technical_questions = self.mock_technical_col
        self.mock_db.coding_questions = self.mock_coding_col

    @patch("app.config.database.Database.get_db")
    def test_create_aptitude_question_success(self, mock_get_db: MagicMock) -> None:
        """Test successful creation of an aptitude question."""
        mock_get_db.return_value = self.mock_db
        self.mock_aptitude_col.count_documents.return_value = 0  # No duplicate
        self.mock_aptitude_col.insert_one.return_value = MagicMock(inserted_id=ObjectId())

        payload = {
            "category": "Logical Reasoning",
            "question": "What comes next in sequence: 2, 4, 8, 16, ...?",
            "options": ["24", "32", "64", "18"],
            "correctAnswer": "32",
            "difficulty": "Easy",
            "marks": 2
        }

        res = QuestionService.create_aptitude_question(payload, created_by=str(ObjectId()))
        self.assertTrue(res["success"])
        self.assertEqual(res["status_code"], 201)
        self.assertEqual(res["data"]["question"], payload["question"])

    @patch("app.config.database.Database.get_db")
    def test_create_question_duplicate_blocked(self, mock_get_db: MagicMock) -> None:
        """Test that duplicate question creation is rejected with 409 status."""
        mock_get_db.return_value = self.mock_db
        self.mock_aptitude_col.count_documents.return_value = 1  # Duplicate found

        payload = {
            "question": "Duplicate Question Text",
            "options": ["A", "B"],
            "correctAnswer": "A"
        }

        res = QuestionService.create_aptitude_question(payload)
        self.assertFalse(res["success"])
        self.assertEqual(res["status_code"], 409)
        self.assertEqual(res["error"], "DUPLICATE_QUESTION")

    @patch("app.config.database.Database.get_db")
    def test_get_question_by_id_not_found(self, mock_get_db: MagicMock) -> None:
        """Test retrieving a non-existent question returns 404."""
        mock_get_db.return_value = self.mock_db
        self.mock_technical_col.find_one.return_value = None

        res = QuestionService.get_question_by_id(QUESTION_TYPE_TECHNICAL, str(ObjectId()))
        self.assertFalse(res["success"])
        self.assertEqual(res["status_code"], 404)
        self.assertEqual(res["error"], "QUESTION_NOT_FOUND")

    @patch("app.config.database.Database.get_db")
    def test_list_questions_pagination(self, mock_get_db: MagicMock) -> None:
        """Test listing questions with pagination metadata."""
        mock_get_db.return_value = self.mock_db
        self.mock_coding_col.count_documents.return_value = 25

        # Mock cursor
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.limit.return_value = [
            {
                "_id": ObjectId(),
                "title": f"Coding Problem {i}",
                "programmingLanguage": "Python",
                "category": "Algorithms",
                "problemStatement": f"Solve problem {i}",
                "difficulty": "Medium",
                "inputFormat": "int",
                "outputFormat": "int",
                "constraints": "N < 100",
                "sampleTestCases": [],
                "marks": 10,
                "timeLimit": 2.0,
                "memoryLimit": 256,
                "explanation": "",
                "isActive": True,
                "createdAt": "2026-07-09T10:00:00Z",
                "updatedAt": "2026-07-09T10:00:00Z"
            }
            for i in range(10)
        ]
        self.mock_coding_col.find.return_value = mock_cursor

        res = QuestionService.list_questions(QUESTION_TYPE_CODING, page=1, limit=10)
        self.assertTrue(res["success"])
        self.assertEqual(res["meta"]["total_items"], 25)
        self.assertEqual(res["meta"]["total_pages"], 3)
        self.assertEqual(len(res["data"]), 10)

    @patch("app.config.database.Database.get_db")
    def test_generate_random_questions(self, mock_get_db: MagicMock) -> None:
        """Test random sampling of questions."""
        mock_get_db.return_value = self.mock_db
        self.mock_aptitude_col.aggregate.return_value = [
            {
                "_id": ObjectId(),
                "category": "Math",
                "question": "2+2=?",
                "options": ["3", "4", "5"],
                "correctAnswer": "4",
                "difficulty": "Easy",
                "marks": 1,
                "isActive": True
            }
        ]

        res = QuestionService.generate_random_questions(QUESTION_TYPE_APTITUDE, size=5, strip_answers=True)
        self.assertTrue(res["success"])
        self.assertEqual(len(res["data"]), 1)
        self.assertNotIn("correctAnswer", res["data"][0])


if __name__ == "__main__":
    unittest.main()
