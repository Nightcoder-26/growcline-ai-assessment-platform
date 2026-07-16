"""
Cheating Detection Routes
FastAPI APIRouter for the Cheating Detection Engine backend module.
"""

import logging
from fastapi import APIRouter, Depends, Header, HTTPException

try:
    from controllers.cheating_detection_controller import CheatingDetectionController
    from middleware.jwt_utils import decode_token
except ImportError:
    from app.controllers.cheating_detection_controller import CheatingDetectionController
    from app.middleware.jwt_utils import decode_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/cheating", tags=["Cheating Detection"])


# ---------------------------------------------------------------------------
# JWT authentication dependency
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
    """
    return await CheatingDetectionController.get_report(
        interview_id=interview_id,
        current_user=current_user,
    )
