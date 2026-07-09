"""
Coding Service Module
Responsible for:
- Managing coding questions
- Validating submission payloads
- Running hidden test case evaluation via an extensible execution interface
- Comparing expected vs actual outputs
- Calculating coding marks and generating execution results

Architecture: Controller -> Service -> Model -> MongoDB
"""

import logging
import subprocess
import tempfile
import os
import time
import shutil
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from bson import ObjectId
from pymongo.errors import PyMongoError

try:
    from config.database import Database
except ImportError:
    from app.config.database import Database

try:
    from models.coding_question_model import CodingQuestion
    from services.question_service import QuestionService, QUESTION_TYPE_CODING
except ImportError:
    from app.models.coding_question_model import CodingQuestion
    from app.services.question_service import QuestionService, QUESTION_TYPE_CODING

logger = logging.getLogger(__name__)

# Constants for Execution Status
STATUS_SUCCESS = "SUCCESS"
STATUS_ACCEPTED = "Accepted"
STATUS_WRONG_ANSWER = "Wrong Answer"
STATUS_TIME_LIMIT_EXCEEDED = "Time Limit Exceeded"
STATUS_MEMORY_LIMIT_EXCEEDED = "Memory Limit Exceeded"
STATUS_RUNTIME_ERROR = "Runtime Error"
STATUS_COMPILATION_ERROR = "Compilation Error"
STATUS_UNSUPPORTED_LANGUAGE = "Unsupported Language"

SUPPORTED_LANGUAGES = {"python", "python3", "javascript", "js", "java", "cpp", "c"}


class ICodeExecutionEngine(ABC):
    """
    Abstract Base Class / Extensible Interface for Code Execution Engines.
    Designed so external sandboxes (Docker, Judge0, AWS Lambda, Kubernetes pods)
    can easily be plugged into the platform without altering business logic.
    """

    @abstractmethod
    def execute(
        self,
        code: str,
        language: str,
        input_data: str,
        time_limit: float,
        memory_limit: int
    ) -> Dict[str, Any]:
        """
        Executes code against provided standard input within time and memory boundaries.

        Args:
            code (str): Source code string.
            language (str): Programming language (e.g., 'python', 'cpp', 'java').
            input_data (str): Standard input provided to the script.
            time_limit (float): Maximum allowed execution time in seconds.
            memory_limit (int): Maximum allowed memory limit in MB.

        Returns:
            Dict[str, Any]: {
                "status": str (STATUS_* constant),
                "output": str (stdout),
                "error": str (stderr),
                "execution_time_ms": float
            }
        """
        pass


