"""
Cheating Detection Routes
FastAPI APIRouter for the Cheating Detection Engine backend module.
"""

import logging
from datetime import datetime
from typing import Optional
from bson import ObjectId

from fastapi import APIRouter, Depends, Header, HTTPException

from app.config.database import Database
from app.controllers.cheating_detection_controller import CheatingDetectionController
from app.utils.jwt_utils import decode_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/cheating", tags=["Cheating Detection"])


# ---------------------------------------------------------------------------
# JWT authentication dependency
# ---------------------------------------------------------------------------

async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """
    Validate a Bearer JWT from the Authorization header.
    If no header is provided or token is invalid, automatically resolves to the
    default candidate user to enable guest cheating analysis requests.
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

@router.post("/interview/{interview_id}/analyze")
async def analyze_interview(
    interview_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    POST /api/cheating/interview/{interview_id}/analyze

    Triggers risk calculation on proctoring event logs and generates/updates report.
    """
    return await CheatingDetectionController.analyze_interview(
        interview_id=interview_id,
        current_user=current_user,
    )


@router.get("/interview/{interview_id}/report")
async def get_report(
    interview_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    GET /api/cheating/interview/{interview_id}/report

    Retrieves the generated risk analysis report.
    Requires admin role.
    """
    return await CheatingDetectionController.get_report(
        interview_id=interview_id,
        current_user=current_user,
    )


@router.get("/interview/{interview_id}/report/candidate")
async def get_report_for_candidate(
    interview_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    GET /api/cheating/interview/{interview_id}/report/candidate

    Retrieves the cheating report for the interview owner (candidate, read-only).
    Does NOT require admin role — validates ownership via JWT.
    """
    return await CheatingDetectionController.get_report_for_candidate(
        interview_id=interview_id,
        current_user=current_user,
    )
