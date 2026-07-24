"""
Interview Session Routes
========================
FastAPI APIRouter that exposes the unified interview session endpoints.
These endpoints orchestrate the Video Recording, Live Proctoring, Cheating
Detection, and Interview Analytics modules into a single workflow.

Endpoints
---------
POST   /api/interview/start                   — Start unified session
GET    /api/interview/proctoring/{sessionId}  — Live proctoring status
GET    /api/interview/cheating/{sessionId}    — Live cheating risk status
POST   /api/interview/end/{sessionId}         — End session (auto-runs analysis)
GET    /api/interview-analytics/{sessionId}   — Fetch analytics report
"""

import logging
from datetime import datetime
from typing import Optional
from bson import ObjectId

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.utils.jwt_utils import decode_token
from app.config.database import Database
import app.services.interview_session_service as session_service

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Routers — two separate prefixes as per the spec
# ---------------------------------------------------------------------------

router          = APIRouter(prefix="/api/interview",           tags=["Interview Session"])
analytics_router = APIRouter(prefix="/api/interview-analytics", tags=["Interview Session"])


# ---------------------------------------------------------------------------
# JWT Authentication Dependency
# ---------------------------------------------------------------------------

async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
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
# Request schemas
# ---------------------------------------------------------------------------

class StartSessionRequest(BaseModel):
    """Body for POST /api/interview/start"""
    jobRole:         str            = Field(..., min_length=1, max_length=200, description="Target job role")
    interviewType:   str            = Field("TECHNICAL",   description="TECHNICAL | HR | BEHAVIORAL | RESUME_BASED")
    difficulty:      str            = Field("MEDIUM",      description="EASY | MEDIUM | HARD")
    totalQuestions:  int            = Field(5,    ge=1, le=20, description="Number of questions")
    durationSeconds: int            = Field(1800, ge=300, le=7200, description="Session time limit")
    resumeId:        Optional[str]  = Field(None, description="Required for RESUME_BASED type")


# ---------------------------------------------------------------------------
# Routes — /api/interview/*
# ---------------------------------------------------------------------------

@router.post(
    "/start",
    summary="Start a unified interview session",
)
async def start_session(
    body: StartSessionRequest,
    current_user: dict = Depends(get_current_user),
) -> JSONResponse:
    try:
        user_id = str(current_user["id"])

        result = session_service.start_session(
            user_id=user_id,
            job_role=body.jobRole,
            interview_type=body.interviewType,
            difficulty=body.difficulty,
            total_questions=body.totalQuestions,
            duration_seconds=body.durationSeconds,
            resume_id=body.resumeId,
        )

        return JSONResponse(
            status_code=201,
            content={
                "success":  True,
                "message":  "Interview session started successfully.",
                "data":     result,
            },
        )

    except ValueError as error:
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": str(error)},
        )
    except RuntimeError as error:
        logger.error("[SessionRoute] start_session error: %s", error)
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": str(error)},
        )
    except Exception as error:
        logger.error("[SessionRoute] Unexpected error starting session: %s", error)
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "An unexpected error occurred. Please try again."},
        )


@router.get(
    "/proctoring/{session_id}",
    summary="Get live proctoring status for a session",
)
async def get_proctoring_status(
    session_id: str,
    current_user: dict = Depends(get_current_user),
) -> JSONResponse:
    try:
        user_id = str(current_user["id"])

        status = session_service.get_proctoring_status(
            interview_id=session_id,
            user_id=user_id,
        )

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data":    status,
            },
        )

    except ValueError as error:
        msg = str(error)
        status_code = 403 if "permission" in msg.lower() else 404 if "not found" in msg.lower() else 400
        return JSONResponse(
            status_code=status_code,
            content={"success": False, "message": msg},
        )
    except Exception as error:
        logger.error("[SessionRoute] get_proctoring_status error for %s: %s", session_id, error)
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "An unexpected error occurred. Please try again."},
        )


@router.get(
    "/cheating/{session_id}",
    summary="Get live cheating detection risk status for a session",
)
async def get_cheating_status(
    session_id: str,
    current_user: dict = Depends(get_current_user),
) -> JSONResponse:
    try:
        user_id = str(current_user["id"])

        cheating_status = session_service.get_cheating_status(
            interview_id=session_id,
            user_id=user_id,
        )

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data":    cheating_status,
            },
        )

    except ValueError as error:
        msg = str(error)
        status_code = 403 if "permission" in msg.lower() else 404 if "not found" in msg.lower() else 400
        return JSONResponse(
            status_code=status_code,
            content={"success": False, "message": msg},
        )
    except Exception as error:
        logger.error("[SessionRoute] get_cheating_status error for %s: %s", session_id, error)
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "An unexpected error occurred. Please try again."},
        )


@router.post(
    "/end/{session_id}",
    summary="End a unified interview session",
)
async def end_session(
    session_id: str,
    current_user: dict = Depends(get_current_user),
) -> JSONResponse:
    try:
        user_id = str(current_user["id"])

        result = session_service.end_session(
            interview_id=session_id,
            user_id=user_id,
        )

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Interview session ended successfully. Analytics are being generated.",
                "data":    result,
            },
        )

    except ValueError as error:
        msg = str(error)
        status_code = 409 if "already" in msg.lower() else 403 if "permission" in msg.lower() else 400
        return JSONResponse(
            status_code=status_code,
            content={"success": False, "message": msg},
        )
    except RuntimeError as error:
        logger.error("[SessionRoute] end_session error for %s: %s", session_id, error)
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": str(error)},
        )
    except Exception as error:
        logger.error("[SessionRoute] Unexpected error ending session %s: %s", session_id, error)
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "An unexpected error occurred. Please try again."},
        )


# ---------------------------------------------------------------------------
# Routes — /api/interview-analytics/*
# ---------------------------------------------------------------------------

@analytics_router.get(
    "/{session_id}",
    summary="Fetch interview analytics report",
)
async def get_interview_analytics(
    session_id: str,
    refresh: bool = Query(False),
    current_user: dict = Depends(get_current_user),
) -> JSONResponse:
    try:
        user_id   = str(current_user["id"])
        user_role = str(current_user.get("role", "candidate"))

        report = session_service.get_analytics_report(
            interview_id=session_id,
            user_id=user_id,
            user_role=user_role,
            force_refresh=refresh,
        )

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data":    report,
            },
        )

    except ValueError as error:
        msg = str(error)
        status_code = 403 if "permission" in msg.lower() else 404 if "not found" in msg.lower() else 400
        return JSONResponse(
            status_code=status_code,
            content={"success": False, "message": msg},
        )
    except Exception as error:
        logger.error("[SessionRoute] get_interview_analytics error for %s: %s", session_id, error)
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "An unexpected error occurred. Please try again."},
        )
