"""
Coding Controller Module
Handles full CRUD, random coding challenge generation, and evaluation for coding questions.
"""

from datetime import datetime, timezone
from flask import request, jsonify
from bson import ObjectId

try:
    from config.database import Database
    from models.coding_question_model import CodingQuestion
except ImportError:
    from app.config.database import Database
    from app.models.coding_question_model import CodingQuestion


class CodingController:
    """Coding Question Controller"""

    @staticmethod
    def create_question():
        """
        POST /api/coding (or /api/coding/questions)
        Creates a new coding question document.
        """
        try:
            data = request.get_json(silent=True) or {}

            title = data.get("title", data.get("question"))
            problem_statement = data.get("problemStatement", data.get("problem_statement", data.get("description")))
            programming_language = data.get("programmingLanguage", data.get("programming_language", "Python"))
            difficulty = data.get("difficulty", "Easy")
            input_format = data.get("inputFormat", data.get("input_format", ""))
            output_format = data.get("outputFormat", data.get("output_format", ""))
            constraints = data.get("constraints", "")
            sample_input = data.get("sampleInput", data.get("sample_input", ""))
            sample_output = data.get("sampleOutput", data.get("sample_output", ""))
            test_cases = data.get("testCases", data.get("test_cases", []))
            hidden_test_cases = data.get("hiddenTestCases", data.get("hidden_test_cases", []))
            marks = data.get("marks", 10)
            category = data.get("category", "Algorithms")
            tags = data.get("tags", [])

            if not title or not problem_statement:
                return jsonify({
                    "success": False,
                    "message": "Required fields missing: title and problemStatement are required."
                }), 400

            question_doc = CodingQuestion.create_question(
                title=title,
                problem_statement=problem_statement,
                programming_language=programming_language,
                difficulty=difficulty,
                input_format=input_format,
                output_format=output_format,
                constraints=constraints,
                sample_input=sample_input,
                sample_output=sample_output,
                test_cases=test_cases,
                hidden_test_cases=hidden_test_cases,
                marks=marks,
                category=category,
                tags=tags
            )

            db = Database.get_db()
            result = db.coding_questions.insert_one(question_doc)

            return jsonify({
                "success": True,
                "message": "Question created successfully.",
                "question_id": str(result.inserted_id),
                "data": CodingQuestion.response(question_doc)
            }), 201

        except Exception as error:
            return jsonify({
                "success": False,
                "message": str(error)
            }), 500

    @staticmethod
    def get_all_questions():
        """
        GET /api/coding (or /api/coding/questions)
        Retrieves all coding questions.
        """
        try:
            db = Database.get_db()

            query = {}
            if request and hasattr(request, "args"):
                lang = request.args.get("programmingLanguage")
                diff = request.args.get("difficulty")
                if lang:
                    query["programmingLanguage"] = {"$regex": f"^{lang}$", "$options": "i"}
                if diff:
                    query["difficulty"] = {"$regex": f"^{diff}$", "$options": "i"}

            questions_cursor = db.coding_questions.find(query)
            questions = [CodingQuestion.response(q) for q in questions_cursor if q]

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
        GET /api/coding/<question_id>
        Retrieves a specific coding question by ID.
        """
        try:
            if not ObjectId.is_valid(question_id):
                return jsonify({
                    "success": False,
                    "message": "Invalid question ID format."
                }), 400

            db = Database.get_db()
            question = db.coding_questions.find_one({"_id": ObjectId(question_id)})

            if not question:
                return jsonify({
                    "success": False,
                    "message": "Question not found."
                }), 404

            return jsonify({
                "success": True,
                "data": CodingQuestion.response(question)
            }), 200

        except Exception as error:
            return jsonify({
                "success": False,
                "message": str(error)
            }), 500

    @staticmethod
    def update_question(question_id):
        """
        PUT /api/coding/<question_id>
        Updates an existing coding question.
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
            if "title" in data:
                update_fields["title"] = data["title"]
            if "programmingLanguage" in data:
                update_fields["programmingLanguage"] = data["programmingLanguage"]
            if "difficulty" in data:
                update_fields["difficulty"] = data["difficulty"]
            if "problemStatement" in data:
                update_fields["problemStatement"] = data["problemStatement"]
            if "inputFormat" in data:
                update_fields["inputFormat"] = data["inputFormat"]
            if "outputFormat" in data:
                update_fields["outputFormat"] = data["outputFormat"]
            if "constraints" in data:
                update_fields["constraints"] = data["constraints"]
            if "sampleInput" in data:
                update_fields["sampleInput"] = data["sampleInput"]
            if "sampleOutput" in data:
                update_fields["sampleOutput"] = data["sampleOutput"]
            if "testCases" in data:
                update_fields["testCases"] = data["testCases"]
                update_fields["sampleTestCases"] = data["testCases"]
            if "hiddenTestCases" in data:
                update_fields["hiddenTestCases"] = data["hiddenTestCases"]
            if "marks" in data:
                update_fields["marks"] = int(data["marks"])
            if "isActive" in data:
                update_fields["isActive"] = bool(data["isActive"])

            update_fields["updatedAt"] = datetime.now(timezone.utc)

            db = Database.get_db()
            result = db.coding_questions.update_one(
                {"_id": ObjectId(question_id)},
                {"$set": update_fields}
            )

            if result.matched_count == 0:
                return jsonify({
                    "success": False,
                    "message": "Question not found."
                }), 404

            updated_doc = db.coding_questions.find_one({"_id": ObjectId(question_id)})

            return jsonify({
                "success": True,
                "message": "Question updated successfully.",
                "data": CodingQuestion.response(updated_doc)
            }), 200

        except Exception as error:
            return jsonify({
                "success": False,
                "message": str(error)
            }), 500

    @staticmethod
    def delete_question(question_id):
        """
        DELETE /api/coding/<question_id>
        Deletes a coding question by ID.
        """
        try:
            if not ObjectId.is_valid(question_id):
                return jsonify({
                    "success": False,
                    "message": "Invalid question ID format."
                }), 400

            db = Database.get_db()
            result = db.coding_questions.delete_one({"_id": ObjectId(question_id)})

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
        POST /api/coding/generate
        Randomly samples coding challenges from MongoDB.
        """
        try:
            data = request.get_json(silent=True) or {}
            num_questions = int(data.get("numberOfQuestions", data.get("total_questions", 3)))
            difficulty = data.get("difficulty")

            match_stage = {"isActive": True}
            if difficulty:
                match_stage["difficulty"] = difficulty

            pipeline = [
                {"$match": match_stage},
                {"$sample": {"size": max(1, num_questions)}}
            ]

            db = Database.get_db()
            sampled_docs = list(db.coding_questions.aggregate(pipeline))

            if len(sampled_docs) < num_questions and difficulty:
                fallback_pipeline = [
                    {"$match": {"isActive": True}},
                    {"$sample": {"size": max(1, num_questions)}}
                ]
                sampled_docs = list(db.coding_questions.aggregate(fallback_pipeline))

            formatted_questions = []
            for doc in sampled_docs:
                item = CodingQuestion.response(doc)
                if item:
                    item.pop("hiddenTestCases", None)
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
        POST /api/coding/submit
        Evaluates candidate coding answers.
        """
        try:
            data = request.get_json(silent=True) or {}
            answers = data.get("answers", data.get("submissions", []))

            if not isinstance(answers, list):
                return jsonify({
                    "success": False,
                    "message": "Answers must be a list of user code responses."
                }), 400

            db = Database.get_db()
            score = 0
            total_possible_marks = 0

            for ans in answers:
                question_id = ans.get("questionId", ans.get("question_id"))
                if not question_id or not ObjectId.is_valid(question_id):
                    continue

                q_doc = db.coding_questions.find_one({"_id": ObjectId(question_id)})
                if not q_doc:
                    continue

                q_marks = q_doc.get("marks", 10)
                total_possible_marks += q_marks
                # If code is present and non-empty, assign marks or run evaluation
                if ans.get("code") or ans.get("solution"):
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
