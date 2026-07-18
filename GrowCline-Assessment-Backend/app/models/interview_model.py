"""
Interview Model
Defines the MongoDB document structure and all database operations
for the AI Interview module across three collections:
  - interviews
  - interview_questions
  - interview_answers
"""

from datetime import datetime, timezone
from bson import ObjectId

# ---------------------------------------------------------------------------
# Interview Status Constants
# ---------------------------------------------------------------------------

STATUS_CREATED     = "CREATED"
STATUS_IN_PROGRESS = "IN_PROGRESS"
STATUS_PAUSED      = "PAUSED"
STATUS_COMPLETED   = "COMPLETED"
STATUS_CANCELLED   = "CANCELLED"
STATUS_EXPIRED     = "EXPIRED"

VALID_STATUSES = {
    STATUS_CREATED,
    STATUS_IN_PROGRESS,
    STATUS_PAUSED,
    STATUS_COMPLETED,
    STATUS_CANCELLED,
    STATUS_EXPIRED,
}

# ---------------------------------------------------------------------------
# Interview Type Constants
# ---------------------------------------------------------------------------

TYPE_TECHNICAL  = "TECHNICAL"
TYPE_HR         = "HR"
TYPE_BEHAVIORAL = "BEHAVIORAL"
TYPE_RESUME     = "RESUME_BASED"

VALID_INTERVIEW_TYPES = {TYPE_TECHNICAL, TYPE_HR, TYPE_BEHAVIORAL, TYPE_RESUME}

# ---------------------------------------------------------------------------
# Difficulty Constants
# ---------------------------------------------------------------------------

DIFFICULTY_EASY   = "EASY"
DIFFICULTY_MEDIUM = "MEDIUM"
DIFFICULTY_HARD   = "HARD"

VALID_DIFFICULTIES = {DIFFICULTY_EASY, DIFFICULTY_MEDIUM, DIFFICULTY_HARD}

# ---------------------------------------------------------------------------
# Serialization Helpers
# ---------------------------------------------------------------------------

def _fmt(dt) -> str | None:
    """Return ISO-8601 string for a datetime, or None."""
    if isinstance(dt, datetime):
        return dt.isoformat()
    return dt


# ---------------------------------------------------------------------------
# Interview Document
# ---------------------------------------------------------------------------

class Interview:
    """
    Represents an 'interviews' MongoDB document.

    An interview session belongs to one user (candidate) and tracks the
    entire AI-driven question-answer lifecycle through to completion.
    """

    COLLECTION = "interviews"

    # ------------------------------------------------------------------
    # Document builder
    # ------------------------------------------------------------------

    @staticmethod
    def create_interview(
        user_id: str,
        job_role: str,
        interview_type: str,
        difficulty: str = DIFFICULTY_MEDIUM,
        total_questions: int = 10,
        duration_seconds: int = 1800,
        resume_id: str | None = None,
    ) -> dict:
        """
        Build a new 'interviews' document ready for MongoDB insertion.

        Args:
            user_id:          Authenticated candidate ObjectId string.
            job_role:         Target role (e.g. "Backend Developer").
            interview_type:   One of TECHNICAL | HR | BEHAVIORAL | RESUME_BASED.
            difficulty:       EASY | MEDIUM | HARD.
            total_questions:  Maximum number of questions for this session.
            duration_seconds: Allowed session duration in seconds.
            resume_id:        ObjectId string of a linked resume document, or None.

        Returns:
            dict ready to pass to collection.insert_one().
        """
        now = datetime.now(timezone.utc)
        return {
            "_id":             ObjectId(),
            "userId":          ObjectId(user_id),
            "jobRole":         job_role,
            "interviewType":   interview_type,
            "status":          STATUS_IN_PROGRESS,
            "difficulty":      difficulty,
            "currentQuestion": 0,
            "totalQuestions":  total_questions,
            "startedAt":       now,
            "endedAt":         None,
            "durationSeconds": duration_seconds,
            "resumeId":        ObjectId(resume_id) if resume_id else None,
            "createdAt":       now,
            "updatedAt":       now,
        }

    # ------------------------------------------------------------------
    # Serializer
    # ------------------------------------------------------------------

    @staticmethod
    def response(doc: dict) -> dict:
        """
        Serialize an 'interviews' MongoDB document for an API response.

        Converts ObjectId / datetime values to JSON-safe strings and
        exposes all fields needed by downstream modules.

        Args:
            doc: Raw MongoDB document from the interviews collection.

        Returns:
            dict safe for JSON serialisation.
        """
        elapsed = None
        remaining = None
        started = doc.get("startedAt")
        if isinstance(started, datetime):
            elapsed = int((datetime.now(timezone.utc) - started.replace(tzinfo=timezone.utc)
                           if started.tzinfo is None else
                           datetime.now(timezone.utc) - started).total_seconds())
            remaining = max(0, doc.get("durationSeconds", 1800) - elapsed)

        return {
            "id":              str(doc["_id"]),
            "userId":          str(doc["userId"]),
            "jobRole":         doc.get("jobRole", ""),
            "interviewType":   doc.get("interviewType", ""),
            "status":          doc.get("status", ""),
            "difficulty":      doc.get("difficulty", ""),
            "currentQuestion": doc.get("currentQuestion", 0),
            "totalQuestions":  doc.get("totalQuestions", 10),
            "startedAt":       _fmt(doc.get("startedAt")),
            "endedAt":         _fmt(doc.get("endedAt")),
            "durationSeconds": doc.get("durationSeconds", 1800),
            "elapsedSeconds":  elapsed,
            "remainingSeconds": remaining,
            "resumeId":        str(doc["resumeId"]) if doc.get("resumeId") else None,
            "createdAt":       _fmt(doc.get("createdAt")),
            "updatedAt":       _fmt(doc.get("updatedAt")),
        }


