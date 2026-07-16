"""
Unit Test Suite for Assessment Results and Evaluation Reports
Tests formatting and retrieval of stored assessment results.
"""

import unittest
from unittest.mock import patch, MagicMock
from bson import ObjectId

try:
    from models.assessment_result_model import AssessmentResult
except ImportError:
    from app.models.assessment_result_model import AssessmentResult


class TestResultModelAndReporting(unittest.TestCase):
    """Test cases for AssessmentResult creation and serializing."""

    def test_create_result_doc(self) -> None:
        """Test document factory for AssessmentResult."""
        aid = ObjectId()
        uid = ObjectId()

        doc = AssessmentResult.create_result(
            assessment_id=str(aid),
            user_id=str(uid),
            total_score=85.5,
            percentage=85.5,
            status="Passed"
        )
        self.assertEqual(doc["assessmentId"], aid)
        self.assertEqual(doc["userId"], uid)
        self.assertEqual(doc["totalScore"], 85.5)

    def test_response_serializer(self) -> None:
        """Test response serializing of ObjectId to string."""
        doc = AssessmentResult.create_result(
            assessment_id=str(ObjectId()),
            user_id=str(ObjectId()),
            total_score=90.0,
            percentage=90.0,
            status="Passed"
        )
        res = AssessmentResult.response(doc)
        self.assertIsInstance(res["id"], str)
        self.assertEqual(res["totalScore"], 90.0)


if __name__ == "__main__":
    unittest.main()
