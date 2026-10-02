"""
Coding Controller Module
Handles CRUD, random challenge generation, Run, Submit-One, and batch Submit for coding questions.

Auth: all /run and /submit* endpoints require JWT (via get_current_user dependency in routes).
      Only admins may create/update/delete questions.

Concurrency strategy for 15-problem Submit:
  - We evaluate all 15 problems in a ThreadPoolExecutor (cap 5) to stay within typical
    60-second HTTP request timeouts while calling Judge0 in parallel.
  - Background job polling was considered but adds complexity; parallel evaluation with
    a 45-second aggregate timeout is sufficient for 15 × 2s problems at concurrency 5.
"""

from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from bson import ObjectId
from typing import Optional, Dict, Any, List

try:
    from config.database import Database
    from models.coding_question_model import CodingQuestion
    from services.coding_service import (
        CodingService,
        check_run_rate_limit,
        RUN_RATE_LIMIT_SECONDS,
        STATUS_JUDGE_UNAVAILABLE,
    )
except ImportError:
    from app.config.database import Database
    from app.models.coding_question_model import CodingQuestion
    from app.services.coding_service import (
        CodingService,
        check_run_rate_limit,
        RUN_RATE_LIMIT_SECONDS,
        STATUS_JUDGE_UNAVAILABLE,
    )


