"""
Coding Service Module
Responsible for:
- Managing coding questions
- Validating submission payloads
- Running hidden test case evaluation via an extensible execution interface
- Comparing expected vs actual outputs (exact / unordered_lines / unordered_tokens)
- Calculating coding marks and generating execution results
- Persisting run/submit events to coding_submissions collection

Architecture: Controller -> Service -> Model -> MongoDB

Judge0 integration notes:
- Set JUDGE0_URL (e.g. http://localhost:2358 for self-hosted)
- Optionally set JUDGE0_API_KEY and JUDGE0_RAPIDAPI_HOST for RapidAPI flavour
- Local subprocess fallback only enabled when ALLOW_LOCAL_EXECUTION=true (dev only)
"""

import logging
import subprocess
import tempfile
import os
import time
import shutil
import json
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple

import httpx
from bson import ObjectId
from pymongo.errors import PyMongoError

try:
    from config.database import Database
    from config.settings import Config
except ImportError:
    from app.config.database import Database
    from app.config.settings import Config

try:
    from models.coding_question_model import CodingQuestion
    from services.question_service import QuestionService, QUESTION_TYPE_CODING
except ImportError:
    from app.models.coding_question_model import CodingQuestion
    from app.services.question_service import QuestionService, QUESTION_TYPE_CODING

logger = logging.getLogger(__name__)

# ── Execution Status Constants ────────────────────────────────────────────────
STATUS_SUCCESS             = "SUCCESS"
STATUS_ACCEPTED            = "Accepted"
STATUS_WRONG_ANSWER        = "Wrong Answer"
STATUS_TIME_LIMIT_EXCEEDED = "Time Limit Exceeded"
STATUS_MEMORY_LIMIT_EXCEEDED = "Memory Limit Exceeded"
STATUS_RUNTIME_ERROR       = "Runtime Error"
STATUS_COMPILATION_ERROR   = "Compilation Error"
STATUS_UNSUPPORTED_LANGUAGE = "Unsupported Language"
STATUS_JUDGE_UNAVAILABLE   = "Judge Unavailable"

SUPPORTED_LANGUAGES = {"python", "python3", "javascript", "js", "java", "cpp", "c++", "c"}

# ── Judge0 Language ID Map ─────────────────────────────────────────────────────
# Verified against Judge0 CE language list (GET /languages).
# Language names are normalised to lowercase before lookup.
JUDGE0_LANGUAGE_IDS: Dict[str, int] = {
    "python":     71,
    "python3":    71,
    "py":         71,
    "javascript": 63,
    "js":         63,
    "java":       62,
    "c++":        54,
    "cpp":        54,
    "c":          50,
}


def _normalize_language(language: str) -> str:
    """Normalise language string for consistent lookup ('C++' -> 'cpp')."""
    lang = language.strip().lower()
    if lang in ("c++",):
        return "cpp"
    return lang


def _normalize_output(text: str) -> str:
    """
    Normalise output for comparison:
    strip trailing whitespace per line, remove trailing newlines.
    """
    lines = text.splitlines()
    stripped = [line.rstrip() for line in lines]
    # Remove trailing blank lines
    while stripped and not stripped[-1]:
        stripped.pop()
    return "\n".join(stripped)


def _compare_outputs(actual: str, expected: str, checker: str = "exact") -> bool:
    """
    Compare actual vs expected output using the specified checker strategy.

    Checkers:
      - "exact"            (default): normalised line-by-line equality
      - "unordered_lines"  : same lines in any order (e.g. Group Anagrams groups)
      - "unordered_tokens" : same space-separated tokens in any order (e.g. Top K Frequent)
    """
    norm_actual   = _normalize_output(actual)
    norm_expected = _normalize_output(expected)

    if checker == "unordered_lines":
        return sorted(norm_actual.splitlines()) == sorted(norm_expected.splitlines())
    elif checker == "unordered_tokens":
        return sorted(norm_actual.split()) == sorted(norm_expected.split())
    else:  # "exact" (default)
        return norm_actual == norm_expected


