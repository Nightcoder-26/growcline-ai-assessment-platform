"""
Interview Service
Business logic for the AI Interview module.

Responsibilities
----------------
- Create and manage interview sessions
- Generate AI questions via Groq LLM (llama3-70b-8192)
- Evaluate candidate answers via Groq LLM
- Validate interview state (ownership, status, timer)
- Track question progression
- Calculate interview duration and produce a completion summary
- Store interview history (questions + answers + evaluations)

Architecture:  Route → Controller → Service → Model → MongoDB
"""

import json
import logging
import re
from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId

try:
    from config.database import Database
    from config.settings import Config
except ImportError:
    from app.config.database import Database
    from app.config.settings import Config

try:
    from models.interview_model import (
        Interview,
        InterviewAnswer,
        InterviewModel,
        InterviewQuestion,
        STATUS_COMPLETED,
        STATUS_CANCELLED,
        STATUS_EXPIRED,
        STATUS_IN_PROGRESS,
        VALID_INTERVIEW_TYPES,
        VALID_DIFFICULTIES,
        TYPE_RESUME,
    )
except ImportError:
    from app.models.interview_model import (
        Interview,
        InterviewAnswer,
        InterviewModel,
        InterviewQuestion,
        STATUS_COMPLETED,
        STATUS_CANCELLED,
        STATUS_EXPIRED,
        STATUS_IN_PROGRESS,
        VALID_INTERVIEW_TYPES,
        VALID_DIFFICULTIES,
        TYPE_RESUME,
    )

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Groq AI Client — lazy initialisation
# ---------------------------------------------------------------------------

_groq_client = None


def _get_groq_client():
    """
    Return a cached Groq client.  Raises RuntimeError if the package or
    API key is unavailable so callers can surface a clean 500 error.
    """
    global _groq_client
    if _groq_client is not None:
        return _groq_client

    try:
        from groq import Groq  # type: ignore
    except ImportError:
        raise RuntimeError(
            "groq package is not installed. Run: pip install groq"
        )

    api_key = Config.GROQ_API_KEY
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured in .env.")

    _groq_client = Groq(api_key=api_key)
    return _groq_client


# ---------------------------------------------------------------------------
# AI Prompt Templates
# ---------------------------------------------------------------------------

QUESTION_SYSTEM_PROMPT = (
    "You are an expert technical interviewer. "
    "Generate exactly ONE interview question based on the given parameters. "
    "Return ONLY a raw JSON object with a single key 'question' containing the question text. "
    "No markdown, no code fences, no extra commentary."
)

QUESTION_USER_TEMPLATE = """
Generate one interview question with these parameters:
- Job Role: {job_role}
- Interview Type: {interview_type}
- Difficulty Level: {difficulty}
- Question Number: {question_number} of {total_questions}

Previously asked questions (do NOT repeat these):
{previous_questions}

Resume skills (use when relevant for RESUME_BASED type):
{resume_skills}

Return ONLY this JSON:
{{"question": "<your question here>"}}
""".strip()

EVALUATION_SYSTEM_PROMPT = (
    "You are an expert interview evaluator. "
    "Evaluate the candidate answer and return ONLY a raw JSON object. "
    "No markdown, no code fences, no extra commentary."
)

EVALUATION_USER_TEMPLATE = """
Evaluate this interview answer:

Job Role: {job_role}
Interview Type: {interview_type}
Question: {question_text}
Candidate Answer: {candidate_answer}

Return ONLY this JSON:
{{
  "score": <integer 0-100>,
  "feedback": "<one paragraph narrative feedback>",
  "strengths": ["<strength 1>", "<strength 2>"],
  "weaknesses": ["<weakness 1>"],
  "suggestions": ["<improvement 1>"],
  "keywords_matched": ["<keyword 1>", "<keyword 2>"]
}}
""".strip()

# Default model and token limits
_GROQ_MODEL       = "llama3-70b-8192"
_QUESTION_TOKENS  = 400
_EVALUATION_TOKENS = 600


# ---------------------------------------------------------------------------
# Internal AI helpers
# ---------------------------------------------------------------------------

