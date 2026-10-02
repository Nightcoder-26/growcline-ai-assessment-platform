"""
Unit Test Suite for Coding Assessment API endpoints
Tests CRUD, generate, run, submit-one, and submit operations under /api/coding.
"""

import unittest
from unittest.mock import patch, MagicMock
from bson import ObjectId
from fastapi.testclient import TestClient

from app import app
from app.middleware.auth_middleware import get_current_user

ADMIN_USER = {
    "_id": ObjectId("507f1f77bcf86cd799439011"),
    "email": "admin@example.com",
    "fullName": "Admin User",
    "role": "admin",
}

CANDIDATE_USER = {
    "_id": ObjectId("507f1f77bcf86cd799439012"),
    "email": "candidate@example.com",
    "fullName": "Candidate User",
    "role": "candidate",
}


class TestCodingAPI(unittest.TestCase):
    """Test suite for /api/coding endpoints."""

    def setUp(self) -> None:
        self.client = TestClient(app)
        self.mock_db = MagicMock()
        self.mock_col = MagicMock()
        self.mock_db.coding_questions = self.mock_col
        self.mock_db.coding_submissions = MagicMock()
        # Default authenticated user is admin
        app.dependency_overrides[get_current_user] = lambda: ADMIN_USER

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    @patch("app.config.database.Database.get_db")
    def test_create_coding_question_returns_201(self, mock_get_db: MagicMock) -> None:
        """Test POST /api/coding returns 201 Created for authenticated admin."""
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
        data = res.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["question_id"], str(fake_id))

    @patch("app.controllers.coding_controller.CodingService.evaluate_submission")
    @patch("app.config.database.Database.get_db")
    def test_submit_coding_assessment(self, mock_get_db: MagicMock, mock_eval: MagicMock) -> None:
        """Test POST /api/coding/submit returns score, percentage, and results."""
        mock_get_db.return_value = self.mock_db
        qid = ObjectId()

        mock_eval.return_value = {
            "success": True,
            "data": {
                "question_id": str(qid),
                "status": "Accepted",
                "marks_obtained": 10.0,
                "max_marks": 10.0,
                "passed_tests": 2,
                "total_tests": 2,
                "percentage": 100.0,
                "test_results": [
                    {"is_hidden": False, "passed": True},
                    {"is_hidden": True, "passed": True},
                ],
            }
        }

        payload = {
            "assessmentId": "coding_assessment_1",
            "answers": [
                {
                    "questionId": str(qid),
                    "code": "def twoSum(nums, target): return [0, 1]",
                    "language": "python"
                }
            ]
        }

        res = self.client.post("/api/coding/submit", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["score"], 10)
        self.assertEqual(data["percentage"], 100)
        self.assertIn("results", data)
        self.assertEqual(len(data["results"]), 1)

    @patch("app.controllers.coding_controller.CodingService.run_sample_cases")
    def test_run_code_sample_cases(self, mock_run_sample: MagicMock) -> None:
        """Test POST /api/coding/run executes candidate code on sample cases."""
        mock_run_sample.return_value = {
            "success": True,
            "status_code": 200,
            "data": {
                "submission_id": "test_sub_123",
                "question_id": str(ObjectId()),
                "status": "Accepted",
                "passed_tests": 1,
                "total_tests": 1,
                "results": [
                    {
                        "input": "2 7 11 15\n9",
                        "expected_output": "0 1",
                        "actual_output": "0 1",
                        "passed": True,
                        "status": "Accepted"
                    }
                ]
            }
        }

        payload = {
            "questionId": str(ObjectId()),
            "code": "nums = input()\ntarget = input()\nprint('0 1')",
            "language": "python"
        }

        res = self.client.post("/api/coding/run", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["status"], "Accepted")
        self.assertEqual(len(data["data"]["results"]), 1)

    @patch("app.controllers.coding_controller.CodingService.evaluate_submission")
    def test_submit_one_problem(self, mock_eval: MagicMock) -> None:
        """Test POST /api/coding/submit-one returns verdict and hidden test counts."""
        qid = ObjectId()
        mock_eval.return_value = {
            "success": True,
            "data": {
                "question_id": str(qid),
                "status": "Accepted",
                "marks_obtained": 10.0,
                "max_marks": 10.0,
                "passed_tests": 3,
                "total_tests": 3,
                "percentage": 100.0,
                "test_results": [
                    {"is_hidden": False, "passed": True, "input": "2 7", "expected_output": "0 1", "actual_output": "0 1"},
                    {"is_hidden": True, "passed": True, "input": "Hidden", "expected_output": "Hidden", "actual_output": "Matched"},
                    {"is_hidden": True, "passed": True, "input": "Hidden", "expected_output": "Hidden", "actual_output": "Matched"},
                ]
            }
        }

        payload = {
            "questionId": str(qid),
            "code": "print('0 1')",
            "language": "python"
        }

        res = self.client.post("/api/coding/submit-one", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["status"], "Accepted")
        self.assertEqual(data["hidden_summary"]["passed"], 2)
        self.assertEqual(data["hidden_summary"]["total"], 2)


if __name__ == "__main__":
    unittest.main()
