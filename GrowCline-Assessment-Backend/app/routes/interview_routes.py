"""
Interview Routes
FastAPI APIRouter for the AI Interview module.

Registers all seven interview endpoints under the /api/interviews prefix.

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
from typing import Optional
from datetime import datetime
from bson import ObjectId

from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import JSONResponse

from app.controllers.interview_controller import InterviewController
from app.utils.jwt_utils import decode_token
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


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/user/{user_id}", summary="List all interviews for a user")
async def get_user_interviews(
    user_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    GET /api/interviews/user/{user_id}

    Returns all interview sessions belonging to the specified user,
    ordered from newest to oldest. A candidate may only retrieve their
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
    """
    return await InterviewController.end_interview(
        interview_id=interview_id,
        current_user=current_user,
    )
