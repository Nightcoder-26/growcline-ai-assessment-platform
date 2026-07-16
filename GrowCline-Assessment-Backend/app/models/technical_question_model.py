"""
Technical Question Model
Defines document schema and formatting methods for technical_questions collection.
"""

from datetime import datetime, timezone
from bson import ObjectId


class TechnicalQuestion:
    """Technical Question Model"""

    @staticmethod
    def create_question(
        technology,
        question,
        options,
        correct_answer,
        difficulty="Easy",
        category=None,
        marks=1,
        explanation="",
        question_type="MCQ",
        tags=None,
        created_by=None,
    ):
        now = datetime.now(timezone.utc)
        cat = category or technology or "General"
        return {
            "_id": ObjectId(),
            "technology": technology or "General",
            "category": cat,
            "question": question,
            "questionType": question_type or "MCQ",
            "options": options,
            "correctAnswer": correct_answer,
            "correct_answer": correct_answer,
            "difficulty": difficulty or "Easy",
            "marks": int(marks) if marks is not None else 1,
            "explanation": explanation or "",
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

        updated_at = question.get("updatedAt")
        if isinstance(updated_at, datetime):
            updated_at = updated_at.isoformat()

        return {
            "_id": str(question["_id"]),
            "id": str(question["_id"]),
            "technology": question.get("technology", "General"),
            "category": question.get("category", question.get("technology", "General")),
            "question": question.get("question", ""),
            "questionType": question.get("questionType", "MCQ"),
            "options": question.get("options", []),
            "correctAnswer": question.get("correctAnswer", question.get("correct_answer", "")),
            "difficulty": question.get("difficulty", "Easy"),
            "marks": question.get("marks", 1),
            "explanation": question.get("explanation", ""),
            "tags": question.get("tags", []),
            "isActive": question.get("isActive", True),
            "createdAt": created_at,
            "updatedAt": updated_at,
        }