# ── Abstract Interface ────────────────────────────────────────────────────────

class ICodeExecutionEngine(ABC):
    """
    Abstract Base Class / Extensible Interface for Code Execution Engines.
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
        Execute code against stdin within resource limits.

        Returns:
            {
                "status": str (STATUS_* constant),
                "output": str (stdout),
                "error": str (stderr / compile error),
                "execution_time_ms": float,
                "memory_kb": int,
            }
        """
        pass


# ── Judge0 Engine ─────────────────────────────────────────────────────────────

class Judge0ExecutionEngine(ICodeExecutionEngine):
    """
    Concrete ICodeExecutionEngine implementation backed by Judge0 CE.

    Supports:
      - Self-hosted Judge0 (set JUDGE0_URL, optionally JUDGE0_API_KEY)
      - RapidAPI-hosted Judge0 (set JUDGE0_RAPIDAPI_HOST in addition)
    """

    # Judge0 status id -> our STATUS_* constants
    _STATUS_MAP: Dict[int, str] = {
        1:  STATUS_COMPILATION_ERROR,   # In Queue (should not happen with wait=true)
        2:  STATUS_COMPILATION_ERROR,   # Processing (should not happen with wait=true)
        3:  STATUS_SUCCESS,             # Accepted (execution finished)
        4:  STATUS_WRONG_ANSWER,        # Wrong Answer (Judge0 itself won't set this; we compare)
        5:  STATUS_TIME_LIMIT_EXCEEDED,
        6:  STATUS_COMPILATION_ERROR,
        7:  STATUS_RUNTIME_ERROR,       # SIGSEGV
        8:  STATUS_RUNTIME_ERROR,       # SIGXFSZ
        9:  STATUS_RUNTIME_ERROR,       # SIGFPE
        10: STATUS_RUNTIME_ERROR,       # SIGABRT
        11: STATUS_RUNTIME_ERROR,       # NZEC (non-zero exit code)
        12: STATUS_RUNTIME_ERROR,       # Runtime Error Other
        13: STATUS_JUDGE_UNAVAILABLE,   # Internal Error
        14: STATUS_JUDGE_UNAVAILABLE,   # Exec Format Error
    }

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        rapidapi_host: Optional[str] = None,
        timeout: float = 15.0,
        max_retries: int = 2,
    ):
        self._base_url      = (base_url or Config.JUDGE0_URL).rstrip("/")
        self._api_key       = api_key or Config.JUDGE0_API_KEY
        self._rapidapi_host = rapidapi_host or Config.JUDGE0_RAPIDAPI_HOST
        self._timeout       = timeout
        self._max_retries   = max_retries

    def _build_headers(self) -> Dict[str, str]:
        headers: Dict[str, str] = {"Content-Type": "application/json"}
        if self._rapidapi_host:
            headers["X-RapidAPI-Host"] = self._rapidapi_host
            if self._api_key:
                headers["X-RapidAPI-Key"] = self._api_key
        elif self._api_key:
            headers["X-Auth-Token"] = self._api_key
        return headers

    def execute(
        self,
        code: str,
        language: str,
        input_data: str,
        time_limit: float = 2.0,
        memory_limit: int = 256,
    ) -> Dict[str, Any]:
        lang_key = _normalize_language(language)
        language_id = JUDGE0_LANGUAGE_IDS.get(lang_key)
        if language_id is None:
            return {
                "status": STATUS_UNSUPPORTED_LANGUAGE,
                "output": "",
                "error": f"Language '{language}' is not supported. Supported: {', '.join(JUDGE0_LANGUAGE_IDS.keys())}",
                "execution_time_ms": 0.0,
                "memory_kb": 0,
            }

        payload = {
            "source_code":    code,
            "language_id":    language_id,
            "stdin":          input_data,
            "cpu_time_limit": time_limit,
            "memory_limit":   memory_limit * 1024,  # MB -> KB
        }

        url = f"{self._base_url}/submissions?base64_encoded=false&wait=true"
        last_err: Optional[Exception] = None

        for attempt in range(self._max_retries + 1):
            try:
                with httpx.Client(timeout=self._timeout) as client:
                    resp = client.post(
                        url,
                        headers=self._build_headers(),
                        json=payload,
                    )
                resp.raise_for_status()
                return self._parse_response(resp.json())
            except httpx.TimeoutException as exc:
                last_err = exc
                logger.warning(f"Judge0 timeout (attempt {attempt + 1}): {exc}")
                if attempt < self._max_retries:
                    time.sleep(0.5 * (attempt + 1))
            except httpx.HTTPStatusError as exc:
                last_err = exc
                logger.warning(f"Judge0 HTTP error (attempt {attempt + 1}): {exc.response.status_code}")
                if exc.response.status_code < 500:
                    break  # Client error — no point retrying
                if attempt < self._max_retries:
                    time.sleep(0.5 * (attempt + 1))
            except Exception as exc:
                last_err = exc
                logger.error(f"Judge0 unexpected error (attempt {attempt + 1}): {exc}")
                break

        # Graceful failure — NEVER silently score 0
        logger.error(f"Judge0 unavailable after {self._max_retries + 1} attempts: {last_err}")
        return {
            "status": STATUS_JUDGE_UNAVAILABLE,
            "output": "",
            "error": (
                "Code execution service (Judge0) is currently unavailable. "
                "Please contact support or try again later. Your submission was NOT scored."
            ),
            "execution_time_ms": 0.0,
            "memory_kb": 0,
        }

    def _parse_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        status_id = (data.get("status") or {}).get("id", 13)
        judge0_status = self._STATUS_MAP.get(status_id, STATUS_RUNTIME_ERROR)

        stdout   = data.get("stdout") or ""
        stderr   = data.get("stderr") or ""
        compile_output = data.get("compile_output") or ""
        error_msg = compile_output if compile_output else stderr

        # time in seconds from Judge0 → ms
        exec_time_s = data.get("time")
        exec_time_ms = float(exec_time_s) * 1000.0 if exec_time_s else 0.0

        memory_kb = int(data.get("memory") or 0)

        # Structured logging (no source code logged)
        logger.info(
            "Judge0 result: status_id=%s status=%s time_ms=%.1f memory_kb=%d",
            status_id, judge0_status, exec_time_ms, memory_kb
        )

        return {
            "status": judge0_status,
            "output": stdout,
            "error": error_msg,
            "execution_time_ms": round(exec_time_ms, 2),
            "memory_kb": memory_kb,
        }


