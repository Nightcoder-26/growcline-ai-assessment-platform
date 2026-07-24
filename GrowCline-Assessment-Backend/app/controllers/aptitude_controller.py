"""
Aptitude Controller Module
Handles full CRUD, random test generation, and evaluation for aptitude questions.
"""

from datetime import datetime, timezone
from bson import ObjectId
from typing import Optional

from app.config.database import Database
from app.models.aptitude_question_model import AptitudeQuestion


class AptitudeController:
    """Aptitude Question Controller"""

    @staticmethod
    def create_question(data: dict) -> tuple[dict, int]:
        """
        POST /api/aptitude (or /api/aptitude/questions)
        Creates a new aptitude question document.
        """
        try:
            question_text = data.get("question")
            category = data.get("category")
            difficulty = data.get("difficulty")
            options = data.get("options")
            correct_answer = data.get("correctAnswer", data.get("correct_answer"))
            explanation = data.get("explanation", "")
            marks = data.get("marks", 1)
            question_type = data.get("questionType", "MCQ")
            tags = data.get("tags", [])

            if not question_text or not category or not difficulty or not options or correct_answer is None:
                return {
                    "success": False,
                    "message": "Required fields missing: question, category, difficulty, options, and correctAnswer are required."
                }, 400

            if not isinstance(options, list) or len(options) < 2:
                return {
                    "success": False,
                    "message": "Options must be a list containing at least 2 items."
                }, 400

            question_doc = AptitudeQuestion.create_question(
                question=question_text,
                category=category,
                difficulty=difficulty,
                options=options,
                correct_answer=correct_answer,
                explanation=explanation,
                marks=marks,
                question_type=question_type,
                tags=tags
            )

            db = Database.get_db()
            result = db.aptitude_questions.insert_one(question_doc)

            return {
                "success": True,
                "message": "Question created successfully.",
                "question_id": str(result.inserted_id),
                "data": AptitudeQuestion.response(question_doc)
            }, 201

        except Exception as error:
            return {
                "success": False,
                "message": str(error)
            }, 500

    @staticmethod
    def get_all_questions() -> tuple[dict, int]:
        """
        GET /api/aptitude (or /api/aptitude/questions)
        Retrieves all aptitude questions.
        """
        try:
            db = Database.get_db()
            questions_cursor = db.aptitude_questions.find()

            questions = [AptitudeQuestion.response(q) for q in questions_cursor if q]

            return {
                "success": True,
                "count": len(questions),
                "data": questions
            }, 200

        except Exception as error:
            return {
                "success": False,
                "message": str(error)
            }, 500

    @staticmethod
    def get_question_by_id(question_id: str) -> tuple[dict, int]:
        """
        GET /api/aptitude/<question_id>
        Retrieves a specific aptitude question by its ID.
        """
        try:
            if not ObjectId.is_valid(question_id):
                return {
                    "success": False,
                    "message": "Invalid question ID format."
                }, 400

            db = Database.get_db()
            question = db.aptitude_questions.find_one({"_id": ObjectId(question_id)})

            if not question:
                return {
                    "success": False,
                    "message": "Question not found."
                }, 404

            return {
                "success": True,
                "data": AptitudeQuestion.response(question)
            }, 200

        except Exception as error:
            return {
                "success": False,
                "message": str(error)
            }, 500

    @staticmethod
    def update_question(question_id: str, data: dict) -> tuple[dict, int]:
        """
        PUT /api/aptitude/<question_id>
        Updates an existing aptitude question.
        """
        try:
            if not ObjectId.is_valid(question_id):
                return {
                    "success": False,
                    "message": "Invalid question ID format."
                }, 400

            if not data:
                return {
                    "success": False,
                    "message": "No update payload provided."
                }, 400

            update_fields = {}
            if "question" in data:
                update_fields["question"] = data["question"]
            if "category" in data:
                update_fields["category"] = data["category"]
            if "difficulty" in data:
                update_fields["difficulty"] = data["difficulty"]
            if "options" in data:
                update_fields["options"] = data["options"]
            if "correctAnswer" in data or "correct_answer" in data:
                correct = data.get("correctAnswer", data.get("correct_answer"))
                update_fields["correctAnswer"] = correct
                update_fields["correct_answer"] = correct
            if "explanation" in data:
                update_fields["explanation"] = data["explanation"]
            if "marks" in data:
                update_fields["marks"] = int(data["marks"])
            if "isActive" in data:
                update_fields["isActive"] = bool(data["isActive"])

            update_fields["updatedAt"] = datetime.now(timezone.utc)

            db = Database.get_db()
            result = db.aptitude_questions.update_one(
                {"_id": ObjectId(question_id)},
                {"$set": update_fields}
            )

            if result.matched_count == 0:
                return {
                    "success": False,
                    "message": "Question not found."
                }, 404

            updated_doc = db.aptitude_questions.find_one({"_id": ObjectId(question_id)})

            return {
                "success": True,
                "message": "Question updated successfully.",
                "data": AptitudeQuestion.response(updated_doc)
            }, 200

        except Exception as error:
            return {
                "success": False,
                "message": str(error)
            }, 500

    @staticmethod
    def delete_question(question_id: str) -> tuple[dict, int]:
        """
        DELETE /api/aptitude/<question_id>
        Deletes an aptitude question by ID.
        """
        try:
            if not ObjectId.is_valid(question_id):
                return {
                    "success": False,
                    "message": "Invalid question ID format."
                }, 400

            db = Database.get_db()
            result = db.aptitude_questions.delete_one({"_id": ObjectId(question_id)})

            if result.deleted_count == 0:
                return {
                    "success": False,
                    "message": "Question not found."
                }, 404

            return {
                "success": True,
                "message": "Question deleted successfully."
            }, 200

        except Exception as error:
            return {
                "success": False,
                "message": str(error)
            }, 500

    @staticmethod
    def generate_assessment(data: dict) -> tuple[dict, int]:
        """
        POST /api/aptitude/generate
        Randomly samples questions from MongoDB based on difficulty and size.
        """
        try:
            num_questions = int(data.get("numberOfQuestions", data.get("total_questions", 10)))
            difficulty = data.get("difficulty")

            match_stage = {"isActive": True}
            if difficulty:
                match_stage["difficulty"] = difficulty

            pipeline = [
                {"$match": match_stage},
                {"$sample": {"size": max(1, num_questions)}}
            ]

            db = Database.get_db()
            sampled_docs = list(db.aptitude_questions.aggregate(pipeline))

            # If fewer found with specific difficulty, fallback to any active question
            if len(sampled_docs) < num_questions and difficulty:
                fallback_pipeline = [
                    {"$match": {"isActive": True}},
                    {"$sample": {"size": max(1, num_questions)}}
                ]
                sampled_docs = list(db.aptitude_questions.aggregate(fallback_pipeline))

            formatted_questions = []
            for doc in sampled_docs:
                item = AptitudeQuestion.response(doc)
                if item:
                    item.pop("correctAnswer", None)
                    formatted_questions.append(item)

            return {
                "success": True,
                "count": len(formatted_questions),
                "data": formatted_questions
            }, 200

        except Exception as error:
            return {
                "success": False,
                "message": str(error)
            }, 500

    @staticmethod
    def submit_assessment(data: dict) -> tuple[dict, int]:
        """
        POST /api/aptitude/submit
        Evaluates candidate answers and calculates score & percentage.
        """
        try:
            answers = data.get("answers", [])

            if not isinstance(answers, list):
                return {
                    "success": False,
                    "message": "Answers must be a list of user responses."
                }, 400

            db = Database.get_db()
            score = 0
            total_possible_marks = 0

            for ans in answers:
                question_id = ans.get("questionId", ans.get("question_id"))
                selected_answer = ans.get("selectedAnswer", ans.get("selected_option"))

                if not question_id or not ObjectId.is_valid(question_id):
                    continue

                q_doc = db.aptitude_questions.find_one({"_id": ObjectId(question_id)})
                if not q_doc:
                    continue

                q_marks = q_doc.get("marks", 1)
                total_possible_marks += q_marks

                correct = q_doc.get("correctAnswer", q_doc.get("correct_answer"))
                if str(correct).strip() == str(selected_answer).strip():
                    score += q_marks

            if total_possible_marks > 0:
                percentage = round((score / total_possible_marks) * 100)
            else:
                percentage = 0

            return {
                "success": True,
                "score": score,
                "percentage": percentage
            }, 200

        except Exception as error:
            return {
                "success": False,
                "message": str(error)
            }, 500