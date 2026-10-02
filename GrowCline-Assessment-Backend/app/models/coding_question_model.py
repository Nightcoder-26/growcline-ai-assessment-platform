"""
Coding Question Model
Defines document schema and formatting methods for coding_questions collection.

Security note: response() strips hiddenTestCases and referenceSolution by default.
Pass include_hidden=True only for server-side evaluation (never from client-facing routes).
"""

from datetime import datetime, timezone
from bson import ObjectId
from typing import Any, Dict, List, Optional


class CodingQuestion:
    """Coding Question Model"""

    @staticmethod
    def create_question(
        title: str,
        problem_statement: str,
        programming_language: str = "Python",
        difficulty: str = "Easy",
        input_format: str = "",
        output_format: str = "",
        constraints: str = "",
        sample_input: str = "",
        sample_output: str = "",
        test_cases: Optional[List[Dict]] = None,
        hidden_test_cases: Optional[List[Dict]] = None,
        marks: int = 10,
        category: str = "Algorithms",
        sample_test_cases: Optional[List[Dict]] = None,
        time_limit: float = 2.0,
        memory_limit: int = 256,
        explanation: str = "",
        tags: Optional[List[str]] = None,
        created_by: Optional[str] = None,
        checker: str = "exact",
        reference_solution: str = "",
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        tc  = test_cases if test_cases is not None else (sample_test_cases or [])
        htc = hidden_test_cases if hidden_test_cases is not None else []
        return {
            "_id":                ObjectId(),
            "title":              title,
            "programmingLanguage": programming_language or "Python",
            "difficulty":         difficulty or "Easy",
            "problemStatement":   problem_statement,
            "inputFormat":        input_format or "",
            "outputFormat":       output_format or "",
            "constraints":        constraints or "",
            "sampleInput":        sample_input or "",
            "sampleOutput":       sample_output or "",
            "testCases":          tc,
            "sampleTestCases":    tc,
            "hiddenTestCases":    htc,
            # Server-only field — never returned in response()
            "referenceSolution":  reference_solution or "",
            "checker":            checker or "exact",
            "marks":              int(marks) if marks is not None else 10,
            "category":           category or "Algorithms",
            "timeLimit":          float(time_limit) if time_limit is not None else 2.0,
            "memoryLimit":        int(memory_limit) if memory_limit is not None else 256,
            "explanation":        explanation or "",
            "tags":               tags if tags else [],
            "isActive":           True,
            "createdBy":          ObjectId(created_by) if created_by else None,
            "createdAt":          now,
            "updatedAt":          now,
        }

    @staticmethod
    def response(
        question: Optional[Dict[str, Any]],
        include_hidden: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """
        Serialize a question document for API responses.

        Args:
            question: Raw MongoDB document.
            include_hidden: If True, include hiddenTestCases (server-side evaluation only).
                            NEVER set True for client-facing endpoints.
        """
        if not question:
            return None

        created_at = question.get("createdAt")
        if isinstance(created_at, datetime):
            created_at = created_at.isoformat()

        updated_at = question.get("updatedAt")
        if isinstance(updated_at, datetime):
            updated_at = updated_at.isoformat()

        result: Dict[str, Any] = {
            "_id":                str(question["_id"]),
            "id":                 str(question["_id"]),
            "title":              question.get("title", ""),
            "programmingLanguage": question.get("programmingLanguage", "Python"),
            "difficulty":         question.get("difficulty", "Easy"),
            "problemStatement":   question.get("problemStatement", ""),
            "inputFormat":        question.get("inputFormat", ""),
            "outputFormat":       question.get("outputFormat", ""),
            "constraints":        question.get("constraints", ""),
            "sampleInput":        question.get("sampleInput", ""),
            "sampleOutput":       question.get("sampleOutput", ""),
            # testCases = sample cases only (safe to expose)
            "testCases":          question.get("testCases", question.get("sampleTestCases", [])),
            "marks":              question.get("marks", 10),
            "category":           question.get("category", "Algorithms"),
            "checker":            question.get("checker", "exact"),
            "timeLimit":          question.get("timeLimit", 2.0),
            "memoryLimit":        question.get("memoryLimit", 256),
            "explanation":        question.get("explanation", ""),
            "tags":               question.get("tags", []),
            "isActive":           question.get("isActive", True),
            "createdAt":          created_at,
            "updatedAt":          updated_at,
            # hiddenTestCases and referenceSolution are NEVER included unless explicitly requested
        }

        if include_hidden:
            result["hiddenTestCases"]   = question.get("hiddenTestCases", [])
            result["referenceSolution"] = question.get("referenceSolution", "")

        return result