def _call_groq(system_prompt: str, user_prompt: str, max_tokens: int) -> str:
    """
    Send a chat completion request to Groq and return the raw content string.

    Raises:
        RuntimeError: on Groq API failure or unexpected response.
    """
    client = _get_groq_client()
    try:
        response = client.chat.completions.create(
            model=_GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            max_tokens=max_tokens,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:
        logger.error("Groq API call failed: %s", exc)
        raise RuntimeError(f"AI service error: {exc}") from exc


def _extract_json(text: str) -> dict:
    """
    Robustly extract a JSON object from an AI response string.

    Strips markdown code fences if present, then parses.

    Raises:
        ValueError: if no valid JSON object is found.
    """
    # Remove markdown code fences
    text = re.sub(r"```(?:json)?", "", text).strip()

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Fallback: find first {...} block
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Could not extract JSON from AI response: {text[:200]}")


# ---------------------------------------------------------------------------
# AI Question Generation
# ---------------------------------------------------------------------------

def generate_ai_question(
    job_role: str,
    interview_type: str,
    difficulty: str,
    question_number: int,
    total_questions: int,
    previous_questions: list[str] | None = None,
    resume_skills: list[str] | None = None,
) -> str:
    """
    Generate a single interview question using the Groq LLM.

    Args:
        job_role:           Target job role.
        interview_type:     TECHNICAL | HR | BEHAVIORAL | RESUME_BASED.
        difficulty:         EASY | MEDIUM | HARD.
        question_number:    Current question index (1-based).
        total_questions:    Total questions in the session.
        previous_questions: List of already-asked question texts to avoid repetition.
        resume_skills:      Skills extracted from the candidate's resume.

    Returns:
        Question text string.

    Raises:
        RuntimeError: if the AI service fails.
    """
    prev_list = "\n".join(
        f"- {q}" for q in (previous_questions or [])
    ) or "None"

    skills_text = ", ".join(resume_skills or []) or "Not provided"

    user_prompt = QUESTION_USER_TEMPLATE.format(
        job_role=job_role,
        interview_type=interview_type,
        difficulty=difficulty,
        question_number=question_number,
        total_questions=total_questions,
        previous_questions=prev_list,
        resume_skills=skills_text,
    )

    raw = _call_groq(QUESTION_SYSTEM_PROMPT, user_prompt, _QUESTION_TOKENS)

    try:
        data = _extract_json(raw)
        question_text = data.get("question", "").strip()
        if not question_text:
            raise ValueError("Empty question returned by AI.")
        return question_text
    except (ValueError, KeyError) as exc:
        logger.warning("Could not parse AI question JSON (%s), using raw: %s", exc, raw[:100])
        # Use the raw text as a fallback question
        cleaned = raw.replace("{", "").replace("}", "").replace('"question":', "").strip().strip('"')
        return cleaned or f"Describe your experience with {job_role} responsibilities."


# ---------------------------------------------------------------------------
# AI Answer Evaluation
# ---------------------------------------------------------------------------

def evaluate_ai_answer(
    job_role: str,
    interview_type: str,
    question_text: str,
    candidate_answer: str,
) -> dict:
    """
    Evaluate a candidate's answer using the Groq LLM.

    Returns a dict with keys: score, feedback, strengths, weaknesses,
    suggestions, keywords_matched.

    Raises:
        RuntimeError: if the AI service fails.
    """
    user_prompt = EVALUATION_USER_TEMPLATE.format(
        job_role=job_role,
        interview_type=interview_type,
        question_text=question_text,
        candidate_answer=candidate_answer,
    )

    raw = _call_groq(EVALUATION_SYSTEM_PROMPT, user_prompt, _EVALUATION_TOKENS)

    try:
        data = _extract_json(raw)
    except ValueError:
        logger.warning("AI evaluation JSON parse failed, using defaults.")
        data = {}

    # Clamp score to 0-100
    score = data.get("score", 50)
    try:
        score = max(0, min(100, int(score)))
    except (TypeError, ValueError):
        score = 50

    return {
        "score":            score,
        "feedback":         str(data.get("feedback", "No feedback available.")),
        "strengths":        list(data.get("strengths", [])),
        "weaknesses":       list(data.get("weaknesses", [])),
        "suggestions":      list(data.get("suggestions", [])),
        "keywords_matched": list(data.get("keywords_matched", [])),
    }


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def _validate_object_id(oid: str, label: str = "id") -> ObjectId:
    """Convert string to ObjectId; raise ValueError with a clear message on failure."""
    try:
        return ObjectId(oid)
    except (InvalidId, TypeError):
        raise ValueError(f"Invalid {label}: '{oid}' is not a valid ObjectId.")


def _assert_owner(interview: dict, user_id: str) -> None:
    """Raise PermissionError if the interview does not belong to user_id."""
    if str(interview["userId"]) != user_id:
        raise PermissionError("You do not have access to this interview.")


def _assert_active(interview: dict) -> None:
    """Raise ValueError if the interview is not in an active (IN_PROGRESS) state."""
    status = interview.get("status", "")
    if status == STATUS_COMPLETED:
        raise ValueError("This interview has already been completed.")
    if status == STATUS_CANCELLED:
        raise ValueError("This interview has been cancelled.")
    if status == STATUS_EXPIRED:
        raise ValueError("This interview session has expired.")
    if status != STATUS_IN_PROGRESS:
        raise ValueError(f"Interview is not active (current status: {status}).")


def _check_timer(interview: dict) -> None:
    """
    Auto-expire the interview if the allowed duration has elapsed.

    Raises:
        ValueError: if the interview timer has expired.
    """
    started = interview.get("startedAt")
    duration = interview.get("durationSeconds", 1800)
    if not isinstance(started, datetime):
        return

    now = datetime.now(timezone.utc)
    started_utc = started.replace(tzinfo=timezone.utc) if started.tzinfo is None else started
    elapsed = (now - started_utc).total_seconds()

    if elapsed > duration:
        # Auto-expire in DB
        db = Database.get_db()
        InterviewModel.update(
            db,
            str(interview["_id"]),
            {"status": STATUS_EXPIRED},
        )
        raise ValueError(
            f"Interview session has expired. Allowed duration: {duration}s, elapsed: {int(elapsed)}s."
        )


# ---------------------------------------------------------------------------
# Public Service Functions
# ---------------------------------------------------------------------------

def create_interview(
    user_id: str,
    job_role: str,
    interview_type: str,
    difficulty: str = "MEDIUM",
    total_questions: int = 10,
    duration_seconds: int = 1800,
    resume_id: str | None = None,
) -> dict:
    """
    Create a new interview session and generate the first AI question.

    Validates:
    - User exists in the database
    - interview_type is supported
    - difficulty is supported
    - For RESUME_BASED interviews, resume_id is provided

    Returns a dict with keys: interview, question.

    Raises:
        ValueError: on validation failure.
        RuntimeError: on AI or database failure.
    """
    db = Database.get_db()

    # Validate user
    _validate_object_id(user_id, "user_id")
    user = db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise ValueError("Authenticated user not found.")

    # Validate enums
    if interview_type not in VALID_INTERVIEW_TYPES:
        raise ValueError(
            f"Unsupported interview type '{interview_type}'. "
            f"Valid types: {sorted(VALID_INTERVIEW_TYPES)}."
        )
    if difficulty not in VALID_DIFFICULTIES:
        raise ValueError(
            f"Unsupported difficulty '{difficulty}'. "
            f"Valid options: {sorted(VALID_DIFFICULTIES)}."
        )

    # Resume-based validation
    resume_skills: list[str] = []
    if interview_type == TYPE_RESUME:
        if not resume_id:
            raise ValueError("resume_id is required for RESUME_BASED interview type.")
        # Try to fetch skills from resume if a resumes collection exists
        try:
            resume_doc = db.resumes.find_one({"_id": ObjectId(resume_id)})
            if resume_doc:
                resume_skills = resume_doc.get("skills", [])
        except Exception:
            pass  # Resume collection may not exist yet; continue gracefully

    # Build and persist the interview document
    interview_doc = Interview.create_interview(
        user_id=user_id,
        job_role=job_role,
        interview_type=interview_type,
        difficulty=difficulty,
        total_questions=total_questions,
        duration_seconds=duration_seconds,
        resume_id=resume_id,
    )
    interview_id = InterviewModel.create(db, interview_doc)

    # Generate the first question
    question_number = 1
    question_text = generate_ai_question(
        job_role=job_role,
        interview_type=interview_type,
        difficulty=difficulty,
        question_number=question_number,
        total_questions=total_questions,
        previous_questions=[],
        resume_skills=resume_skills,
    )

    # Persist the question
    question_doc = InterviewQuestion.create_question(
        interview_id=interview_id,
        question_number=question_number,
        question_text=question_text,
        question_type=interview_type,
    )
    question_id = InterviewModel.create_question(db, question_doc)

    # Increment currentQuestion counter
    InterviewModel.update(db, interview_id, {"currentQuestion": 1})

    # Re-fetch the persisted documents for consistent serialisation
    interview = InterviewModel.find_by_id(db, interview_id)
    question  = InterviewModel.find_question_by_id(db, question_id)

    return {
        "interview": Interview.response(interview),
        "question":  _enrich_question(question, interview),
    }


def get_next_question(interview_id: str, user_id: str, topic_hint: str | None = None) -> dict:
    """
    Generate and persist the next AI question for an active interview.

    Validates:
    - Interview exists and belongs to the requesting user
    - Interview is IN_PROGRESS
    - Timer has not expired
    - Maximum question count not yet reached

    Returns a serialised QuestionResponse dict.

    Raises:
        ValueError: on any validation failure.
        RuntimeError: on AI failure.
    """
    db = Database.get_db()

    interview = _fetch_and_validate(db, interview_id, user_id)

    current   = interview.get("currentQuestion", 0)
    total     = interview.get("totalQuestions", 10)

    if current >= total:
        raise ValueError(
            f"All {total} questions have been asked. End the interview to see your results."
        )

    # Collect previous question texts to avoid repetition
    prev_docs     = InterviewModel.find_questions_by_interview(db, interview_id)
    previous_texts = [q.get("questionText", "") for q in prev_docs]

    # Fetch resume skills if available
    resume_skills: list[str] = []
    if interview.get("resumeId"):
        try:
            resume_doc = db.resumes.find_one({"_id": interview["resumeId"]})
            if resume_doc:
                resume_skills = resume_doc.get("skills", [])
        except Exception:
            pass

    question_number = current + 1
    question_text = generate_ai_question(
        job_role=interview["jobRole"],
        interview_type=interview["interviewType"],
        difficulty=interview["difficulty"],
        question_number=question_number,
        total_questions=total,
        previous_questions=previous_texts,
        resume_skills=resume_skills,
    )

    if topic_hint:
        question_text = f"[Topic: {topic_hint}] {question_text}"

    question_doc = InterviewQuestion.create_question(
        interview_id=interview_id,
        question_number=question_number,
        question_text=question_text,
        question_type=interview["interviewType"],
    )
    question_id = InterviewModel.create_question(db, question_doc)
    InterviewModel.increment_question(db, interview_id)

    # Re-fetch for accurate timestamps
    question  = InterviewModel.find_question_by_id(db, question_id)
    interview = InterviewModel.find_by_id(db, interview_id)

    return _enrich_question(question, interview)


def submit_answer(
    interview_id: str,
    user_id: str,
    question_id: str,
    candidate_answer: str,
) -> dict:
    """
    Save a candidate's answer and evaluate it with AI.

    Validates:
    - Interview exists, belongs to user, and is active
    - Timer has not expired
    - The referenced question belongs to this interview
    - The question has not already been answered

    Returns an EvaluationResponse-shaped dict.

    Raises:
        ValueError: on validation failure.
        RuntimeError: on AI or database failure.
    """
    db = Database.get_db()

    interview = _fetch_and_validate(db, interview_id, user_id)

    # Validate question
    _validate_object_id(question_id, "question_id")
    question = InterviewModel.find_question_by_id(db, question_id)
    if not question:
        raise ValueError(f"Question '{question_id}' not found.")
    if str(question["interviewId"]) != interview_id:
        raise ValueError("Question does not belong to this interview.")

    # Prevent duplicate answers
    existing = InterviewModel.find_answer_by_question(db, question_id)
    if existing:
        raise ValueError("This question has already been answered.")

    # AI evaluation
    evaluation = evaluate_ai_answer(
        job_role=interview["jobRole"],
        interview_type=interview["interviewType"],
        question_text=question["questionText"],
        candidate_answer=candidate_answer,
    )

    # Persist answer + evaluation
    answer_doc = InterviewAnswer.create_answer(
        interview_id=interview_id,
        question_id=question_id,
        candidate_answer=candidate_answer,
        evaluation_score=evaluation["score"],
        feedback=evaluation["feedback"],
        keywords_matched=evaluation["keywords_matched"],
        strengths=evaluation["strengths"],
        weaknesses=evaluation["weaknesses"],
        suggestions=evaluation["suggestions"],
    )
    answer_id = InterviewModel.create_answer(db, answer_doc)

    # Re-fetch final answer doc
    saved_answer = db[InterviewAnswer.COLLECTION].find_one({"_id": ObjectId(answer_id)})
    interview    = InterviewModel.find_by_id(db, interview_id)

    current  = interview.get("currentQuestion", 0)
    total    = interview.get("totalQuestions", 10)

    result = InterviewAnswer.response(saved_answer)
    result["currentQuestion"]  = current
    result["totalQuestions"]   = total
    result["interviewComplete"] = current >= total

    return result


def end_interview(interview_id: str, user_id: str) -> dict:
    """
    Mark an interview as COMPLETED and return a summary.

    Validates:
    - Interview exists and belongs to the requesting user
    - Interview is IN_PROGRESS (not already completed/cancelled)

    Returns an InterviewSummaryResponse-shaped dict.

    Raises:
        ValueError: on validation failure.
    """
    db = Database.get_db()

    interview = _fetch_and_validate(db, interview_id, user_id)

    ended_at = datetime.now(timezone.utc)
    InterviewModel.complete_interview(db, interview_id, ended_at)

    # Compute summary statistics
    answers = InterviewModel.find_answers_by_interview(db, interview_id)
    scores  = [a.get("evaluationScore", 0) for a in answers if a.get("evaluationScore") is not None]
    avg_score = round(sum(scores) / len(scores), 2) if scores else None

    started_at = interview.get("startedAt")
    actual_duration = None
    if isinstance(started_at, datetime):
        started_utc = started_at.replace(tzinfo=timezone.utc) if started_at.tzinfo is None else started_at
        actual_duration = int((ended_at - started_utc).total_seconds())

    def _fmt(dt):
        return dt.isoformat() if isinstance(dt, datetime) else dt

    return {
        "interviewId":          interview_id,
        "status":               STATUS_COMPLETED,
        "jobRole":              interview.get("jobRole", ""),
        "interviewType":        interview.get("interviewType", ""),
        "difficulty":           interview.get("difficulty", ""),
        "totalQuestions":       interview.get("totalQuestions", 10),
        "questionsAnswered":    len(answers),
        "averageScore":         avg_score,
        "startedAt":            _fmt(interview.get("startedAt")),
        "endedAt":              _fmt(ended_at),
        "durationSeconds":      interview.get("durationSeconds", 1800),
        "actualDurationSeconds": actual_duration,
    }


def get_interview(interview_id: str, user_id: str) -> dict:
    """
    Fetch a single interview session (metadata only, no questions/answers).

    Raises:
        ValueError: if not found or not owned by user_id.
    """
    db = Database.get_db()
    _validate_object_id(interview_id, "interview_id")

    interview = InterviewModel.find_by_id(db, interview_id)
    if not interview:
        raise ValueError(f"Interview '{interview_id}' not found.")

    _assert_owner(interview, user_id)
    return Interview.response(interview)


def get_interview_history(interview_id: str, user_id: str) -> dict:
    """
    Return the complete question-answer-evaluation history for an interview.

    Raises:
        ValueError: if not found or not owned by user_id.
    """
    db = Database.get_db()
    _validate_object_id(interview_id, "interview_id")

    interview = InterviewModel.find_by_id(db, interview_id)
    if not interview:
        raise ValueError(f"Interview '{interview_id}' not found.")

    _assert_owner(interview, user_id)

    questions = InterviewModel.find_questions_by_interview(db, interview_id)
    answers   = InterviewModel.find_answers_by_interview(db, interview_id)

    # Build a lookup map from question ObjectId → answer doc
    answer_map: dict[str, dict] = {
        str(a["questionId"]): a for a in answers
    }

    history = []
    for q in questions:
        qid = str(q["_id"])
        ans = answer_map.get(qid)
        history.append({
            "questionNumber": q.get("questionNumber"),
            "question":       q.get("questionText", ""),
            "answer":         ans["candidateAnswer"] if ans else None,
            "evaluationScore": ans["evaluationScore"] if ans else None,
            "feedback":       ans["feedback"] if ans else None,
            "strengths":      ans.get("strengths", []) if ans else [],
            "weaknesses":     ans.get("weaknesses", []) if ans else [],
            "suggestions":    ans.get("suggestions", []) if ans else [],
            "answeredAt":     ans["answeredAt"].isoformat() if ans and isinstance(ans.get("answeredAt"), datetime) else None,
        })

    scores    = [h["evaluationScore"] for h in history if h["evaluationScore"] is not None]
    avg_score = round(sum(scores) / len(scores), 2) if scores else None

    def _fmt(dt):
        return dt.isoformat() if isinstance(dt, datetime) else dt

    return {
        "interviewId":      interview_id,
        "userId":           str(interview["userId"]),
        "jobRole":          interview.get("jobRole", ""),
        "interviewType":    interview.get("interviewType", ""),
        "difficulty":       interview.get("difficulty", ""),
        "status":           interview.get("status", ""),
        "totalQuestions":   interview.get("totalQuestions", 10),
        "questionsAnswered": len(answers),
        "averageScore":     avg_score,
        "startedAt":        _fmt(interview.get("startedAt")),
        "endedAt":          _fmt(interview.get("endedAt")),
        "durationSeconds":  interview.get("durationSeconds", 1800),
        "history":          history,
    }


def get_user_interviews(user_id: str) -> list[dict]:
    """
    Return all interview sessions for a user, newest first.

    Raises:
        ValueError: if user_id is not a valid ObjectId.
    """
    _validate_object_id(user_id, "user_id")
    db = Database.get_db()
    docs = InterviewModel.find_by_user(db, user_id)
    return [Interview.response(d) for d in docs]


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _fetch_and_validate(db, interview_id: str, user_id: str) -> dict:
    """
    Fetch an interview document and apply ownership, status, and timer checks.

    Used by every mutating endpoint to keep guard logic centralised.
    """
    _validate_object_id(interview_id, "interview_id")
    interview = InterviewModel.find_by_id(db, interview_id)
    if not interview:
        raise ValueError(f"Interview '{interview_id}' not found.")

    _assert_owner(interview, user_id)
    _assert_active(interview)
    _check_timer(interview)

    return interview


def _enrich_question(question: dict, interview: dict) -> dict:
    """
    Add session-level progress fields to a serialised question response.
    """
    result = InterviewQuestion.response(question)
    current = interview.get("currentQuestion", 0)
    total   = interview.get("totalQuestions", 10)

    result["remainingQuestions"] = max(0, total - current)
    result["totalQuestions"]     = total

    # Compute remaining seconds
    started = interview.get("startedAt")
    if isinstance(started, datetime):
        now        = datetime.now(timezone.utc)
        started_utc = started.replace(tzinfo=timezone.utc) if started.tzinfo is None else started
        elapsed    = int((now - started_utc).total_seconds())
        result["remainingSeconds"] = max(0, interview.get("durationSeconds", 1800) - elapsed)
    else:
        result["remainingSeconds"] = interview.get("durationSeconds", 1800)

    return result
