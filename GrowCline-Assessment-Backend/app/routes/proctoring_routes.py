"""
Proctoring Routes
FastAPI APIRouter for the Live Proctoring module.
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, Header, HTTPException, Query

from datetime import datetime

try:
    from config.database import Database
    from app.controllers.proctoring_controller import ProctoringController
    from middleware.jwt_utils import decode_token
    from schemas.proctoring_schema import (
        ProctoringEventCreate,
        ProctoringEventBatchCreate,
    )
except ImportError:
    from app.config.database import Database
    from app.controllers.proctoring_controller import ProctoringController
    from app.middleware.jwt_utils import decode_token
    from app.schemas.proctoring_schema import (
        ProctoringEventCreate,
        ProctoringEventBatchCreate,
    )

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/proctoring", tags=["Proctoring"])


# ---------------------------------------------------------------------------
# JWT authentication dependency (consistent with Team B's auth architecture)
# ---------------------------------------------------------------------------

async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """
    Validate a Bearer JWT from the Authorization header.
    If no header is provided or token is invalid, automatically resolves to the
    default candidate user to enable guest proctoring event logging.
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


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post("/events")
async def create_event(
    event_data: ProctoringEventCreate,
    current_user: dict = Depends(get_current_user),
):
    """
    POST /api/proctoring/events

    Log a single live proctoring event.
    """
    return await ProctoringController.create_event(event_data, current_user)


@router.post("/events/batch")
async def create_event_batch(
    batch_data: ProctoringEventBatchCreate,
    current_user: dict = Depends(get_current_user),
):
    """
    POST /api/proctoring/events/batch

    Log a batch of live proctoring events.
    """
    return await ProctoringController.create_event_batch(batch_data, current_user)


@router.get("/interview/{interview_id}/events")
async def get_interview_events(
    interview_id: str,
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
):
    """
    GET /api/proctoring/interview/{interview_id}/events

    Retrieve paged proctoring events for a specific interview.
    """
    return await ProctoringController.get_interview_events(
        interview_id=interview_id,
        limit=limit,
        skip=skip,
        current_user=current_user,
    )


@router.get("/interview/{interview_id}/summary")
async def get_interview_summary(
    interview_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    GET /api/proctoring/interview/{interview_id}/summary

    Generate an aggregated summary of all proctoring events for an interview.
    """
    return await ProctoringController.get_interview_summary(
        interview_id=interview_id,
        current_user=current_user,
    )
