"""
Coding Question Model
Defines document schema and formatting methods for coding_questions collection.
"""

from datetime import datetime, timezone
from bson import ObjectId


class CodingQuestion:
    """Coding Question Model"""

    @staticmethod
    def create_question(
        title,
        problem_statement,
        programming_language="Python",
        difficulty="Easy",
        input_format="",
        output_format="",
        constraints="",
        sample_input="",
        sample_output="",
        test_cases=None,
        hidden_test_cases=None,
        marks=10,
        category="Algorithms",
        sample_test_cases=None,
        time_limit=2.0,
        memory_limit=256,
        explanation="",
        tags=None,
        created_by=None,
    ):
        now = datetime.now(timezone.utc)
        tc = test_cases if test_cases is not None else (sample_test_cases or [])
        htc = hidden_test_cases if hidden_test_cases is not None else []
        return {
            "_id": ObjectId(),
            "title": title,
            "programmingLanguage": programming_language or "Python",
            "difficulty": difficulty or "Easy",
            "problemStatement": problem_statement,
            "inputFormat": input_format or "",
            "outputFormat": output_format or "",
            "constraints": constraints or "",
            "sampleInput": sample_input or "",
            "sampleOutput": sample_output or "",
            "testCases": tc,
            "sampleTestCases": tc,
            "hiddenTestCases": htc,
            "marks": int(marks) if marks is not None else 10,
            "category": category or "Algorithms",
            "timeLimit": float(time_limit) if time_limit is not None else 2.0,
            "memoryLimit": int(memory_limit) if memory_limit is not None else 256,
            "explanation": explanation or "",
            "tags": tags if tags else [],
            "isActive": True,
            "createdBy": ObjectId(created_by) if created_by else None,
            "createdAt": now,
            "updatedAt": now,
        }

    @staticmethod
    def response(question):
        if not question:
            return None

        created_at = question.get("createdAt")
        if isinstance(created_at, datetime):
            created_at = created_at.isoformat()

        updated_at = question.get("updatedAt")
        if isinstance(updated_at, datetime):
            updated_at = updated_at.isoformat()

        return {
            "_id": str(question["_id"]),
            "id": str(question["_id"]),
            "title": question.get("title", ""),
            "programmingLanguage": question.get("programmingLanguage", "Python"),
            "difficulty": question.get("difficulty", "Easy"),
            "problemStatement": question.get("problemStatement", ""),
            "inputFormat": question.get("inputFormat", ""),
            "outputFormat": question.get("outputFormat", ""),
            "constraints": question.get("constraints", ""),
            "sampleInput": question.get("sampleInput", ""),
            "sampleOutput": question.get("sampleOutput", ""),
            "testCases": question.get("testCases", question.get("sampleTestCases", [])),
            "hiddenTestCases": question.get("hiddenTestCases", []),
            "marks": question.get("marks", 10),
            "category": question.get("category", "Algorithms"),
            "timeLimit": question.get("timeLimit", 2.0),
            "memoryLimit": question.get("memoryLimit", 256),
            "explanation": question.get("explanation", ""),
            "tags": question.get("tags", []),
            "isActive": question.get("isActive", True),
            "createdAt": created_at,
            "updatedAt": updated_at,
        }