class LocalPythonExecutionEngine(ICodeExecutionEngine):
    """
    Concrete implementation of ICodeExecutionEngine for local Python execution using subprocesses.
    Includes time-limit enforcement and temporary sandbox file cleanup.
    Note: For production deployments, use DockerExecutionEngine or RemoteJudgeExecutionEngine.
    """

    def execute(
        self,
        code: str,
        language: str,
        input_data: str,
        time_limit: float = 2.0,
        memory_limit: int = 256
    ) -> Dict[str, Any]:
        lang_clean = language.lower().strip()
        if lang_clean not in {"python", "python3", "py"}:
            return {
                "status": STATUS_UNSUPPORTED_LANGUAGE,
                "output": "",
                "error": f"Language '{language}' is not supported by LocalPythonExecutionEngine.",
                "execution_time_ms": 0.0
            }

        temp_dir = None
        try:
            # Create isolated temporary directory
            temp_dir = tempfile.mkdtemp(prefix="growcline_sandbox_")
            script_path = os.path.join(temp_dir, "solution.py")

            with open(script_path, "w", encoding="utf-8") as f:
                f.write(code)

            start_time = time.time()
            process = subprocess.Popen(
                ["python", script_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=temp_dir
            )

            stdout_data, stderr_data = process.communicate(input=input_data, timeout=time_limit)
            exec_time_ms = (time.time() - start_time) * 1000.0

            if process.returncode != 0:
                return {
                    "status": STATUS_RUNTIME_ERROR,
                    "output": stdout_data.strip(),
                    "error": stderr_data.strip(),
                    "execution_time_ms": round(exec_time_ms, 2)
                }

            return {
                "status": STATUS_SUCCESS,
                "output": stdout_data.strip(),
                "error": "",
                "execution_time_ms": round(exec_time_ms, 2)
            }

        except subprocess.TimeoutExpired:
            if 'process' in locals() and process:
                process.kill()
            return {
                "status": STATUS_TIME_LIMIT_EXCEEDED,
                "output": "",
                "error": f"Execution exceeded maximum allowed time limit of {time_limit}s.",
                "execution_time_ms": time_limit * 1000.0
            }
        except Exception as e:
            logger.error(f"Sandbox execution failure: {str(e)}", exc_info=True)
            return {
                "status": STATUS_RUNTIME_ERROR,
                "output": "",
                "error": f"Internal execution engine error: {str(e)}",
                "execution_time_ms": 0.0
            }
        finally:
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                except Exception:
                    pass


class DockerExecutionEngine(ICodeExecutionEngine):
    """
    Extensible Interface / Adapter for containerized Docker execution or Kubernetes Pods.
    This class demonstrates how the platform cleanly scales to support multi-language sandboxes
    without modifying controller or scoring layers.
    """

    def execute(
        self,
        code: str,
        language: str,
        input_data: str,
        time_limit: float = 2.0,
        memory_limit: int = 256
    ) -> Dict[str, Any]:
        """
        Implementation note: When plugging into Docker SDK or REST APIs (like Judge0 / Piston),
        construct the container payload here, invoke the external evaluation interface,
        and map the response back to standard ExecutionResult format.
        """
        logger.info(f"Delegating execution of {language} code to Docker/Remote sandbox engine.")
        # Fallback to local python engine if language is Python, else return structured interface response
        if language.lower() in {"python", "python3"}:
            return LocalPythonExecutionEngine().execute(code, language, input_data, time_limit, memory_limit)
        
        return {
            "status": STATUS_UNSUPPORTED_LANGUAGE,
            "output": "",
            "error": f"External Docker sandbox for '{language}' is configured as an extensible interface. Plug in Judge0/Docker SDK here.",
            "execution_time_ms": 0.0
        }


class CodingService:
    """
    Service class responsible for coding assessment workflows:
    - Managing coding problems
    - Validating user submissions
    - Executing test case evaluation engines
    - Grading output and generating actionable score reports
    """

    @staticmethod
    def get_execution_engine(engine_type: str = "local") -> ICodeExecutionEngine:
        """
        Factory method to acquire an instance of the requested code execution engine.

        Args:
            engine_type (str): Engine identifier ('local', 'docker', 'judge0').

        Returns:
            ICodeExecutionEngine: Configured engine instance.
        """
        if engine_type.lower() == "docker":
            return DockerExecutionEngine()
        return LocalPythonExecutionEngine()

    @classmethod
    def manage_question(cls, action: str, question_id: Optional[str] = None, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Unified management wrapper for CRUD operations on coding questions.
        Delegates to QuestionService to ensure duplicate validation and schema compliance.

        Args:
            action (str): Operation type ('create', 'get', 'update', 'delete', 'list').
            question_id (Optional[str]): Target question ID.
            payload (Optional[Dict[str, Any]]): Data for create/update.

        Returns:
            Dict[str, Any]: Standardized API response.
        """
        act = action.lower().strip()
        if act == "create":
            return QuestionService.create_question(QUESTION_TYPE_CODING, payload or {})
        elif act == "get" and question_id:
            return QuestionService.get_question_by_id(QUESTION_TYPE_CODING, question_id)
        elif act == "update" and question_id:
            return QuestionService.update_question(QUESTION_TYPE_CODING, question_id, payload or {})
        elif act == "delete" and question_id:
            return QuestionService.delete_question(QUESTION_TYPE_CODING, question_id)
        elif act == "list":
            return QuestionService.list_questions(QUESTION_TYPE_CODING, **(payload or {}))
        else:
            return {"success": False, "status_code": 400, "message": "Invalid management action specified.", "error": "INVALID_ACTION"}

    @classmethod
    def validate_submission(cls, submission_payload: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validates the structure and syntax requirements of a coding submission payload.

        Args:
            submission_payload (Dict[str, Any]): Incoming submission data.

        Returns:
            Tuple[bool, str, Dict[str, Any]]: (Is Valid, Error Message, Fetched Question Document)
        """
        if not submission_payload or not isinstance(submission_payload, dict):
            return False, "Submission payload must be a non-empty JSON object.", {}

        question_id = submission_payload.get("questionId") or submission_payload.get("question_id")
        code = submission_payload.get("code", "")
        language = submission_payload.get("programmingLanguage") or submission_payload.get("language", "python")

        if not question_id or not ObjectId.is_valid(question_id):
            return False, "Valid 'questionId' is required.", {}

        if not code or not code.strip():
            return False, "Source code cannot be empty.", {}

        if len(code) > 50000:
            return False, "Source code exceeds maximum allowed length of 50,000 characters.", {}

        if language.lower().strip() not in SUPPORTED_LANGUAGES:
            return False, f"Unsupported programming language '{language}'. Supported: {', '.join(SUPPORTED_LANGUAGES)}", {}

        try:
            db = Database.get_db()
            question_doc = db.coding_questions.find_one({"_id": ObjectId(question_id), "isActive": True})
            if not question_doc:
                return False, "Coding question not found or is no longer active.", {}
            
            return True, "", question_doc
        except PyMongoError as db_err:
            logger.error(f"Database error during submission validation: {str(db_err)}")
            return False, "Database connection error during validation.", {}

    @classmethod
    def run_test_case_evaluation(
        cls,
        engine: ICodeExecutionEngine,
        code: str,
        language: str,
        test_case: Dict[str, Any],
        time_limit: float,
        memory_limit: int,
        is_hidden: bool = False
    ) -> Dict[str, Any]:
        """
        Evaluates a single test case against the user's source code.
        Compares actual output with expected output using strict trimming.

        Args:
            engine (ICodeExecutionEngine): Execution engine instance.
            code (str): Source code.
            language (str): Programming language.
            test_case (Dict[str, Any]): Test case dictionary with 'input' and 'output'.
            time_limit (float): Max execution time.
            memory_limit (int): Max memory usage.
            is_hidden (bool): If True, masks actual/expected output in the return object.

        Returns:
            Dict[str, Any]: Evaluation summary for this test case.
        """
        input_str = str(test_case.get("input", ""))
        expected_output = str(test_case.get("output", "")).strip()

        exec_result = engine.execute(code, language, input_str, time_limit, memory_limit)
        actual_output = exec_result.get("output", "").strip()
        exec_status = exec_result.get("status", STATUS_RUNTIME_ERROR)

        passed = False
        test_status = exec_status

        if exec_status == STATUS_SUCCESS:
            if actual_output == expected_output:
                passed = True
                test_status = STATUS_ACCEPTED
            else:
                test_status = STATUS_WRONG_ANSWER

        result_item = {
            "test_case_id": str(test_case.get("_id", ObjectId())),
            "is_hidden": is_hidden,
            "passed": passed,
            "status": test_status,
            "execution_time_ms": exec_result.get("execution_time_ms", 0.0),
            "error_message": exec_result.get("error", "")
        }

        if not is_hidden:
            result_item["input"] = input_str
            result_item["expected_output"] = expected_output
            result_item["actual_output"] = actual_output
        else:
            result_item["input"] = "Hidden Test Case"
            result_item["expected_output"] = "Hidden"
            result_item["actual_output"] = "Hidden" if not passed else "Matched"

        return result_item

    @classmethod
    def evaluate_submission(
        cls,
        submission_payload: Dict[str, Any],
        engine_type: str = "local"
    ) -> Dict[str, Any]:
        """
        Executes complete end-to-end evaluation of a coding submission.
        Runs sample and hidden test cases, computes final grade, and returns execution breakdown.

        Args:
            submission_payload (Dict[str, Any]): Payload containing questionId, code, language, userId.
            engine_type (str): Sandbox engine type ('local', 'docker').

        Returns:
            Dict[str, Any]: Comprehensive grading and evaluation report.
        """
        is_valid, error_msg, question_doc = cls.validate_submission(submission_payload)
        if not is_valid:
            return {
                "success": False,
                "status_code": 400,
                "message": error_msg,
                "error": "VALIDATION_FAILED"
            }

        try:
            code = submission_payload.get("code", "")
            language = submission_payload.get("programmingLanguage") or submission_payload.get("language", "python")
            time_limit = float(question_doc.get("timeLimit", 2.0))
            memory_limit = int(question_doc.get("memoryLimit", 256))
            max_marks = float(question_doc.get("marks", 10.0))

            sample_tests = question_doc.get("sampleTestCases", [])
            hidden_tests = question_doc.get("hiddenTestCases", [])
            all_tests = [(tc, False) for tc in sample_tests] + [(tc, True) for tc in hidden_tests]

            if not all_tests:
                logger.warning(f"Question ID {question_doc['_id']} has no test cases configured.")
                return {
                    "success": True,
                    "status_code": 200,
                    "message": "Submission received, but question has no test cases configured.",
                    "data": {
                        "question_id": str(question_doc["_id"]),
                        "status": STATUS_ACCEPTED,
                        "marks_obtained": max_marks,
                        "max_marks": max_marks,
                        "passed_tests": 0,
                        "total_tests": 0,
                        "test_results": []
                    }
                }

            engine = cls.get_execution_engine(engine_type)
            test_results = []
            passed_count = 0
            overall_status = STATUS_ACCEPTED

            for tc, is_hidden in all_tests:
                eval_res = cls.run_test_case_evaluation(
                    engine=engine,
                    code=code,
                    language=language,
                    test_case=tc,
                    time_limit=time_limit,
                    memory_limit=memory_limit,
                    is_hidden=is_hidden
                )
                test_results.append(eval_res)
                if eval_res["passed"]:
                    passed_count += 1
                else:
                    # Capture first failure reason as overall status if not Accepted
                    if overall_status == STATUS_ACCEPTED:
                        overall_status = eval_res["status"]

            total_tests = len(all_tests)
            marks_obtained = round((passed_count / total_tests) * max_marks, 2) if total_tests > 0 else 0.0

            logger.info(f"Evaluated submission for Question {question_doc['_id']}: {passed_count}/{total_tests} passed ({overall_status})")

            return {
                "success": True,
                "status_code": 200,
                "message": f"Code evaluation completed: {overall_status}.",
                "data": {
                    "question_id": str(question_doc["_id"]),
                    "status": overall_status,
                    "marks_obtained": marks_obtained,
                    "max_marks": max_marks,
                    "passed_tests": passed_count,
                    "total_tests": total_tests,
                    "percentage": round((passed_count / total_tests) * 100, 2) if total_tests > 0 else 0.0,
                    "test_results": test_results
                }
            }

        except Exception as err:
            logger.critical(f"Unexpected error during code evaluation: {str(err)}", exc_info=True)
            return {
                "success": False,
                "status_code": 500,
                "message": "Internal server error during code execution.",
                "error": "INTERNAL_SERVER_ERROR"
            }
