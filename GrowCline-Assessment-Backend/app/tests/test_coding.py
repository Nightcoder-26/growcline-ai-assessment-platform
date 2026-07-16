"""
Unit Test Suite for CodingService
Tests coding question management, submission payload validation,
and hidden test case evaluation interface.
"""

import unittest
from unittest.mock import patch, MagicMock
from bson import ObjectId

try:
    from services.coding_service import CodingService, STATUS_ACCEPTED, STATUS_WRONG_ANSWER
except ImportError:
    from app.services.coding_service import CodingService, STATUS_ACCEPTED, STATUS_WRONG_ANSWER


class TestCodingService(unittest.TestCase):
    """Test cases for CodingService."""

    @patch("app.config.database.Database.get_db")
    def test_validate_submission_valid_payload(self, mock_get_db: MagicMock) -> None:
        """Test submission payload validation passes with required fields."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        qid = ObjectId()
        mock_db.coding_questions.find_one.return_value = {"_id": qid, "isActive": True}

        payload = {
            "questionId": str(qid),
            "code": "print('Hello World')",
            "language": "python"
        }
        is_valid, msg, clean_data = CodingService.validate_submission(payload)
        self.assertTrue(is_valid)

    @patch("app.config.database.Database.get_db")
    def test_validate_submission_missing_code(self, mock_get_db: MagicMock) -> None:
        """Test submission payload validation fails when source code is missing."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        payload = {
            "questionId": str(ObjectId()),
            "language": "python"
        }
        is_valid, msg, clean_data = CodingService.validate_submission(payload)
        self.assertFalse(is_valid)
        self.assertIn("code", msg.lower())

    @patch("app.config.database.Database.get_db")
    def test_evaluate_submission_wrong_answer(self, mock_get_db: MagicMock) -> None:
        """Test evaluation of submission against hidden test cases."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db

        question_id = str(ObjectId())
        mock_db.coding_questions.find_one.return_value = {
            "_id": ObjectId(question_id),
            "programmingLanguage": "python",
            "timeLimit": 2.0,
            "memoryLimit": 256,
            "marks": 20,
            "isActive": True,
            "hiddenTestCases": [
                {"input": "2 3\n", "output": "5"}
            ]
        }

        mock_engine = MagicMock()
        mock_engine.execute.return_value = {
            "success": True,
            "status": "SUCCESS",
            "output": "4\n",
            "stderr": "",
            "execution_time_ms": 15.0
        }

        with patch.object(CodingService, "get_execution_engine", return_value=mock_engine):
            payload = {
                "questionId": question_id,
                "code": "print(4)",
                "language": "python"
            }
            res = CodingService.evaluate_submission(payload)
            self.assertTrue(res["success"])
            self.assertEqual(res["data"]["status"], STATUS_WRONG_ANSWER)
            self.assertEqual(res["data"]["marks_obtained"], 0)


if __name__ == "__main__":
    unittest.main()