# ---------------------------------------------------------------------------
# Interview Question Document
# ---------------------------------------------------------------------------

class InterviewQuestion:
    """
    Represents an 'interview_questions' MongoDB document.

    Each question belongs to exactly one interview session and carries an
    ordinal questionNumber so that history can be reconstructed in order.
    """

    COLLECTION = "interview_questions"

    @staticmethod
    def create_question(
        interview_id: str,
        question_number: int,
        question_text: str,
        question_type: str,
        generated_by: str = "GROQ",
    ) -> dict:
        """
        Build a new 'interview_questions' document ready for MongoDB insertion.

        Args:
            interview_id:    Parent interview ObjectId string.
            question_number: 1-based sequential question index.
            question_text:   The AI-generated question text.
            question_type:   Mirrors the parent interview type.
            generated_by:    AI provider label (e.g. "GROQ", "GEMINI").

        Returns:
            dict ready to pass to collection.insert_one().
        """
        now = datetime.now(timezone.utc)
        return {
            "_id":            ObjectId(),
            "interviewId":    ObjectId(interview_id),
            "questionNumber": question_number,
            "questionType":   question_type,
            "questionText":   question_text,
            "generatedBy":    generated_by,
            "createdAt":      now,
        }

    @staticmethod
    def response(doc: dict) -> dict:
        """Serialize an interview_questions document for an API response."""
        return {
            "id":             str(doc["_id"]),
            "interviewId":    str(doc["interviewId"]),
            "questionNumber": doc.get("questionNumber"),
            "questionType":   doc.get("questionType", ""),
            "questionText":   doc.get("questionText", ""),
            "generatedBy":    doc.get("generatedBy", ""),
            "createdAt":      _fmt(doc.get("createdAt")),
        }


# ---------------------------------------------------------------------------
# Interview Answer Document
# ---------------------------------------------------------------------------

class InterviewAnswer:
    """
    Represents an 'interview_answers' MongoDB document.

    Each answer links a candidate's text response to a specific question and
    stores the AI evaluation results alongside it.
    """

    COLLECTION = "interview_answers"

    @staticmethod
    def create_answer(
        interview_id: str,
        question_id: str,
        candidate_answer: str,
        evaluation_score: int = 0,
        feedback: str = "",
        keywords_matched: list | None = None,
        strengths: list | None = None,
        weaknesses: list | None = None,
        suggestions: list | None = None,
    ) -> dict:
        """
        Build a new 'interview_answers' document ready for MongoDB insertion.

        Args:
            interview_id:      Parent interview ObjectId string.
            question_id:       Linked interview_questions ObjectId string.
            candidate_answer:  Raw text response submitted by the candidate.
            evaluation_score:  AI-assigned integer score 0–100.
            feedback:          Narrative feedback paragraph from AI.
            keywords_matched:  List of keywords found in the answer.
            strengths:         List of identified strength phrases.
            weaknesses:        List of identified weakness phrases.
            suggestions:       List of improvement suggestions from AI.

        Returns:
            dict ready to pass to collection.insert_one().
        """
        now = datetime.now(timezone.utc)
        return {
            "_id":             ObjectId(),
            "interviewId":     ObjectId(interview_id),
            "questionId":      ObjectId(question_id),
            "candidateAnswer": candidate_answer,
            "evaluationScore": evaluation_score,
            "feedback":        feedback,
            "keywordsMatched": keywords_matched or [],
            "strengths":       strengths or [],
            "weaknesses":      weaknesses or [],
            "suggestions":     suggestions or [],
            "answeredAt":      now,
        }

    @staticmethod
    def response(doc: dict) -> dict:
        """Serialize an interview_answers document for an API response."""
        return {
            "id":              str(doc["_id"]),
            "interviewId":     str(doc["interviewId"]),
            "questionId":      str(doc["questionId"]),
            "candidateAnswer": doc.get("candidateAnswer", ""),
            "evaluationScore": doc.get("evaluationScore", 0),
            "feedback":        doc.get("feedback", ""),
            "keywordsMatched": doc.get("keywordsMatched", []),
            "strengths":       doc.get("strengths", []),
            "weaknesses":      doc.get("weaknesses", []),
            "suggestions":     doc.get("suggestions", []),
            "answeredAt":      _fmt(doc.get("answeredAt")),
        }


