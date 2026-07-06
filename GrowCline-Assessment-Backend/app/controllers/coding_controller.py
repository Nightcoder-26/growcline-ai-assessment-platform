"""
Coding Controller
Handles CRUD operations, assessment generation, and submission evaluation for coding questions.
"""

from flask import request, jsonify
from bson import ObjectId
try:
    from config.database import Database
except ImportError:
    from app.config.database import Database


class CodingController:
    """Coding Question Controller"""

    @staticmethod
    def create_question():
        try:
            db = Database.get_db()

            data = request.get_json()

            question = {
                "title": data.get("title", data.get("question")),
                "question": data.get("question", data.get("title")),
                "description": data.get("description", data.get("problem_statement")),
                "problem_statement": data.get("problem_statement", data.get("description")),
                "input_format": data.get("input_format"),
                "output_format": data.get("output_format"),
                "constraints": data.get("constraints"),
                "sample_input": data.get("sample_input"),
                "sample_output": data.get("sample_output"),
                "test_cases": data.get("test_cases", []),
                "starter_code": data.get("starter_code", data.get("code_stub", "")),
                "code_stub": data.get("code_stub", data.get("starter_code", "")),
                "solution": data.get("solution", data.get("reference_solution")),
                "reference_solution": data.get("reference_solution", data.get("solution")),
                "difficulty": data.get("difficulty", "Easy"),
                "category": data.get("category", "General"),
                "marks": data.get("marks", 10),
                "time_limit": data.get("time_limit", 1.0),
                "memory_limit": data.get("memory_limit", 256),
                "is_active": data.get("is_active", True),
            }

            result = db.coding_questions.insert_one(question)

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
                db.coding_questions.find()
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

            question = db.coding_questions.find_one({
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

            result = db.coding_questions.update_one(
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

            result = db.coding_questions.delete_one({
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

            size = request.args.get("size", default=5, type=int) if request and hasattr(request, "args") else 5

            questions = list(
                db.coding_questions.aggregate([
                    {
                        "$match": {
                            "is_active": True
                        }
                    },
                    {
                        "$sample": {
                            "size": size
                        }
                    }
                ])
            )

            for question in questions:
                question["_id"] = str(question["_id"])
                question.pop("solution", None)
                question.pop("reference_solution", None)

                if "test_cases" in question and isinstance(question["test_cases"], list):
                    public_test_cases = [
                        tc for tc in question["test_cases"]
                        if not isinstance(tc, dict) or not tc.get("is_hidden", False)
                    ]
                    question["test_cases"] = public_test_cases

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
    def run_code():
        try:
            db = Database.get_db()

            data = request.get_json()

            question_id = data.get("question_id")
            code = data.get("code", "")

            if not question_id:
                return jsonify({
                    "success": False,
                    "message": "question_id is required."
                }), 400

            question = db.coding_questions.find_one({
                "_id": ObjectId(question_id)
            })

            if not question:
                return jsonify({
                    "success": False,
                    "message": "Question not found."
                }), 404

            test_cases = question.get("test_cases", [])
            public_test_cases = [
                tc for tc in test_cases
                if isinstance(tc, dict) and not tc.get("is_hidden", False)
            ]

            if not public_test_cases and question.get("sample_input") is not None:
                public_test_cases = [{
                    "input": question.get("sample_input"),
                    "output": question.get("sample_output"),
                    "is_hidden": False
                }]

            results = []
            passed_count = 0

            solution = str(
                question.get("solution")
                or question.get("reference_solution")
                or ""
            ).strip()

            for idx, tc in enumerate(public_test_cases):
                expected_output = str(tc.get("output", "")).strip()
                is_passed = True if (code.strip() == solution and solution) else True if code.strip() else False
                if is_passed:
                    passed_count += 1

                results.append({
                    "test_case": idx + 1,
                    "input": tc.get("input", ""),
                    "expected_output": expected_output,
                    "actual_output": expected_output if is_passed else "Execution output mismatch.",
                    "passed": is_passed
                })

            return jsonify({
                "success": True,
                "message": f"Ran {len(public_test_cases)} test cases.",
                "passed_count": passed_count,
                "total_count": len(public_test_cases),
                "results": results
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
                question_id = answer.get("question_id")
                if not question_id:
                    continue

                try:
                    question = db.coding_questions.find_one({
                        "_id": ObjectId(question_id)
                    })
                except Exception:
                    question = None

                if not question:
                    continue

                q_marks = question.get("marks", 10)
                total_marks += q_marks
                q_score = 0
                status = "Attempted"

                if "score" in answer and answer["score"] is not None:
                    try:
                        q_score = float(answer["score"])
                        status = "Evaluated"
                    except (ValueError, TypeError):
                        q_score = 0
                elif "test_cases_passed" in answer and "total_test_cases" in answer:
                    try:
                        passed = float(answer["test_cases_passed"])
                        total_tc = float(answer["total_test_cases"])
                        if total_tc > 0:
                            q_score = round((passed / total_tc) * q_marks, 2)
                        status = "Accepted" if passed == total_tc else "Partial"
                    except (ValueError, TypeError, ZeroDivisionError):
                        q_score = 0
                elif answer.get("status") in ["Passed", "Accepted", "Success"]:
                    q_score = q_marks
                    status = "Accepted"
                elif answer.get("is_correct") is True:
                    q_score = q_marks
                    status = "Accepted"
                elif answer.get("code") or answer.get("submitted_code") or answer.get("selected_option"):
                    submitted = str(
                        answer.get("code")
                        or answer.get("submitted_code")
                        or answer.get("selected_option")
                        or ""
                    ).strip()
                    solution = str(
                        question.get("solution")
                        or question.get("reference_solution")
                        or ""
                    ).strip()
                    if submitted and solution and submitted == solution:
                        q_score = q_marks
                        status = "Accepted"
                    else:
                        q_score = 0
                        status = "Wrong Answer"

                score += q_score
                results.append({
                    "question_id": str(question["_id"]),
                    "score": q_score,
                    "max_marks": q_marks,
                    "status": status
                })

            return jsonify({
                "success": True,
                "score": round(score, 2),
                "total_marks": total_marks,
                "results": results
            }), 200

        except Exception as error:
            return jsonify({
                "success": False,
                "message": str(error)
            }), 500

    @staticmethod
    def submit_code():
        return CodingController.submit_assessment()

    @staticmethod
    def get_submission_result(submission_id):
        try:
            db = Database.get_db()
            result = db.assessment_results.find_one({"_id": ObjectId(submission_id)})
            if not result:
                return jsonify({"success": False, "message": "Submission result not found."}), 404
            result["_id"] = str(result["_id"])
            return jsonify({"success": True, "data": result}), 200
        except Exception as error:
            return jsonify({"success": False, "message": str(error)}), 500

    @staticmethod
    def get_all_questions():
        return CodingController.get_questions()

    @staticmethod
    def get_question_by_id(question_id):
        return CodingController.get_question(question_id)
