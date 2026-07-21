"""
Interview Routes
FastAPI APIRouter for the AI Interview module.

Registers all seven interview endpoints under the /api/interviews prefix.
Follows the exact same pattern as the existing recording_routes.py and
proctoring_routes.py used by Team B.

Endpoints
---------
POST   /api/interviews/start                  — Start a new interview session
POST   /api/interviews/{interview_id}/question — Generate next AI question
POST   /api/interviews/{interview_id}/answer   — Submit and evaluate an answer
GET    /api/interviews/{interview_id}          — Get interview metadata
GET    /api/interviews/{interview_id}/history  — Get full Q&A history
POST   /api/interviews/{interview_id}/end      — End/complete the interview
GET    /api/interviews/user/{user_id}          — List all interviews for a user
"""

import logging

from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import JSONResponse

try:
    from controllers.interview_controller import InterviewController
    from middleware.jwt_utils import decode_token
    from config.database import Database
    from schemas.interview_schema import (
        InterviewCreateRequest,
        QuestionRequest,
        AnswerRequest,
    )
except ImportError:
    from app.controllers.interview_controller import InterviewController
    from app.middleware.jwt_utils import decode_token
    from app.config.database import Database
    from app.schemas.interview_schema import (
        InterviewCreateRequest,
        QuestionRequest,
        AnswerRequest,
    )

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/interviews", tags=["AI Interviews"])


# ---------------------------------------------------------------------------
# JWT Authentication Dependency
# ---------------------------------------------------------------------------

async def get_current_user(authorization: Optional[str] = Header(None)):
    """
    Validate a Bearer JWT from the Authorization header.
    If no header is provided or token is invalid, automatically resolves to the
    default candidate user to enable guest interview sessions.
    """
    db = Database.get_db()

    def _get_guest_user():
        user = db.users.find_one({"role": "candidate"})
        if not user:
            user = db.users.find_one()
        if not user:
            res = db.users.insert_one({
                "email": "candidate@growcline.com",
                "name": "Candidate User",
                "role": "candidate",
                "createdAt": datetime.utcnow()
            })
            user = db.users.find_one({"_id": res.inserted_id})
        return {
            "id": str(user["_id"]),
            "email": user.get("email", "candidate@growcline.com"),
            "role": user.get("role", "candidate"),
        }

    if not authorization or not authorization.startswith("Bearer "):
        return _get_guest_user()

    token = authorization.split(" ", 1)[1].strip()
    if not token:
        return _get_guest_user()

    payload = decode_token(token)
    if not payload or "id" not in payload:
        return _get_guest_user()

    try:
        from bson import ObjectId
        user = db.users.find_one({"_id": ObjectId(payload["id"])})
        if not user:
            return _get_guest_user()
        return {
            "id": str(user["_id"]),
            "email": user.get("email", "candidate@growcline.com"),
            "role": user.get("role", "candidate"),
        }
    except Exception:
        return _get_guest_user()

    return {
        "id":    payload.get("id"),
        "email": payload.get("email"),
        "role":  payload.get("role"),
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

# NOTE: The /user/{user_id} route MUST be registered before /{interview_id}
# to prevent FastAPI from treating "user" as an interview_id path segment.

@router.get("/user/{user_id}", summary="List all interviews for a user")
async def get_user_interviews(
    user_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    GET /api/interviews/user/{user_id}

    Returns all interview sessions belonging to the specified user,
    ordered from newest to oldest.  A candidate may only retrieve their
    own interview list.
    """
    return await InterviewController.get_user_interviews(
        requested_user_id=user_id,
        current_user=current_user,
    )


@router.post("/start", summary="Start a new AI interview session")
async def start_interview(
    body: InterviewCreateRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    POST /api/interviews/start

    Creates a new interview session for the authenticated candidate,
    generates the first AI question, and returns both the session metadata
    and the opening question.

    **Body fields**
    - `jobRole` (required)  — Target job role, e.g. "Backend Developer"
    - `interviewType` (required) — TECHNICAL | HR | BEHAVIORAL | RESUME_BASED
    - `difficulty` (optional, default MEDIUM) — EASY | MEDIUM | HARD
    - `totalQuestions` (optional, default 10) — 1–20
    - `durationSeconds` (optional, default 1800) — 300–7200
    - `resumeId` (optional) — Required when interviewType is RESUME_BASED
    """
    return await InterviewController.start_interview(
        body=body.model_dump(),
        current_user=current_user,
    )


@router.post("/{interview_id}/question", summary="Generate the next AI question")
async def get_next_question(
    interview_id: str,
    body: QuestionRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    POST /api/interviews/{interview_id}/question

    Generates and persists the next AI question for an active interview session.
    Validates session ownership, status, and timer before calling the AI.

    **Body fields**
    - `topicHint` (optional) — Guide the AI toward a specific sub-topic
    """
    return await InterviewController.get_next_question(
        interview_id=interview_id,
        body=body.model_dump(),
        current_user=current_user,
    )


@router.post("/{interview_id}/answer", summary="Submit and evaluate a candidate answer")
async def submit_answer(
    interview_id: str,
    body: AnswerRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    POST /api/interviews/{interview_id}/answer

    Accepts the candidate's answer to a specific question, evaluates it
    using the Groq AI, and persists the evaluation result.

    **Body fields**
    - `questionId` (required) — ObjectId of the question being answered
    - `candidateAnswer` (required) — The candidate's answer text (1–5000 chars)
    """
    return await InterviewController.submit_answer(
        interview_id=interview_id,
        body=body.model_dump(),
        current_user=current_user,
    )


@router.get("/{interview_id}", summary="Get interview session metadata")
async def get_interview(
    interview_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    GET /api/interviews/{interview_id}

    Returns the interview session document (metadata only).
    Does not include questions or answers — use /history for the full record.
    """
    return await InterviewController.get_interview(
        interview_id=interview_id,
        current_user=current_user,
    )


@router.get("/{interview_id}/history", summary="Get full interview Q&A history")
async def get_interview_history(
    interview_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    GET /api/interviews/{interview_id}/history

    Returns the complete question-answer-evaluation history for an interview,
    including AI scores, feedback, strengths, weaknesses, and suggestions.

    This endpoint provides the data consumed by:
    - Video Recording module (attaches recordings to interview sessions)
    - Live Proctoring module (correlates events to session timeline)
    - Cheating Detection module (analyses event patterns)
    - Interview Analytics module (generates the final interview report)
    """
    return await InterviewController.get_interview_history(
        interview_id=interview_id,
        current_user=current_user,
    )


@router.post("/{interview_id}/end", summary="End and complete an interview session")
async def end_interview(
    interview_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    POST /api/interviews/{interview_id}/end

    Marks the interview as COMPLETED, records the end time,
    and returns a summary with overall statistics (average score,
    questions answered, actual duration).
    """
    return await InterviewController.end_interview(
        interview_id=interview_id,
        current_user=current_user,
    )