# ---------------------------------------------------------------------------
# Model-layer CRUD helpers (pure MongoDB operations, no business logic)
# ---------------------------------------------------------------------------

class InterviewModel:
    """
    Thin MongoDB CRUD layer for all three interview collections.

    All methods receive a 'db' (Database.get_db()) reference so they
    remain stateless and testable without global state.
    """

    # ── interviews ──────────────────────────────────────────────────────

    @staticmethod
    def create(db, doc: dict) -> str:
        """Insert a new interview document; return its string _id."""
        result = db[Interview.COLLECTION].insert_one(doc)
        return str(result.inserted_id)

    @staticmethod
    def find_by_id(db, interview_id: str) -> dict | None:
        """Return an interview document by _id, or None."""
        try:
            return db[Interview.COLLECTION].find_one({"_id": ObjectId(interview_id)})
        except Exception:
            return None

    @staticmethod
    def find_by_user(db, user_id: str) -> list[dict]:
        """Return all interview documents for a user, newest first."""
        try:
            cursor = db[Interview.COLLECTION].find(
                {"userId": ObjectId(user_id)}
            ).sort("createdAt", -1)
            return list(cursor)
        except Exception:
            return []

    @staticmethod
    def update(db, interview_id: str, fields: dict) -> bool:
        """
        Partially update an interview document.

        Args:
            interview_id: Target document _id string.
            fields:        Dict of fields to $set.

        Returns:
            True if a document was modified, False otherwise.
        """
        fields["updatedAt"] = datetime.now(timezone.utc)
        result = db[Interview.COLLECTION].update_one(
            {"_id": ObjectId(interview_id)},
            {"$set": fields},
        )
        return result.modified_count > 0

    @staticmethod
    def complete_interview(db, interview_id: str, ended_at: datetime) -> bool:
        """Mark an interview as COMPLETED and record its end time."""
        now = datetime.now(timezone.utc)
        result = db[Interview.COLLECTION].update_one(
            {"_id": ObjectId(interview_id)},
            {
                "$set": {
                    "status":    STATUS_COMPLETED,
                    "endedAt":   ended_at,
                    "updatedAt": now,
                }
            },
        )
        return result.modified_count > 0

    @staticmethod
    def increment_question(db, interview_id: str) -> bool:
        """Atomically increment currentQuestion by 1."""
        now = datetime.now(timezone.utc)
        result = db[Interview.COLLECTION].update_one(
            {"_id": ObjectId(interview_id)},
            {
                "$inc": {"currentQuestion": 1},
                "$set": {"updatedAt": now},
            },
        )
        return result.modified_count > 0

    # ── interview_questions ──────────────────────────────────────────────

    @staticmethod
    def create_question(db, doc: dict) -> str:
        """Insert a new question document; return its string _id."""
        result = db[InterviewQuestion.COLLECTION].insert_one(doc)
        return str(result.inserted_id)

    @staticmethod
    def find_question_by_id(db, question_id: str) -> dict | None:
        """Return a question document by _id, or None."""
        try:
            return db[InterviewQuestion.COLLECTION].find_one(
                {"_id": ObjectId(question_id)}
            )
        except Exception:
            return None

    @staticmethod
    def find_questions_by_interview(db, interview_id: str) -> list[dict]:
        """Return all questions for an interview, ordered by questionNumber."""
        try:
            cursor = db[InterviewQuestion.COLLECTION].find(
                {"interviewId": ObjectId(interview_id)}
            ).sort("questionNumber", 1)
            return list(cursor)
        except Exception:
            return []

    # ── interview_answers ────────────────────────────────────────────────

    @staticmethod
    def create_answer(db, doc: dict) -> str:
        """Insert a new answer document; return its string _id."""
        result = db[InterviewAnswer.COLLECTION].insert_one(doc)
        return str(result.inserted_id)

    @staticmethod
    def find_answers_by_interview(db, interview_id: str) -> list[dict]:
        """Return all answers for an interview, ordered by answeredAt."""
        try:
            cursor = db[InterviewAnswer.COLLECTION].find(
                {"interviewId": ObjectId(interview_id)}
            ).sort("answeredAt", 1)
            return list(cursor)
        except Exception:
            return []

    @staticmethod
    def find_answer_by_question(db, question_id: str) -> dict | None:
        """Return the answer document linked to a specific question, or None."""
        try:
            return db[InterviewAnswer.COLLECTION].find_one(
                {"questionId": ObjectId(question_id)}
            )
        except Exception:
            return None