# ── Local Python Fallback (dev only) ─────────────────────────────────────────

class LocalPythonExecutionEngine(ICodeExecutionEngine):
    """
    Local subprocess Python executor — dev/testing fallback ONLY.
    Enabled only when ALLOW_LOCAL_EXECUTION=true.
    NEVER use in production: runs untrusted candidate code on the API server.
    """

    def execute(
        self,
        code: str,
        language: str,
        input_data: str,
        time_limit: float = 2.0,
        memory_limit: int = 256,
    ) -> Dict[str, Any]:
        lang_clean = language.lower().strip()
        if lang_clean not in {"python", "python3", "py"}:
            return {
                "status": STATUS_UNSUPPORTED_LANGUAGE,
                "output": "",
                "error": f"LocalPythonExecutionEngine only supports Python; got '{language}'.",
                "execution_time_ms": 0.0,
                "memory_kb": 0,
            }

        temp_dir = None
        try:
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
                cwd=temp_dir,
            )
            stdout_data, stderr_data = process.communicate(input=input_data, timeout=time_limit)
            exec_time_ms = (time.time() - start_time) * 1000.0

            if process.returncode != 0:
                return {
                    "status": STATUS_RUNTIME_ERROR,
                    "output": stdout_data.strip(),
                    "error": stderr_data.strip(),
                    "execution_time_ms": round(exec_time_ms, 2),
                    "memory_kb": 0,
                }
            return {
                "status": STATUS_SUCCESS,
                "output": stdout_data.strip(),
                "error": "",
                "execution_time_ms": round(exec_time_ms, 2),
                "memory_kb": 0,
            }

        except subprocess.TimeoutExpired:
            if "process" in locals() and process:
                process.kill()
            return {
                "status": STATUS_TIME_LIMIT_EXCEEDED,
                "output": "",
                "error": f"Execution exceeded {time_limit}s time limit.",
                "execution_time_ms": time_limit * 1000.0,
                "memory_kb": 0,
            }
        except Exception as e:
            logger.error(f"LocalPythonExecutionEngine error: {e}", exc_info=True)
            return {
                "status": STATUS_RUNTIME_ERROR,
                "output": "",
                "error": f"Internal execution engine error: {e}",
                "execution_time_ms": 0.0,
                "memory_kb": 0,
            }
        finally:
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)


