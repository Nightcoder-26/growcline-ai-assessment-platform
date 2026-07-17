"""
Interview Analytics Routes
FastAPI APIRouter for the Interview Analytics module.

Routes:
    POST   /api/analytics/interview/{interview_id}/generate  — generate report
    GET    /api/analytics/interview/{interview_id}           — get report
    GET    /api/analytics/user/{user_id}                     — list user reports
    DELETE /api/analytics/interview/{interview_id}           — delete report
"""

import logging
from fastapi import APIRouter, Depends, Header, HTTPException

try:
    from controllers.interview_analytics_controller import InterviewAnalyticsController
    from middleware.jwt_utils import decode_token
    from schemas.interview_analytics_schema import AnalyticsGenerateRequest
except ImportError:
    from app.controllers.interview_analytics_controller import InterviewAnalyticsController
    from app.middleware.jwt_utils import decode_token
    from app.schemas.interview_analytics_schema import AnalyticsGenerateRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analytics", tags=["Interview Analytics"])


# ---------------------------------------------------------------------------
# JWT authentication dependency
# ---------------------------------------------------------------------------

async def get_current_user(authorization: str = Header(...)) -> dict:
    """
    Dependency that validates a Bearer JWT token from the Authorization header.
    Returns the authenticated user dict.

    Never trusts user identity from the request body or query params.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authentication token is required.",
        )

    token = authorization.split(" ", 1)[1].strip()
    payload = decode_token(token)

    if not payload or "id" not in payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token.",
        )

    return {
        "id": payload.get("id"),
        "email": payload.get("email"),
        "role": payload.get("role"),
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post("/interview/{interview_id}/generate")
async def generate_analytics(
    interview_id: str,
    body: AnalyticsGenerateRequest = None,
    current_user: dict = Depends(get_current_user),
):
    """
    POST /api/analytics/interview/{interview_id}/generate

    Generate an analytics report for the completed interview.

    Steps:
        1. Authenticate via JWT.
        2. Validate interview exists and is completed.
        3. Verify ownership / admin access.
        4. Guard against duplicate generation (unless force_refresh=True).
        5. Fetch recording, proctoring, and cheating data.
        6. Compute metrics and persist to interview_analytics.
        7. Return the generated report.
    """
    force_refresh = body.force_refresh if body else False
    return await InterviewAnalyticsController.generate_analytics(
        interview_id=interview_id,
        current_user=current_user,
        force_refresh=force_refresh,
    )


@router.get("/interview/{interview_id}")
async def get_analytics(
    interview_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    GET /api/analytics/interview/{interview_id}

    Retrieve the analytics report for a specific interview.
    """
    return await InterviewAnalyticsController.get_analytics(
        interview_id=interview_id,
        current_user=current_user,
    )


@router.get("/user/{user_id}")
async def get_user_analytics(
    user_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    GET /api/analytics/user/{user_id}

    Retrieve all interview analytics reports for a candidate, newest first.
    Admins may query any user; candidates are limited to their own data.
    """
    return await InterviewAnalyticsController.get_user_analytics(
        user_id=user_id,
        current_user=current_user,
    )


@router.delete("/interview/{interview_id}")
async def delete_analytics(
    interview_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    DELETE /api/analytics/interview/{interview_id}

    Delete the analytics report associated with a specific interview.
    Intended to be called when the parent interview is deleted.
    """
    return await InterviewAnalyticsController.delete_analytics(
        interview_id=interview_id,
        current_user=current_user,
    )
