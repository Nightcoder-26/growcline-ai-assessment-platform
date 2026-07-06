"""
Technical Controller
Handles CRUD operations, assessment generation, and submission evaluation for technical questions.
"""

from flask import request, jsonify
from bson import ObjectId
try:
    from config.database import Database
except ImportError:
    from app.config.database import Database

try:
    from models.technical_question_model import TechnicalQuestion
except ImportError:
    from app.models.technical_question_model import TechnicalQuestion


class TechnicalController:
    """Technical Question Controller"""

    @staticmethod
    def create_question():
        try:
            db = Database.get_db()
            data = request.get_json()

            if not data or not data.get("question"):
                return jsonify({
                    "success": False,
                    "message": "Question content is required."
                }), 400

            technology = data.get("technology", data.get("category", "General"))
            category = data.get("category", data.get("technology", "General"))
            question_text = data.get("question")
            options = data.get("options", [])
            correct_answer = data.get("correctAnswer", data.get("correct_answer"))
            difficulty = data.get("difficulty", "Easy")
            marks = data.get("marks", 1)
            explanation = data.get("explanation", "")
            question_type = data.get("questionType", data.get("question_type", "MCQ"))
            tags = data.get("tags", [])
            created_by = data.get("createdBy", data.get("created_by"))

            question = TechnicalQuestion.create_question(
                technology=technology,
                category=category,
                question=question_text,
                options=options,
                correct_answer=correct_answer,
                difficulty=difficulty,
                marks=marks,
                explanation=explanation,
                question_type=question_type,
                tags=tags,
                created_by=created_by
            )

            result = db.technical_questions.insert_one(question)

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

            query = {}
            if request and hasattr(request, "args"):
                tech = request.args.get("technology")
                cat = request.args.get("category")
                diff = request.args.get("difficulty")
                if tech:
                    query["technology"] = {"$regex": f"^{tech}$", "$options": "i"}
                if cat:
                    query["category"] = {"$regex": f"^{cat}$", "$options": "i"}
                if diff:
                    query["difficulty"] = {"$regex": f"^{diff}$", "$options": "i"}

            questions = list(db.technical_questions.find(query))

            formatted_questions = []
            for question in questions:
                try:
                    formatted = TechnicalQuestion.response(question)
                except Exception:
                    question["_id"] = str(question["_id"])
                    if "createdBy" in question and question["createdBy"]:
                        question["createdBy"] = str(question["createdBy"])
                    formatted = question
                formatted_questions.append(formatted)

            return jsonify({
                "success": True,
                "count": len(formatted_questions),
                "data": formatted_questions
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

            question = db.technical_questions.find_one({
                "_id": ObjectId(question_id)
            })

            if not question:
                return jsonify({
                    "success": False,
                    "message": "Question not found."
                }), 404

            try:
                formatted = TechnicalQuestion.response(question)
            except Exception:
                question["_id"] = str(question["_id"])
                if "createdBy" in question and question["createdBy"]:
                    question["createdBy"] = str(question["createdBy"])
                formatted = question

            return jsonify({
                "success": True,
                "data": formatted
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

            if not data:
                return jsonify({
                    "success": False,
                    "message": "No update data provided."
                }), 400

            update_fields = dict(data)
            update_fields.pop("_id", None)
            update_fields.pop("id", None)

            result = db.technical_questions.update_one(
                {
                    "_id": ObjectId(question_id)
                },
                {
                    "$set": update_fields
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

            result = db.technical_questions.delete_one({
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

            size = request.args.get("size", default=20, type=int) if request and hasattr(request, "args") else 20
            tech = request.args.get("technology") if request and hasattr(request, "args") else None
            cat = request.args.get("category") if request and hasattr(request, "args") else None

            match_stage = {"$or": [{"isActive": True}, {"is_active": True}, {"isActive": {"$exists": False}, "is_active": {"$exists": False}}]}
            if tech:
                match_stage["technology"] = {"$regex": f"^{tech}$", "$options": "i"}
            if cat:
                match_stage["category"] = {"$regex": f"^{cat}$", "$options": "i"}

            questions = list(
                db.technical_questions.aggregate([
                    {
                        "$match": match_stage
                    },
                    {
                        "$sample": {
                            "size": size
                        }
                    }
                ])
            )

            formatted_questions = []
            for question in questions:
                try:
                    formatted = TechnicalQuestion.response(question)
                except Exception:
                    question["_id"] = str(question["_id"])
                    if "createdBy" in question and question["createdBy"]:
                        question["createdBy"] = str(question["createdBy"])
                    formatted = question
                formatted.pop("correctAnswer", None)
                formatted.pop("correct_answer", None)
                formatted_questions.append(formatted)

            return jsonify({
                "success": True,
                "total_questions": len(formatted_questions),
                "data": formatted_questions
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
            total_marks = 0
            results = []

            for answer in answers:
                question_id = answer.get("question_id", answer.get("questionId"))
                if not question_id:
                    continue

                try:
                    question = db.technical_questions.find_one({
                        "_id": ObjectId(question_id)
                    })
                except Exception:
                    question = None

                if not question:
                    continue

                q_marks = question.get("marks", 1)
                total_marks += q_marks
                selected = answer.get("selected_option", answer.get("selectedOption", answer.get("answer")))
                correct = question.get("correctAnswer", question.get("correct_answer"))

                is_correct = (selected == correct) if correct is not None else False
                q_score = q_marks if is_correct else 0
                score += q_score

                results.append({
                    "question_id": str(question["_id"]),
                    "selected_option": selected,
                    "correct_answer": correct,
                    "is_correct": is_correct,
                    "marks": q_marks,
                    "score": q_score
                })

            return jsonify({
                "success": True,
                "score": score,
                "total_marks": total_marks,
                "results": results
            }), 200

        except Exception as error:
            return jsonify({
                "success": False,
                "message": str(error)
            }), 500

    @staticmethod
    def get_all_questions():
        return TechnicalController.get_questions()

    @staticmethod
    def get_question_by_id(question_id):
        return TechnicalController.get_question(question_id)