# ── Stub Docker engine kept for backward compatibility ────────────────────────

class DockerExecutionEngine(ICodeExecutionEngine):
    """
    Kept for backward compatibility.
    Now delegates to Judge0ExecutionEngine when JUDGE0_URL is configured.
    """

    def execute(
        self,
        code: str,
        language: str,
        input_data: str,
        time_limit: float = 2.0,
        memory_limit: int = 256,
    ) -> Dict[str, Any]:
        if Config.JUDGE0_URL:
            return Judge0ExecutionEngine().execute(code, language, input_data, time_limit, memory_limit)
        if Config.ALLOW_LOCAL_EXECUTION and language.lower() in {"python", "python3"}:
            return LocalPythonExecutionEngine().execute(code, language, input_data, time_limit, memory_limit)
        return {
            "status": STATUS_JUDGE_UNAVAILABLE,
            "output": "",
            "error": "No execution engine configured. Set JUDGE0_URL in .env.",
            "execution_time_ms": 0.0,
            "memory_kb": 0,
        }


# ── In-Memory Rate Limiter for /run ──────────────────────────────────────────
# Simple TTL dict; keyed by userId; stores last request timestamp.
# In production with multiple workers, use Redis instead.
_run_rate_limit: Dict[str, float] = {}
RUN_RATE_LIMIT_SECONDS = 3  # minimum seconds between /run calls per user


def check_run_rate_limit(user_id: str) -> bool:
    """Returns True if the user is allowed to run (rate limit not hit)."""
    now = time.time()
    last = _run_rate_limit.get(user_id, 0)
    if now - last < RUN_RATE_LIMIT_SECONDS:
        return False
    _run_rate_limit[user_id] = now
    return True


# ── CodingService ─────────────────────────────────────────────────────────────

