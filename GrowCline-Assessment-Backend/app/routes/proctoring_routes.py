"""
Proctoring Routes
FastAPI APIRouter for the Live Proctoring module.
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, Header, HTTPException, Query

try:
    from controllers.proctoring_controller import ProctoringController
    from middleware.jwt_utils import decode_token
    from schemas.proctoring_schema import (
        ProctoringEventCreate,
        ProctoringEventBatchCreate,
    )
except ImportError:
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

async def get_current_user(authorization: str = Header(...)) -> dict:
    """
    Dependency that validates a Bearer JWT token from the Authorization header.
    Returns the authenticated user dict.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authentication token is required."
        )

    token = authorization.split(" ", 1)[1].strip()
    payload = decode_token(token)

    if not payload or "id" not in payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token."
        )

    return {
        "id": payload.get("id"),
        "email": payload.get("email"),
        "role": payload.get("role"),
    }


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
