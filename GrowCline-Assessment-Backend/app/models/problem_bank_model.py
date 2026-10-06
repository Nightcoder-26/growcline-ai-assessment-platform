"""
Problem Bank Model
Defines the schema, sanitization, and response formatting for curated coding challenges
stored in the `problem_bank` collection.

Status lifecycle:
  draft -> verified -> approved (or rejected)

Security & Integrity:
  Candidate-facing APIs must NEVER return:
    - referenceSolution
    - bruteForceSolution
    - inputGenerator
    - mutations / wrongSolutions
    - hiddenTestCases
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from bson import ObjectId


STATUS_DRAFT = "draft"
STATUS_VERIFIED = "verified"
STATUS_APPROVED = "approved"
STATUS_REJECTED = "rejected"
VALID_STATUSES = {STATUS_DRAFT, STATUS_VERIFIED, STATUS_APPROVED, STATUS_REJECTED}

CHECKER_EXACT = "exact"
CHECKER_UNORDERED_LINES = "unordered_lines"
CHECKER_UNORDERED_TOKENS = "unordered_tokens"
VALID_CHECKERS = {CHECKER_EXACT, CHECKER_UNORDERED_LINES, CHECKER_UNORDERED_TOKENS}


class ProblemBank:
    """Problem Bank Model for curated coding challenges."""

    @staticmethod
    def create_problem(
        title: str,
        statement: str,
        input_format: str = "",
        output_format: str = "",
        constraints: str = "",
        topic: str = "Algorithms",
        category: Optional[str] = None,
        difficulty: str = "Medium",
        tags: Optional[List[str]] = None,
        languages: Optional[List[str]] = None,
        domains: Optional[List[str]] = None,
        checker: str = CHECKER_EXACT,
        time_limit: float = 2.0,
        memory_limit: int = 256,
        sample_test_cases: Optional[List[Dict[str, str]]] = None,
        hidden_test_cases: Optional[List[Dict[str, str]]] = None,
        status: str = STATUS_DRAFT,
        source: str = "curated_seed",
        created_by: Optional[str] = None,
        reviewed_by: Optional[str] = None,
        version: int = 1,
        # Server-only fields
        reference_solution: str = "",
        brute_force_solution: str = "",
        input_generator: str = "",
        mutations: Optional[List[Dict[str, str]]] = None,
        edge_cases: Optional[List[str]] = None,
        verification_report: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Constructs a clean document for insertion into problem_bank collection."""
        now = datetime.now(timezone.utc)
        clean_status = status.lower() if status and status.lower() in VALID_STATUSES else STATUS_DRAFT
        clean_checker = checker.lower() if checker and checker.lower() in VALID_CHECKERS else CHECKER_EXACT

        sample_tcs = sample_test_cases or []
        hidden_tcs = hidden_test_cases or []

        # Derive sampleInput and sampleOutput from first sample case for backward compatibility
        sample_input = sample_tcs[0].get("input", "") if sample_tcs else ""
        sample_output = sample_tcs[0].get("output", "") if sample_tcs else ""

        return {
            "_id": ObjectId(),
            "title": (title or "").strip(),
            "statement": (statement or "").strip(),
            "problemStatement": (statement or "").strip(),  # alias for backward compat
            "inputFormat": (input_format or "").strip(),
            "outputFormat": (output_format or "").strip(),
            "constraints": (constraints or "").strip(),
            "topic": (topic or "Algorithms").strip(),
            "category": (category or topic or "Algorithms").strip(),
            "difficulty": (difficulty or "Medium").capitalize(),
            "tags": [str(t).strip() for t in (tags or []) if str(t).strip()],
            "languages": [str(l).strip() for l in (languages or ["Python", "JavaScript", "Java", "C++"])],
            "domains": [str(d).strip() for d in (domains or ["General", "Backend", "Full Stack"])],
            "checker": clean_checker,
            "timeLimit": float(time_limit or 2.0),
            "memoryLimit": int(memory_limit or 256),
            "sampleInput": sample_input,
            "sampleOutput": sample_output,
            "sampleTestCases": sample_tcs,
            "hiddenTestCases": hidden_tcs,
            "status": clean_status,
            "source": source or "curated_seed",
            "createdBy": created_by or "system",
            "reviewedBy": reviewed_by,
            "version": int(version or 1),
            "isActive": True,
            "createdAt": now,
            "updatedAt": now,
            # ── Server-Only Fields (NEVER returned to candidates) ──────────────
            "referenceSolution": reference_solution or "",
            "bruteForceSolution": brute_force_solution or "",
            "inputGenerator": input_generator or "",
            "mutations": mutations or [],
            "edgeCases": edge_cases or [],
            "verificationReport": verification_report or None,
            "marks": 10,
        }

    @staticmethod
    def candidate_response(doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Formats problem document for candidate view.
        CRITICAL SECURITY: Strips all server-only fields (referenceSolution,
        bruteForceSolution, inputGenerator, mutations, hiddenTestCases).
        """
        if not doc:
            return None

        oid = doc.get("_id")
        qid = str(oid) if oid else ""
        sample_tcs = doc.get("sampleTestCases") or []
        sample_in = doc.get("sampleInput") or (sample_tcs[0].get("input", "") if sample_tcs else "")
        sample_out = doc.get("sampleOutput") or (sample_tcs[0].get("output", "") if sample_tcs else "")

        # Always return sanitized dict
        return {
            "id": qid,
            "_id": qid,
            "title": doc.get("title", ""),
            "statement": doc.get("statement") or doc.get("problemStatement", ""),
            "problemStatement": doc.get("statement") or doc.get("problemStatement", ""),
            "inputFormat": doc.get("inputFormat", ""),
            "outputFormat": doc.get("outputFormat", ""),
            "constraints": doc.get("constraints", ""),
            "topic": doc.get("topic", "Algorithms"),
            "category": doc.get("category") or doc.get("topic", "Algorithms"),
            "difficulty": doc.get("difficulty", "Medium"),
            "tags": doc.get("tags", []),
            "languages": doc.get("languages", ["Python", "JavaScript", "Java", "C++"]),
            "programmingLanguage": (doc.get("languages") or ["Python"])[0],
            "domains": doc.get("domains", []),
            "checker": doc.get("checker", CHECKER_EXACT),
            "timeLimit": doc.get("timeLimit", 2.0),
            "memoryLimit": doc.get("memoryLimit", 256),
            "sampleInput": sample_in,
            "sampleOutput": sample_out,
            "sampleTestCases": sample_tcs,
            "testCases": sample_tcs,
            "marks": doc.get("marks", 10),
            "leetcodeStyle": True,
            "status": doc.get("status", STATUS_APPROVED),
            "version": doc.get("version", 1),
        }

    @staticmethod
    def admin_response(doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Formats problem document for administrative review.
        Includes verification reports, metadata, server-only code, and hidden tests.
        """
        if not doc:
            return None

        oid = doc.get("_id")
        created_at = doc.get("createdAt")
        updated_at = doc.get("updatedAt")

        return {
            "id": str(oid) if oid else "",
            "_id": str(oid) if oid else "",
            "title": doc.get("title", ""),
            "statement": doc.get("statement") or doc.get("problemStatement", ""),
            "problemStatement": doc.get("statement") or doc.get("problemStatement", ""),
            "inputFormat": doc.get("inputFormat", ""),
            "outputFormat": doc.get("outputFormat", ""),
            "constraints": doc.get("constraints", ""),
            "topic": doc.get("topic", "Algorithms"),
            "category": doc.get("category", "Algorithms"),
            "difficulty": doc.get("difficulty", "Medium"),
            "tags": doc.get("tags", []),
            "languages": doc.get("languages", []),
            "domains": doc.get("domains", []),
            "checker": doc.get("checker", CHECKER_EXACT),
            "timeLimit": doc.get("timeLimit", 2.0),
            "memoryLimit": doc.get("memoryLimit", 256),
            "sampleTestCases": doc.get("sampleTestCases", []),
            "hiddenTestCases": doc.get("hiddenTestCases", []),
            "status": doc.get("status", STATUS_DRAFT),
            "source": doc.get("source", "curated_seed"),
            "createdBy": doc.get("createdBy", "system"),
            "reviewedBy": doc.get("reviewedBy"),
            "version": doc.get("version", 1),
            "isActive": doc.get("isActive", True),
            "createdAt": created_at.isoformat() if isinstance(created_at, datetime) else str(created_at or ""),
            "updatedAt": updated_at.isoformat() if isinstance(updated_at, datetime) else str(updated_at or ""),
            "referenceSolution": doc.get("referenceSolution", ""),
            "bruteForceSolution": doc.get("bruteForceSolution", ""),
            "inputGenerator": doc.get("inputGenerator", ""),
            "mutations": doc.get("mutations", []),
            "edgeCases": doc.get("edgeCases", []),
            "verificationReport": doc.get("verificationReport"),
            "marks": doc.get("marks", 10),
        }
