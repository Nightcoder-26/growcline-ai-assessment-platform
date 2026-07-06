"""
Aptitude Controller
Handles CRUD operations for aptitude questions.
"""

from flask import request, jsonify
from bson import ObjectId
try:
    from config.database import Database
except ImportError:
    from app.config.database import Database


class AptitudeController:
    """Aptitude Question Controller"""

    @staticmethod
    def create_question():
        try:
            db = Database.get_db()

            data = request.get_json()

            question = {
                "question": data.get("question"),
                "options": data.get("options"),
                "correct_answer": data.get("correct_answer"),
                "difficulty": data.get("difficulty", "Easy"),
                "category": data.get("category"),
                "marks": data.get("marks", 1),
                "is_active": True,
            }

            result = db.aptitude_questions.insert_one(question)

            return jsonify({
                "success": True,
                "message": "Question created successfully.",
                "question_id": str(result.inserted_id)
            }), 201

        except Exception as error:
            return jsonify({
                "success": False,
                "message": str(error)
            }), 500

    @staticmethod
    def get_questions():
        try:
            db = Database.get_db()

            questions = list(
                db.aptitude_questions.find()
            )

            for question in questions:
                question["_id"] = str(question["_id"])

            return jsonify({
                "success": True,
                "count": len(questions),
                "data": questions
            }), 200

        except Exception as error:
            return jsonify({
                "success": False,
                "message": str(error)
            }), 500

    @staticmethod
    def get_question(question_id):
        try:
            db = Database.get_db()

            question = db.aptitude_questions.find_one({
                "_id": ObjectId(question_id)
            })

            if not question:
                return jsonify({
                    "success": False,
                    "message": "Question not found."
                }), 404

            question["_id"] = str(question["_id"])

            return jsonify({
                "success": True,
                "data": question
            }), 200

        except Exception as error:
            return jsonify({
                "success": False,
                "message": str(error)
            }), 500

    @staticmethod
    def update_question(question_id):
        try:
            db = Database.get_db()

            data = request.get_json()

            result = db.aptitude_questions.update_one(
                {
                    "_id": ObjectId(question_id)
                },
                {
                    "$set": data
                }
            )

            if result.matched_count == 0:
                return jsonify({
                    "success": False,
                    "message": "Question not found."
                }), 404

            return jsonify({
                "success": True,
                "message": "Question updated successfully."
            }), 200

        except Exception as error:
            return jsonify({
                "success": False,
                "message": str(error)
            }), 500

    @staticmethod
    def delete_question(question_id):
        try:
            db = Database.get_db()

            result = db.aptitude_questions.delete_one({
                "_id": ObjectId(question_id)
            })

            if result.deleted_count == 0:
                return jsonify({
                    "success": False,
                    "message": "Question not found."
                }), 404

            return jsonify({
                "success": True,
                "message": "Question deleted successfully."
            }), 200

        except Exception as error:
            return jsonify({
                "success": False,
                "message": str(error)
            }), 500

    @staticmethod
    def generate_assessment():
        try:
            db = Database.get_db()

            questions = list(
                db.aptitude_questions.aggregate([
                    {
                        "$match": {
                            "is_active": True
                        }
                    },
                    {
                        "$sample": {
                            "size": 20
                        }
                    }
                ])
            )

            for question in questions:
                question["_id"] = str(question["_id"])
                question.pop("correct_answer", None)

            return jsonify({
                "success": True,
                "total_questions": len(questions),
                "data": questions
            }), 200

        except Exception as error:
            return jsonify({
                "success": False,
                "message": str(error)
            }), 500

    @staticmethod
    def submit_assessment():
        try:
            db = Database.get_db()

            data = request.get_json()

            answers = data.get("answers", [])

            score = 0

            for answer in answers:

                question = db.aptitude_questions.find_one({
                    "_id": ObjectId(answer["question_id"])
                })

                if (
                    question
                    and question["correct_answer"]
                    == answer["selected_option"]
                ):
                    score += question.get("marks", 1)

            return jsonify({
                "success": True,
                "score": score
            }), 200

        except Exception as error:
            return jsonify({
                "success": False,
                "message": str(error)
            }), 500

    @staticmethod
    def get_all_questions():
        return AptitudeController.get_questions()

    @staticmethod
    def get_question_by_id(question_id):
        return AptitudeController.get_question(question_id)