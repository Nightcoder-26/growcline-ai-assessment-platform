"""
Unit Test Suite for ScoringService
Tests automated evaluation of aptitude, technical, and coding sections,
percentage, pass/fail thresholds, rank calculation, and category profile aggregation.
"""

import unittest
from unittest.mock import patch, MagicMock
from bson import ObjectId

try:
    from services.scoring_service import ScoringService, STATUS_PASSED, STATUS_FAILED
except ImportError:
    from app.services.scoring_service import ScoringService, STATUS_PASSED, STATUS_FAILED


class TestScoringService(unittest.TestCase):
    """Test cases for ScoringService."""

    def test_calculate_aptitude_score_mcq(self) -> None:
        """Test calculation of aptitude score from candidate answers against expected questions."""
        qid1 = str(ObjectId())
        qid2 = str(ObjectId())

        submitted_answers = [
            {"questionId": qid1, "selectedOption": "Option A"},
            {"questionId": qid2, "selectedOption": "Option B"}
        ]

        mock_db = MagicMock()
        mock_db.aptitude_questions.find.return_value = [
            {
                "_id": ObjectId(qid1),
                "question": "Q1",
                "correctAnswer": "Option A",
                "marks": 2,
                "category": "Logical"
            },
            {
                "_id": ObjectId(qid2),
                "question": "Q2",
                "correctAnswer": "Option C",
                "marks": 2,
                "category": "Verbal"
            }
        ]

        with patch("app.config.database.Database.get_db", return_value=mock_db):
            res = ScoringService.calculate_aptitude_score(submitted_answers, [qid1, qid2])
            self.assertEqual(res["score"], 2)
            self.assertEqual(res["max_marks"], 4)
            self.assertEqual(res["correct_count"], 1)
            self.assertEqual(res["wrong_count"], 1)
            self.assertEqual(res["category_breakdown"]["Logical"]["correct"], 1)
            self.assertEqual(res["category_breakdown"]["Verbal"]["correct"], 0)

    def test_calculate_category_wise_profile(self) -> None:
        """Test identifying strongest and weakest skills across categories."""
        apt_cat = {
            "Logical Reasoning": {"correct": 5, "questions": 5, "obtained": 10.0, "total": 10.0}
        }
        tech_cat = {
            "Python": {"correct": 4, "questions": 5, "obtained": 8.0, "total": 10.0},
            "SQL": {"correct": 1, "questions": 5, "obtained": 2.0, "total": 10.0}
        }
        cod_cat = {
            "Algorithms": {"correct": 3, "questions": 5, "obtained": 30.0, "total": 50.0}
        }

        profile, strongest, weakest = ScoringService.calculate_category_wise_score(
            apt_cat, tech_cat, cod_cat
        )
        self.assertEqual(strongest, "Logical Reasoning")
        self.assertEqual(weakest, "SQL")
        self.assertIn("Python", profile)

    @patch("app.config.database.Database.get_db")
    def test_calculate_and_save_result_passed(self, mock_get_db: MagicMock) -> None:
        """Test end-to-end evaluation resulting in Pass status."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db

        assessment_id = str(ObjectId())
        user_id = str(ObjectId())

        mock_db.assessments.find_one.return_value = {
            "_id": ObjectId(assessment_id),
            "userId": ObjectId(user_id),
            "totalMarks": 100,
            "passingPercentage": 40,
            "aptitudeQuestions": [],
            "technicalQuestions": [],
            "codingQuestions": []
        }

        mock_db.assessment_results.insert_one.return_value = MagicMock(inserted_id=ObjectId())

        payload = {
            "aptitudeAnswers": [],
            "technicalAnswers": [],
            "codingSubmissions": []
        }

        with patch.object(ScoringService, "calculate_aptitude_score", return_value={
            "score": 50, "max_marks": 50, "correct_count": 5, "wrong_count": 0,
            "unanswered_count": 0, "total_questions": 5, "category_breakdown": {}, "detailed_results": []
        }), patch.object(ScoringService, "calculate_technical_score", return_value={
            "score": 30, "max_marks": 50, "correct_count": 3, "wrong_count": 2,
            "unanswered_count": 0, "total_questions": 5, "category_breakdown": {}, "detailed_results": []
        }), patch.object(ScoringService, "calculate_coding_score", return_value={
            "score": 0, "max_marks": 0, "correct_count": 0, "wrong_count": 0,
            "unanswered_count": 0, "total_questions": 0, "category_breakdown": {}, "detailed_results": []
        }):
            res = ScoringService.calculate_and_save_result(assessment_id, user_id, payload)
            self.assertTrue(res["success"])
            self.assertEqual(res["data"]["passStatus"], STATUS_PASSED)
            self.assertEqual(res["data"]["totalScore"], 80)
            self.assertEqual(res["data"]["percentage"], 80.0)


if __name__ == "__main__":
    unittest.main()