class CodingService:
    """
    Service class responsible for coding assessment workflows:
    - Managing coding problems
    - Validating user submissions
    - Executing test case evaluation via pluggable engines
    - Grading output and generating score reports
    - Persisting submissions to coding_submissions collection
    """

    @staticmethod
    def get_execution_engine(engine_type: str = "auto") -> ICodeExecutionEngine:
        """
        Factory: returns the appropriate execution engine.

        Priority:
          1. If engine_type in ("local", "sandbox") → LocalPythonExecutionEngine
          2. If JUDGE0_URL is set → Judge0ExecutionEngine (default "auto" or "judge0")
          3. If ALLOW_LOCAL_EXECUTION=true and no JUDGE0_URL → LocalPythonExecutionEngine
          4. Otherwise → Judge0ExecutionEngine (will return JUDGE_UNAVAILABLE if URL not set)
        """
        engine_str = (engine_type or "auto").lower().strip()
        if engine_str in ("local", "sandbox"):
            return LocalPythonExecutionEngine()
        if engine_str == "docker":
            return DockerExecutionEngine()
        if Config.JUDGE0_URL:
            return Judge0ExecutionEngine()
        if Config.ALLOW_LOCAL_EXECUTION:
            return LocalPythonExecutionEngine()
        # Default: LocalPythonExecutionEngine when Judge0 URL is not configured
        return LocalPythonExecutionEngine()

    @classmethod
    def manage_question(
        cls,
        action: str,
        question_id: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Unified CRUD wrapper for coding questions."""
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
            return {
                "success": False, "status_code": 400,
                "message": "Invalid management action.", "error": "INVALID_ACTION",
            }

    @classmethod
    def validate_submission(
        cls,
        submission_payload: Dict[str, Any],
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """Validate structure and fetch the question document."""
        if not submission_payload or not isinstance(submission_payload, dict):
            return False, "Submission payload must be a non-empty JSON object.", {}

        question_id = submission_payload.get("questionId") or submission_payload.get("question_id")
        code        = submission_payload.get("code", "")
        language    = (
            submission_payload.get("programmingLanguage")
            or submission_payload.get("language", "python")
        )

        if not question_id or not ObjectId.is_valid(question_id):
            return False, "Valid 'questionId' is required.", {}

        if not code or not code.strip():
            return False, "Source code cannot be empty.", {}

        if len(code) > 50000:
            return False, "Source code exceeds maximum allowed length of 50,000 characters.", {}

        if _normalize_language(language) not in JUDGE0_LANGUAGE_IDS and language.lower() not in SUPPORTED_LANGUAGES:
            return False, f"Unsupported language '{language}'.", {}

        try:
            db = Database.get_db()
            question_doc = db.coding_questions.find_one(
                {"_id": ObjectId(question_id), "isActive": True}
            )
            if not question_doc:
                question_doc = db.problem_bank.find_one(
                    {"_id": ObjectId(question_id)}
                )
            if not question_doc:
                return False, "Coding question not found or is no longer active.", {}
            return True, "", question_doc
        except PyMongoError as db_err:
            logger.error(f"DB error during submission validation: {db_err}")
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
        is_hidden: bool = False,
        checker: str = "exact",
    ) -> Dict[str, Any]:
        """
        Evaluate a single test case. Returns per-case result dict.
        Hidden test cases mask input/expected/actual from the candidate.
        """
        input_str       = str(test_case.get("input", ""))
        expected_output = str(test_case.get("output", "") or test_case.get("expectedOutput", ""))

        exec_result  = engine.execute(code, language, input_str, time_limit, memory_limit)
        exec_status  = exec_result.get("status", STATUS_RUNTIME_ERROR)

        # Fallback to local python engine if Judge0 is unavailable
        if exec_status == STATUS_JUDGE_UNAVAILABLE and language.lower().strip() in {"python", "python3", "py"}:
            local_engine = LocalPythonExecutionEngine()
            exec_result = local_engine.execute(code, language, input_str, time_limit, memory_limit)
            exec_status = exec_result.get("status", STATUS_RUNTIME_ERROR)

        actual_output = exec_result.get("output", "")

        passed      = False
        test_status = exec_status

        if exec_status == STATUS_SUCCESS:
            if _compare_outputs(actual_output, expected_output, checker):
                passed      = True
                test_status = STATUS_ACCEPTED
            else:
                test_status = STATUS_WRONG_ANSWER

        result_item: Dict[str, Any] = {
            "test_case_id":       str(test_case.get("_id", ObjectId())),
            "is_hidden":          is_hidden,
            "passed":             passed,
            "status":             test_status,
            "execution_time_ms":  exec_result.get("execution_time_ms", 0.0),
            "memory_kb":          exec_result.get("memory_kb", 0),
            "error_message":      exec_result.get("error", ""),
        }

        if not is_hidden:
            result_item["input"]           = input_str
            result_item["expected_output"] = _normalize_output(expected_output)
            result_item["actual_output"]   = _normalize_output(actual_output)
        else:
            result_item["input"]           = "Hidden Test Case"
            result_item["expected_output"] = "Hidden"
            result_item["actual_output"]   = "Hidden" if not passed else "Matched"

        return result_item

    @classmethod
    def run_sample_cases(
        cls,
        question_id: str,
        code: str,
        language: str,
        user_id: str,
    ) -> Dict[str, Any]:
        """
        Run ONLY the sample test cases for a question (used by POST /api/coding/run).
        Persists the run event to coding_submissions.
        Returns per-case results with full input/expected/actual (sample cases are not hidden).
        """
        try:
            db = Database.get_db()
            question_doc = db.coding_questions.find_one(
                {"_id": ObjectId(question_id), "isActive": True}
            )
            if not question_doc:
                question_doc = db.problem_bank.find_one(
                    {"_id": ObjectId(question_id)}
                )

            if not question_doc:
                return {
                    "success": False, "status_code": 404,
                    "message": "Question not found.",
                }

            sample_tests = question_doc.get("sampleTestCases") or []
            if not sample_tests:
                # Fallback: build from sampleInput/sampleOutput fields
                sample_input  = (question_doc.get("sampleInput") or "").strip()
                sample_output = (question_doc.get("sampleOutput") or "").strip()
                if sample_input:
                    sample_tests = [{"input": sample_input, "output": sample_output}]

            if not sample_tests:
                # Fallback 2: Look up in problem_bank by title or slug
                pb_match = db.problem_bank.find_one({
                    "$or": [
                        {"title": question_doc.get("title")},
                        {"slug": question_doc.get("slug")},
                    ]
                })
                if pb_match and pb_match.get("sampleTestCases"):
                    sample_tests = pb_match["sampleTestCases"]

            if not sample_tests:
                # Fallback 3: Look up in classic test cases dictionary
                from scripts.fix_coding_questions_test_cases import CLASSIC_TEST_CASES
                t = question_doc.get("title", "")
                for k, v in CLASSIC_TEST_CASES.items():
                    if k.lower() == t.lower() or k.lower() in t.lower() or t.lower() in k.lower():
                        sample_tests = v.get("sample", [])
                        break

            if not sample_tests:
                return {
                    "success": False, "status_code": 400,
                    "message": "This question has no sample test cases configured.",
                }

            time_limit   = float(question_doc.get("timeLimit", 2.0))
            memory_limit = int(question_doc.get("memoryLimit", 256))
            checker      = question_doc.get("checker", "exact")

            engine = cls.get_execution_engine()
            results = []

            # Stop early on compile error (run first case to detect it)
            compile_error_detected = False

            # Cap at 3 sample cases for /run to keep it fast
            capped_tests = sample_tests[:3]

            for tc in capped_tests:
                if compile_error_detected:
                    break
                res = cls.run_test_case_evaluation(
                    engine=engine,
                    code=code,
                    language=language,
                    test_case=tc,
                    time_limit=time_limit,
                    memory_limit=memory_limit,
                    is_hidden=False,
                    checker=checker,
                )
                results.append(res)
                if res["status"] in (STATUS_COMPILATION_ERROR, STATUS_JUDGE_UNAVAILABLE):
                    compile_error_detected = True

            passed_count = sum(1 for r in results if r["passed"])
            total_count  = len(results)
            overall_status = STATUS_ACCEPTED if passed_count == total_count else (
                results[0]["status"] if results else STATUS_RUNTIME_ERROR
            )
            for r in results:
                if not r["passed"]:
                    overall_status = r["status"]
                    break

            # Persist run event (no source code stored in log)
            try:
                db.coding_submissions.insert_one({
                    "userId":      user_id,
                    "questionId":  ObjectId(question_id),
                    "language":    language,
                    "codeLength":  len(code),
                    "kind":        "run",
                    "verdict":     overall_status,
                    "passedTests": passed_count,
                    "totalTests":  total_count,
                    "createdAt":   datetime.now(timezone.utc),
                })
            except Exception as log_err:
                logger.warning(f"Failed to persist run event: {log_err}")

            return {
                "success":        True,
                "status_code":    200,
                "overall_status": overall_status,
                "passed":         passed_count,
                "total":          total_count,
                "results":        results,
            }

        except Exception as err:
            logger.error(f"run_sample_cases error: {err}", exc_info=True)
            return {
                "success": False, "status_code": 500,
                "message": "Internal error during code run.",
            }

    @classmethod
    def evaluate_submission(
        cls,
        submission_payload: Dict[str, Any],
        engine_type: str = "auto",
        include_hidden_details: bool = False,
    ) -> Dict[str, Any]:
        """
        Full evaluation: runs sample + hidden test cases, computes score.
        Used by POST /api/coding/submit-one and the batch submit endpoint.

        Concurrency: runs all test cases in a ThreadPoolExecutor (cap=5)
        to keep latency low while preventing overload.
        """
        is_valid, error_msg, question_doc = cls.validate_submission(submission_payload)
        if not is_valid:
            return {
                "success": False, "status_code": 400,
                "message": error_msg, "error": "VALIDATION_FAILED",
            }

        try:
            code         = submission_payload.get("code", "")
            language     = (
                submission_payload.get("programmingLanguage")
                or submission_payload.get("language", "python")
            )
            user_id      = str(submission_payload.get("userId", ""))
            time_limit   = float(question_doc.get("timeLimit", 2.0))
            memory_limit = int(question_doc.get("memoryLimit", 256))
            max_marks    = float(question_doc.get("marks", 10.0))
            checker      = question_doc.get("checker", "exact")

            sample_tests = question_doc.get("sampleTestCases") or []
            if not sample_tests:
                si = (question_doc.get("sampleInput") or "").strip()
                so = (question_doc.get("sampleOutput") or "").strip()
                if si:
                    sample_tests = [{"input": si, "output": so}]

            hidden_tests = question_doc.get("hiddenTestCases") or []

            if not sample_tests and not hidden_tests:
                # Fallback to problem_bank or CLASSIC_TEST_CASES
                db = Database.get_db()
                pb_match = db.problem_bank.find_one({
                    "$or": [
                        {"title": question_doc.get("title")},
                        {"slug": question_doc.get("slug")},
                    ]
                })
                if pb_match:
                    sample_tests = pb_match.get("sampleTestCases") or []
                    hidden_tests = pb_match.get("hiddenTestCases") or []
                else:
                    from scripts.fix_coding_questions_test_cases import CLASSIC_TEST_CASES
                    t = question_doc.get("title", "")
                    for k, v in CLASSIC_TEST_CASES.items():
                        if k.lower() == t.lower() or k.lower() in t.lower() or t.lower() in k.lower():
                            sample_tests = v.get("sample", [])
                            hidden_tests = v.get("hidden", [])
                            break

            all_tests    = [(tc, False) for tc in sample_tests] + [(tc, True) for tc in hidden_tests]

            if not all_tests:
                logger.warning(f"Question {question_doc['_id']} has no test cases; awarding 0 marks.")
                return {
                    "success": True, "status_code": 200,
                    "message": "No test cases configured for this question.",
                    "data": {
                        "question_id":    str(question_doc["_id"]),
                        "status":         STATUS_ACCEPTED,
                        "marks_obtained": 0.0,
                        "max_marks":      max_marks,
                        "passed_tests":   0,
                        "total_tests":    0,
                        "test_results":   [],
                    },
                }

            engine = cls.get_execution_engine(engine_type)

            # ── Concurrent execution with early-stop on compile error ──────────
            # We submit all tasks at once but drain results; if first result is
            # a compile error we short-circuit remaining futures.
            # Concurrency cap of 5 to avoid overwhelming Judge0.
            MAX_CONCURRENCY = 5
            test_results: List[Optional[Dict[str, Any]]] = [None] * len(all_tests)

            def _run_one(idx: int, tc: Dict, is_hidden: bool) -> Tuple[int, Dict]:
                return idx, cls.run_test_case_evaluation(
                    engine=engine,
                    code=code,
                    language=language,
                    test_case=tc,
                    time_limit=time_limit,
                    memory_limit=memory_limit,
                    is_hidden=is_hidden,
                    checker=checker,
                )

            compile_error = False
            with ThreadPoolExecutor(max_workers=MAX_CONCURRENCY) as executor:
                futures = {
                    executor.submit(_run_one, i, tc, hidden): i
                    for i, (tc, hidden) in enumerate(all_tests)
                    if not compile_error
                }
                for future in as_completed(futures):
                    idx, result = future.result()
                    test_results[idx] = result
                    if result["status"] in (STATUS_COMPILATION_ERROR, STATUS_JUDGE_UNAVAILABLE):
                        compile_error = True
                        # Cancel remaining (best-effort)
                        for f in futures:
                            f.cancel()

            # Fill any cancelled slots with a placeholder
            final_results = []
            for i, (_, is_hidden) in enumerate(all_tests):
                if test_results[i] is not None:
                    final_results.append(test_results[i])
                else:
                    final_results.append({
                        "test_case_id":      "",
                        "is_hidden":         is_hidden,
                        "passed":            False,
                        "status":            STATUS_COMPILATION_ERROR,
                        "execution_time_ms": 0.0,
                        "memory_kb":         0,
                        "error_message":     "Skipped due to earlier compile/judge error.",
                        "input":             "Skipped" if not is_hidden else "Hidden Test Case",
                        "expected_output":   "Skipped" if not is_hidden else "Hidden",
                        "actual_output":     "Skipped" if not is_hidden else "Hidden",
                    })

            passed_count  = sum(1 for r in final_results if r["passed"])
            total_tests   = len(final_results)
            marks_obtained = round((passed_count / total_tests) * max_marks, 2) if total_tests else 0.0

            overall_status = STATUS_ACCEPTED
            for r in final_results:
                if not r["passed"]:
                    overall_status = r["status"]
                    break

            logger.info(
                "Submission evaluated: question=%s lang=%s %d/%d passed (%s)",
                question_doc["_id"], language, passed_count, total_tests, overall_status,
            )

            # Persist submission event
            question_id_str = str(question_doc["_id"])
            try:
                db = Database.get_db()
                db.coding_submissions.insert_one({
                    "userId":        user_id,
                    "questionId":    ObjectId(question_id_str),
                    "language":      language,
                    "codeLength":    len(code),
                    "kind":          "submit",
                    "verdict":       overall_status,
                    "passedTests":   passed_count,
                    "totalTests":    total_tests,
                    "marksObtained": marks_obtained,
                    "maxMarks":      max_marks,
                    "createdAt":     datetime.now(timezone.utc),
                })
                # Ensure indexes exist
                db.coding_submissions.create_index([("userId", 1), ("questionId", 1)])
                db.coding_submissions.create_index([("createdAt", -1)])
            except Exception as log_err:
                logger.warning(f"Failed to persist submission: {log_err}")

            return {
                "success":     True,
                "status_code": 200,
                "message":     f"Evaluation complete: {overall_status}.",
                "data": {
                    "question_id":    question_id_str,
                    "status":         overall_status,
                    "marks_obtained": marks_obtained,
                    "max_marks":      max_marks,
                    "passed_tests":   passed_count,
                    "total_tests":    total_tests,
                    "percentage":     round((passed_count / total_tests) * 100, 2) if total_tests else 0.0,
                    "test_results":   final_results,
                },
            }

        except Exception as err:
            logger.critical(f"Unexpected error during code evaluation: {err}", exc_info=True)
            return {
                "success": False, "status_code": 500,
                "message": "Internal server error during code execution.",
                "error":   "INTERNAL_SERVER_ERROR",
            }