class CodingController:
    """Coding Question Controller"""

    # ── CRUD ──────────────────────────────────────────────────────────────────

    @staticmethod
    def create_question(data: dict) -> tuple[dict, int]:
        """POST /api/coding — create a new coding question. Admin only."""
        try:
            title             = data.get("title", data.get("question"))
            problem_statement = data.get("problemStatement", data.get("problem_statement", data.get("description")))
            programming_language = data.get("programmingLanguage", data.get("programming_language", "Python"))
            difficulty        = data.get("difficulty", "Easy")
            input_format      = data.get("inputFormat", data.get("input_format", ""))
            output_format     = data.get("outputFormat", data.get("output_format", ""))
            constraints       = data.get("constraints", "")
            sample_input      = data.get("sampleInput", data.get("sample_input", ""))
            sample_output     = data.get("sampleOutput", data.get("sample_output", ""))
            test_cases        = data.get("testCases", data.get("test_cases", []))
            hidden_test_cases = data.get("hiddenTestCases", data.get("hidden_test_cases", []))
            marks             = data.get("marks", 10)
            category          = data.get("category", "Algorithms")
            tags              = data.get("tags", [])
            checker           = data.get("checker", "exact")
            reference_solution = data.get("referenceSolution", "")

            if not title or not problem_statement:
                return {
                    "success": False,
                    "message": "Required fields missing: title and problemStatement are required.",
                }, 400

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
                tags=tags,
                checker=checker,
                reference_solution=reference_solution,
            )

            db = Database.get_db()
            result = db.coding_questions.insert_one(question_doc)

            return {
                "success": True,
                "message": "Question created successfully.",
                "question_id": str(result.inserted_id),
                "data": CodingQuestion.response(question_doc),
            }, 201

        except Exception as error:
            return {"success": False, "message": str(error)}, 500

    @staticmethod
    def get_all_questions(
        programmingLanguage: Optional[str] = None,
        difficulty: Optional[str] = None,
    ) -> tuple[dict, int]:
        """GET /api/coding — list all questions (hidden tests stripped)."""
        try:
            db = Database.get_db()
            query: Dict[str, Any] = {}
            if programmingLanguage:
                query["programmingLanguage"] = {"$regex": f"^{programmingLanguage}$", "$options": "i"}
            if difficulty:
                query["difficulty"] = {"$regex": f"^{difficulty}$", "$options": "i"}

            questions = [CodingQuestion.response(q) for q in db.coding_questions.find(query) if q]
            return {"success": True, "count": len(questions), "data": questions}, 200

        except Exception as error:
            return {"success": False, "message": str(error)}, 500

    @staticmethod
    def get_question_by_id(question_id: str) -> tuple[dict, int]:
        """GET /api/coding/<question_id> — hidden tests always stripped."""
        try:
            if not ObjectId.is_valid(question_id):
                return {"success": False, "message": "Invalid question ID format."}, 400

            db = Database.get_db()
            question = db.coding_questions.find_one({"_id": ObjectId(question_id)})
            if not question:
                return {"success": False, "message": "Question not found."}, 404

            # include_hidden=False ensures hidden tests never reach the client
            return {"success": True, "data": CodingQuestion.response(question, include_hidden=False)}, 200

        except Exception as error:
            return {"success": False, "message": str(error)}, 500

    @staticmethod
    def update_question(question_id: str, data: dict) -> tuple[dict, int]:
        """PUT /api/coding/<question_id> — admin only."""
        try:
            if not ObjectId.is_valid(question_id):
                return {"success": False, "message": "Invalid question ID format."}, 400

            if not data:
                return {"success": False, "message": "No update payload provided."}, 400

            allowed = [
                "title", "programmingLanguage", "difficulty", "problemStatement",
                "inputFormat", "outputFormat", "constraints", "sampleInput", "sampleOutput",
                "marks", "isActive", "checker", "referenceSolution",
            ]
            update_fields: Dict[str, Any] = {k: data[k] for k in allowed if k in data}

            if "testCases" in data:
                update_fields["testCases"]       = data["testCases"]
                update_fields["sampleTestCases"] = data["testCases"]
            if "hiddenTestCases" in data:
                update_fields["hiddenTestCases"] = data["hiddenTestCases"]
            if "marks" in data:
                update_fields["marks"] = int(data["marks"])

            update_fields["updatedAt"] = datetime.now(timezone.utc)

            db = Database.get_db()
            result = db.coding_questions.update_one(
                {"_id": ObjectId(question_id)},
                {"$set": update_fields},
            )

            if result.matched_count == 0:
                return {"success": False, "message": "Question not found."}, 404

            updated_doc = db.coding_questions.find_one({"_id": ObjectId(question_id)})
            return {
                "success": True,
                "message": "Question updated successfully.",
                "data": CodingQuestion.response(updated_doc),
            }, 200

        except Exception as error:
            return {"success": False, "message": str(error)}, 500

    @staticmethod
    def delete_question(question_id: str) -> tuple[dict, int]:
        """DELETE /api/coding/<question_id> — admin only."""
        try:
            if not ObjectId.is_valid(question_id):
                return {"success": False, "message": "Invalid question ID format."}, 400

            db = Database.get_db()
            result = db.coding_questions.delete_one({"_id": ObjectId(question_id)})

            if result.deleted_count == 0:
                return {"success": False, "message": "Question not found."}, 404

            return {"success": True, "message": "Question deleted successfully."}, 200

        except Exception as error:
            return {"success": False, "message": str(error)}, 500

    @staticmethod
    def generate_assessment(data: dict) -> tuple[dict, int]:
        """POST /api/coding/generate — sample questions (hidden tests stripped)."""
        try:
            num_questions = int(data.get("numberOfQuestions", data.get("total_questions", 3)))
            difficulty    = data.get("difficulty")

            match_stage: Dict[str, Any] = {"isActive": True}
            if difficulty:
                match_stage["difficulty"] = difficulty

            pipeline = [
                {"$match": match_stage},
                {"$sample": {"size": max(1, num_questions)}},
            ]

            db = Database.get_db()
            sampled_docs = list(db.coding_questions.aggregate(pipeline))

            if len(sampled_docs) < num_questions and difficulty:
                sampled_docs = list(db.coding_questions.aggregate([
                    {"$match": {"isActive": True}},
                    {"$sample": {"size": max(1, num_questions)}},
                ]))

            # Never expose hidden tests in /generate
            formatted = [
                CodingQuestion.response(doc, include_hidden=False)
                for doc in sampled_docs
                if doc
            ]

            return {"success": True, "count": len(formatted), "data": formatted}, 200

        except Exception as error:
            return {"success": False, "message": str(error)}, 500

    # ── Run (sample test cases only) ──────────────────────────────────────────

    @staticmethod
    def run_code(data: dict, user_id: str) -> tuple[dict, int]:
        """
        POST /api/coding/run
        Runs code against sample test cases only. Rate-limited per user.
        Returns per-case results with input / expected / actual output.
        """
        # Rate limiting
        if not check_run_rate_limit(user_id):
            return {
                "success": False,
                "message": f"Too many run requests. Please wait {RUN_RATE_LIMIT_SECONDS}s between runs.",
                "error": "RATE_LIMITED",
            }, 429

        question_id = data.get("questionId") or data.get("question_id", "")
        code        = data.get("code", "")
        language    = data.get("language", "python")

        if not question_id:
            return {"success": False, "message": "questionId is required."}, 400
        if not code or not code.strip():
            return {"success": False, "message": "Code cannot be empty."}, 400
        if len(code) > 50000:
            return {"success": False, "message": "Code exceeds 50,000 character limit."}, 400

        result = CodingService.run_sample_cases(
            question_id=question_id,
            code=code,
            language=language,
            user_id=user_id,
        )
        status_code = result.pop("status_code", 200)
        return result, status_code

    # ── Submit-One (hidden test evaluation, single problem) ───────────────────

    @staticmethod
    def submit_one(data: dict, user_id: str) -> tuple[dict, int]:
        """
        POST /api/coding/submit-one
        Evaluates a single problem against all test cases (sample + hidden).
        Returns verdict and hidden test COUNTS only — never reveals hidden inputs/outputs.
        """
        payload = {**data, "userId": user_id}
        result  = CodingService.evaluate_submission(payload)

        if not result.get("success"):
            return result, result.get("status_code", 500)

        eval_data = result["data"]

        # Count hidden test pass/fail separately for the response
        test_results = eval_data.get("test_results", [])
        hidden_passed = sum(1 for r in test_results if r.get("is_hidden") and r.get("passed"))
        hidden_total  = sum(1 for r in test_results if r.get("is_hidden"))
        sample_passed = sum(1 for r in test_results if not r.get("is_hidden") and r.get("passed"))
        sample_total  = sum(1 for r in test_results if not r.get("is_hidden"))

        # Only return sample results details; hidden cases just show count
        sample_results = [r for r in test_results if not r.get("is_hidden")]
        hidden_summary = {
            "passed": hidden_passed,
            "total":  hidden_total,
        }

        return {
            "success":         True,
            "question_id":     eval_data["question_id"],
            "status":          eval_data["status"],
            "marks_obtained":  eval_data["marks_obtained"],
            "max_marks":       eval_data["max_marks"],
            "passed_tests":    eval_data["passed_tests"],
            "total_tests":     eval_data["total_tests"],
            "percentage":      eval_data["percentage"],
            "sample_results":  sample_results,
            "hidden_summary":  hidden_summary,
            "sample_passed":   sample_passed,
            "sample_total":    sample_total,
        }, 200

    # ── Submit-All (batch, 15 problems) ───────────────────────────────────────

    @staticmethod
    def submit_assessment(data: dict, user_id: str) -> tuple[dict, int]:
        """
        POST /api/coding/submit
        Batch-evaluates all submitted answers with real hidden-test grading.
        Runs problems in parallel (cap=5) to stay within request timeout.
        Response is backward-compatible: includes score/total/percentage PLUS
        a per-problem 'results' array.
        """
        answers     = data.get("answers", data.get("submissions", []))
        assessment_id = data.get("assessmentId")

        if not isinstance(answers, list):
            return {"success": False, "message": "Answers must be a list."}, 400

        if not answers:
            return {"success": False, "message": "No answers provided."}, 400

        def _eval_one(ans: Dict[str, Any]) -> Dict[str, Any]:
            """Evaluate one answer inside the thread pool."""
            payload = {**ans, "userId": user_id}
            result  = CodingService.evaluate_submission(payload)
            if not result.get("success"):
                return {
                    "question_id":    ans.get("questionId", ""),
                    "status":         "Error",
                    "marks_obtained": 0.0,
                    "max_marks":      0.0,
                    "passed_tests":   0,
                    "total_tests":    0,
                    "percentage":     0.0,
                    "error":          result.get("message", "Evaluation failed."),
                }
            d = result["data"]
            # Strip hidden test details from batch response too
            test_results = d.get("test_results", [])
            sample_results = [r for r in test_results if not r.get("is_hidden")]
            hidden_passed  = sum(1 for r in test_results if r.get("is_hidden") and r.get("passed"))
            hidden_total   = sum(1 for r in test_results if r.get("is_hidden"))
            return {
                "question_id":    d["question_id"],
                "status":         d["status"],
                "marks_obtained": d["marks_obtained"],
                "max_marks":      d["max_marks"],
                "passed_tests":   d["passed_tests"],
                "total_tests":    d["total_tests"],
                "percentage":     d["percentage"],
                "sample_results": sample_results,
                "hidden_summary": {"passed": hidden_passed, "total": hidden_total},
            }

        MAX_PARALLEL = 5
        problem_results: List[Dict[str, Any]] = []

        with ThreadPoolExecutor(max_workers=MAX_PARALLEL) as executor:
            future_map = {executor.submit(_eval_one, ans): ans for ans in answers}
            for future in as_completed(future_map):
                try:
                    problem_results.append(future.result())
                except Exception as exc:
                    ans = future_map[future]
                    problem_results.append({
                        "question_id":    ans.get("questionId", ""),
                        "status":         "Error",
                        "marks_obtained": 0.0,
                        "max_marks":      0.0,
                        "passed_tests":   0,
                        "total_tests":    0,
                        "percentage":     0.0,
                        "error":          str(exc),
                    })

        total_score    = sum(r.get("marks_obtained", 0.0) for r in problem_results)
        total_possible = sum(r.get("max_marks", 0.0) for r in problem_results)
        percentage     = round((total_score / total_possible) * 100, 2) if total_possible > 0 else 0.0

        # Backward-compatible response shape
        return {
            "success":    True,
            "score":      round(total_score, 2),
            "total":      round(total_possible, 2),
            "percentage": percentage,
            "results":    problem_results,
        }, 200

    @staticmethod
    def get_submission_status(job_id: str) -> tuple[dict, int]:
        """
        GET /api/coding/submissions/<job_id>
        Retrieves a persisted submission record from coding_submissions.
        """
        try:
            if not ObjectId.is_valid(job_id):
                return {"success": False, "message": "Invalid submission ID."}, 400

            db  = Database.get_db()
            doc = db.coding_submissions.find_one({"_id": ObjectId(job_id)})
            if not doc:
                return {"success": False, "message": "Submission not found."}, 404

            return {
                "success":     True,
                "id":          str(doc["_id"]),
                "kind":        doc.get("kind", "submit"),
                "verdict":     doc.get("verdict", ""),
                "passedTests": doc.get("passedTests", 0),
                "totalTests":  doc.get("totalTests", 0),
                "createdAt":   doc["createdAt"].isoformat() if isinstance(doc.get("createdAt"), datetime) else "",
            }, 200

        except Exception as error:
            return {"success": False, "message": str(error)}, 500
