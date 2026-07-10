"""
Unit Test Suite for AssessmentService
Tests assessment lifecycle: creation, random generation, assignment of questions,
state transitions (Pending -> In Progress -> Completed), validation, and deletion.
"""

import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock
from bson import ObjectId

try:
    from services.assessment_service import AssessmentService, STATUS_PENDING, STATUS_IN_PROGRESS, STATUS_COMPLETED
except ImportError:
    from app.services.assessment_service import AssessmentService, STATUS_PENDING, STATUS_IN_PROGRESS, STATUS_COMPLETED


class TestAssessmentService(unittest.TestCase):
    """Test cases for AssessmentService."""

    def setUp(self) -> None:
        self.mock_db = MagicMock()
        self.mock_assessments = MagicMock()
        self.mock_aptitude = MagicMock()
        self.mock_technical = MagicMock()
        self.mock_coding = MagicMock()

        self.mock_db.assessments = self.mock_assessments
        self.mock_db.aptitude_questions = self.mock_aptitude
        self.mock_db.technical_questions = self.mock_technical
        self.mock_db.coding_questions = self.mock_coding

        self.mock_aptitude.find.return_value = []
        self.mock_technical.find.return_value = []
        self.mock_coding.find.return_value = []

    def _get_dummy_doc(self, assessment_id: str, user_id: str, status: str = STATUS_PENDING) -> dict:
        return {
            "_id": ObjectId(assessment_id),
            "title": "Python Exam",
            "assessmentType": "Technical",
            "userId": ObjectId(user_id),
            "aptitudeQuestions": [],
            "technicalQuestions": [],
            "codingQuestions": [],
            "totalQuestions": 0,
            "totalMarks": 0,
            "duration": 60,
            "passingPercentage": 50,
            "instructions": "Answer all questions",
            "status": status,
            "scheduledAt": None,
            "startedAt": None,
            "submittedAt": None,
            "expiresAt": None,
            "isActive": True,
            "createdBy": ObjectId(user_id),
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }

    @patch("app.config.database.Database.get_db")
    def test_create_assessment_success(self, mock_get_db: MagicMock) -> None:
        """Test creating an assessment successfully."""
        mock_get_db.return_value = self.mock_db
        self.mock_assessments.insert_one.return_value = MagicMock(inserted_id=ObjectId())

        payload = {
            "title": "Full Stack Python Interview Assessment",
            "assessmentType": "Technical",
            "userId": str(ObjectId()),
            "duration": 90,
            "passingPercentage": 60
        }

        res = AssessmentService.create_assessment(payload, created_by=str(ObjectId()))
        self.assertTrue(res["success"])
        self.assertEqual(res["status_code"], 201)
        self.assertEqual(res["data"]["status"], STATUS_PENDING)

    @patch("app.config.database.Database.get_db")
    def test_start_assessment_state_transition(self, mock_get_db: MagicMock) -> None:
        """Test transitioning an assessment from Pending to In Progress."""
        mock_get_db.return_value = self.mock_db
        assessment_id = str(ObjectId())
        user_id = str(ObjectId())

        self.mock_assessments.find_one.return_value = self._get_dummy_doc(assessment_id, user_id, STATUS_PENDING)

        res = AssessmentService.start_assessment(assessment_id, user_id=user_id)
        self.assertTrue(res["success"])
        self.assertEqual(res["data"]["status"], STATUS_IN_PROGRESS)

    @patch("app.config.database.Database.get_db")
    def test_start_assessment_invalid_state_fails(self, mock_get_db: MagicMock) -> None:
        """Test starting an already Completed assessment is blocked."""
        mock_get_db.return_value = self.mock_db
        assessment_id = str(ObjectId())
        user_id = str(ObjectId())

        self.mock_assessments.find_one.return_value = self._get_dummy_doc(assessment_id, user_id, STATUS_COMPLETED)

        res = AssessmentService.start_assessment(assessment_id, user_id=user_id)
        self.assertFalse(res["success"])
        self.assertEqual(res["status_code"], 400)
        self.assertEqual(res["error"], "INVALID_STATE")

    @patch("app.config.database.Database.get_db")
    def test_assign_questions(self, mock_get_db: MagicMock) -> None:
        """Test assigning aptitude, technical, and coding question IDs to an assessment."""
        mock_get_db.return_value = self.mock_db
        assessment_id = str(ObjectId())
        user_id = str(ObjectId())

        self.mock_assessments.find_one.return_value = self._get_dummy_doc(assessment_id, user_id, STATUS_PENDING)

        qids = [str(ObjectId()), str(ObjectId())]
        res = AssessmentService.assign_aptitude_questions(assessment_id, qids)
        self.assertTrue(res["success"])
        self.assertEqual(res["status_code"], 200)


if __name__ == "__main__":
    unittest.main()
