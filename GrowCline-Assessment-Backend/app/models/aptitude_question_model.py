from datetime import datetime
from bson import ObjectId


class AptitudeQuestion:
    @staticmethod
    def create_question(
        category,
        question,
        options,
        correct_answer,
        difficulty,
        marks=1,
        explanation="",
        question_type="MCQ",
        tags=None,
        created_by=None,
    ):
        return {
            "_id": ObjectId(),

            "category": category,

            "question": question,

            "questionType": question_type,

            "options": options,

            "correctAnswer": correct_answer,

            "difficulty": difficulty,

            "marks": marks,

            "explanation": explanation,

            "tags": tags if tags else [],

            "isActive": True,

            "createdBy": (
                ObjectId(created_by)
                if created_by
                else None
            ),

            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
        }

    @staticmethod
    def response(question):
        return {
            "id": str(question["_id"]),

            "category": question.get("category"),

            "question": question.get("question"),

            "questionType": question.get("questionType", "MCQ"),

            "options": question.get("options", []),

            "correctAnswer": question.get("correctAnswer"),

            "difficulty": question.get("difficulty"),

            "marks": question.get("marks", 1),

            "explanation": question.get("explanation", ""),

            "tags": question.get("tags", []),

            "isActive": question.get("isActive", True),

            "createdBy": (
                str(question["createdBy"])
                if question.get("createdBy")
                else None
            ),

            "createdAt": question.get("createdAt"),
            "updatedAt": question.get("updatedAt"),
        }