from datetime import datetime
from bson import ObjectId


class TechnicalQuestion:
    @staticmethod
    def create_question(
        technology,
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

            "technology": technology,
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

            "technology": question["technology"],
            "category": question["category"],

            "question": question["question"],

            "questionType": question["questionType"],

            "options": question["options"],

            "correctAnswer": question["correctAnswer"],

            "difficulty": question["difficulty"],

            "marks": question["marks"],

            "explanation": question["explanation"],

            "tags": question.get("tags", []),

            "isActive": question["isActive"],

            "createdBy": (
                str(question["createdBy"])
                if question.get("createdBy")
                else None
            ),

            "createdAt": question["createdAt"],
            "updatedAt": question["updatedAt"],
        }