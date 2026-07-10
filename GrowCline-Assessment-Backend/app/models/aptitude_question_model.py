"""
Aptitude Question Model
Defines the document structure and helper methods for aptitude_questions collection.
"""

from datetime import datetime, timezone
from bson import ObjectId


class AptitudeQuestion:
    """Aptitude Question Model"""

    @staticmethod
    def create_question(
        question,
        category,
        difficulty,
        options,
        correct_answer,
        explanation="",
        marks=1,
        question_type="MCQ",
        tags=None,
        created_by=None,
    ):
        now = datetime.now(timezone.utc)
        return {
            "_id": ObjectId(),
            "question": question,
            "category": category,
            "difficulty": difficulty,
            "options": options,
            "correctAnswer": correct_answer,
            "correct_answer": correct_answer,
            "explanation": explanation or "",
            "marks": int(marks) if marks is not None else 1,
            "questionType": question_type or "MCQ",
            "tags": tags if tags else [],
            "isActive": True,
            "createdBy": ObjectId(created_by) if created_by else None,
            "createdAt": now,
            "updatedAt": now,
        }

    @staticmethod
    def response(question):
        if not question:
            return None
        created_at = question.get("createdAt")
        if isinstance(created_at, datetime):
            created_at = created_at.isoformat()

        return {
            "_id": str(question["_id"]),
            "id": str(question["_id"]),
            "question": question.get("question", ""),
            "category": question.get("category", ""),
            "difficulty": question.get("difficulty", "Easy"),
            "options": question.get("options", []),
            "correctAnswer": question.get("correctAnswer", question.get("correct_answer", "")),
            "explanation": question.get("explanation", ""),
            "marks": question.get("marks", 1),
            "questionType": question.get("questionType", "MCQ"),
            "tags": question.get("tags", []),
            "isActive": question.get("isActive", True),
            "createdAt": created_at,
        }