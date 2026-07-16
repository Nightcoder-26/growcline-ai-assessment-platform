"""
Technical Controller Module
Handles full CRUD, random assessment generation, and evaluation for technical questions.
"""

from datetime import datetime, timezone
from flask import request, jsonify
from bson import ObjectId

try:
    from config.database import Database
    from models.technical_question_model import TechnicalQuestion
except ImportError:
    from app.config.database import Database
    from app.models.technical_question_model import TechnicalQuestion


class TechnicalController:
    """Technical Question Controller"""

    @staticmethod
    def create_question():
        """
        POST /api/technical (or /api/technical/questions)
        Creates a new technical question document.
        """
        try:
            data = request.get_json(silent=True) or {}

            question_text = data.get("question")
            technology = data.get("technology", "Python")
            category = data.get("category", technology)
            difficulty = data.get("difficulty", "Easy")
            options = data.get("options")
            correct_answer = data.get("correctAnswer", data.get("correct_answer"))
            explanation = data.get("explanation", "")
            marks = data.get("marks", 1)
            question_type = data.get("questionType", data.get("question_type", "MCQ"))
            tags = data.get("tags", [])

            if not question_text or not options or correct_answer is None:
                return jsonify({
                    "success": False,
                    "message": "Required fields missing: question, options, and correctAnswer are required."
                }), 400

            if not isinstance(options, list) or len(options) < 2:
                return jsonify({
                    "success": False,
                    "message": "Options must be a list containing at least 2 items."
                }), 400

            question_doc = TechnicalQuestion.create_question(
                technology=technology,
                category=category,
                question=question_text,
                options=options,
                correct_answer=correct_answer,
                difficulty=difficulty,
                marks=marks,
                explanation=explanation,
                question_type=question_type,
                tags=tags
            )

            db = Database.get_db()
            result = db.technical_questions.insert_one(question_doc)

            return jsonify({
                "success": True,
                "message": "Question created successfully.",
                "question_id": str(result.inserted_id),
                "data": TechnicalQuestion.response(question_doc)
            }), 201

        except Exception as error:
            return jsonify({
                "success": False,
                "message": str(error)
            }), 500

    @staticmethod
    def get_all_questions():
        """
        GET /api/technical (or /api/technical/questions)
        Retrieves all technical questions with optional filtering.
        """
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

            questions_cursor = db.technical_questions.find(query)
            questions = [TechnicalQuestion.response(q) for q in questions_cursor if q]

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
    def get_question_by_id(question_id):
        """
        GET /api/technical/<question_id>
        Retrieves a specific technical question by ID.
        """
        try:
            if not ObjectId.is_valid(question_id):
                return jsonify({
                    "success": False,
                    "message": "Invalid question ID format."
                }), 400

            db = Database.get_db()
            question = db.technical_questions.find_one({"_id": ObjectId(question_id)})

            if not question:
                return jsonify({
                    "success": False,
                    "message": "Question not found."
                }), 404

            return jsonify({
                "success": True,
                "data": TechnicalQuestion.response(question)
            }), 200

        except Exception as error:
            return jsonify({
                "success": False,
                "message": str(error)
            }), 500

    @staticmethod
    def update_question(question_id):
        """
        PUT /api/technical/<question_id>
        Updates an existing technical question.
        """
        try:
            if not ObjectId.is_valid(question_id):
                return jsonify({
                    "success": False,
                    "message": "Invalid question ID format."
                }), 400

            data = request.get_json(silent=True) or {}
            if not data:
                return jsonify({
                    "success": False,
                    "message": "No update payload provided."
                }), 400

            update_fields = {}
            if "technology" in data:
                update_fields["technology"] = data["technology"]
            if "category" in data:
                update_fields["category"] = data["category"]
            if "question" in data:
                update_fields["question"] = data["question"]
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
            result = db.technical_questions.update_one(
                {"_id": ObjectId(question_id)},
                {"$set": update_fields}
            )

            if result.matched_count == 0:
                return jsonify({
                    "success": False,
                    "message": "Question not found."
                }), 404

            updated_doc = db.technical_questions.find_one({"_id": ObjectId(question_id)})

            return jsonify({
                "success": True,
                "message": "Question updated successfully.",
                "data": TechnicalQuestion.response(updated_doc)
            }), 200

        except Exception as error:
            return jsonify({
                "success": False,
                "message": str(error)
            }), 500

    @staticmethod
    def delete_question(question_id):
        """
        DELETE /api/technical/<question_id>
        Deletes a technical question by ID.
        """
        try:
            if not ObjectId.is_valid(question_id):
                return jsonify({
                    "success": False,
                    "message": "Invalid question ID format."
                }), 400

            db = Database.get_db()
            result = db.technical_questions.delete_one({"_id": ObjectId(question_id)})

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
        """
        POST /api/technical/generate
        Randomly samples questions from MongoDB matching technology and difficulty.
        """
        try:
            data = request.get_json(silent=True) or {}
            num_questions = int(data.get("numberOfQuestions", data.get("total_questions", 10)))
            difficulty = data.get("difficulty")
            technology = data.get("technology")

            match_stage = {"isActive": True}
            if difficulty:
                match_stage["difficulty"] = difficulty
            if technology:
                match_stage["technology"] = {"$regex": f"^{technology}$", "$options": "i"}

            pipeline = [
                {"$match": match_stage},
                {"$sample": {"size": max(1, num_questions)}}
            ]

            db = Database.get_db()
            sampled_docs = list(db.technical_questions.aggregate(pipeline))

            # Fallback if fewer found with exact filters
            if len(sampled_docs) < num_questions and (difficulty or technology):
                fallback_pipeline = [
                    {"$match": {"isActive": True}},
                    {"$sample": {"size": max(1, num_questions)}}
                ]
                sampled_docs = list(db.technical_questions.aggregate(fallback_pipeline))

            formatted_questions = []
            for doc in sampled_docs:
                item = TechnicalQuestion.response(doc)
                if item:
                    item.pop("correctAnswer", None)
                    formatted_questions.append(item)

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
    def submit_assessment():
        """
        POST /api/technical/submit
        Evaluates candidate answers and returns score & percentage.
        """
        try:
            data = request.get_json(silent=True) or {}
            answers = data.get("answers", [])

            if not isinstance(answers, list):
                return jsonify({
                    "success": False,
                    "message": "Answers must be a list of user responses."
                }), 400

            db = Database.get_db()
            score = 0
            total_possible_marks = 0

            for ans in answers:
                question_id = ans.get("questionId", ans.get("question_id"))
                selected_answer = ans.get("selectedAnswer", ans.get("selected_option"))

                if not question_id or not ObjectId.is_valid(question_id):
                    continue

                q_doc = db.technical_questions.find_one({"_id": ObjectId(question_id)})
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

            return jsonify({
                "success": True,
                "score": score,
                "percentage": percentage
            }), 200

        except Exception as error:
            return jsonify({
                "success": False,
                "message": str(error)
            }), 500
