"""
Interview Analytics Controller
Handles service delegation and response formatting for all
Interview Analytics endpoints using FastAPI JSONResponse.

No business logic lives here — all logic is delegated to the service layer.
"""

import logging
from fastapi.responses import JSONResponse

try:
    from services import interview_analytics_service
except ImportError:
    from app.services import interview_analytics_service

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Shared error mapping helper
# ---------------------------------------------------------------------------

def _handle_value_error(error: ValueError) -> JSONResponse:
    """
    Map a ValueError raised by the service layer to the appropriate
    HTTP status code, following the existing Team B convention.
    """
    msg = str(error)

    if "permission" in msg or "access" in msg or "denied" in msg:
        status_code = 403
    elif "not found" in msg:
        status_code = 404
    elif "already exist" in msg:
        status_code = 409
    else:
        status_code = 400

    return JSONResponse(
        status_code=status_code,
        content={"success": False, "message": msg},
    )


# ---------------------------------------------------------------------------
# Controller class
# ---------------------------------------------------------------------------

class InterviewAnalyticsController:
    """Interview Analytics Controller — thin delegation layer."""

    @staticmethod
    async def generate_analytics(
        interview_id: str,
        current_user: dict,
        force_refresh: bool = False,
    ) -> JSONResponse:
        """
        POST /api/analytics/interview/{interview_id}/generate

        Generates (or refreshes) an analytics report for the given interview.
        """
        try:
            user_id = str(current_user["id"])
            user_role = str(current_user["role"])

            report = interview_analytics_service.generate_analytics(
                interview_id=interview_id,
                user_id=user_id,
                user_role=user_role,
                force_refresh=force_refresh,
            )

            return JSONResponse(
                status_code=201,
                content={
                    "success": True,
                    "message": "Interview analytics generated successfully.",
                    "data": report,
                },
            )

        except ValueError as error:
            return _handle_value_error(error)
        except Exception as error:
            logger.error(
                "Unexpected error generating analytics for interview %s: %s",
                interview_id,
                error,
            )
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": "An unexpected error occurred. Please try again.",
                },
            )

    @staticmethod
    async def get_analytics(interview_id: str, current_user: dict) -> JSONResponse:
        """
        GET /api/analytics/interview/{interview_id}

        Retrieves the analytics report for the given interview.
        """
        try:
            user_id = str(current_user["id"])
            user_role = str(current_user["role"])

            report = interview_analytics_service.get_analytics(
                interview_id=interview_id,
                user_id=user_id,
                user_role=user_role,
            )

            return JSONResponse(
                status_code=200,
                content={"success": True, "data": report},
            )

        except ValueError as error:
            return _handle_value_error(error)
        except Exception as error:
            logger.error(
                "Unexpected error fetching analytics for interview %s: %s",
                interview_id,
                error,
            )
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": "An unexpected error occurred. Please try again.",
                },
            )

    @staticmethod
    async def get_user_analytics(user_id: str, current_user: dict) -> JSONResponse:
        """
        GET /api/analytics/user/{user_id}

        Retrieves all analytics reports for a candidate, newest first.
        """
        try:
            requesting_user_id = str(current_user["id"])
            user_role = str(current_user["role"])

            result = interview_analytics_service.get_user_analytics(
                target_user_id=user_id,
                requesting_user_id=requesting_user_id,
                user_role=user_role,
            )

            return JSONResponse(
                status_code=200,
                content={"success": True, "data": result},
            )

        except ValueError as error:
            return _handle_value_error(error)
        except Exception as error:
            logger.error(
                "Unexpected error fetching analytics for user %s: %s",
                user_id,
                error,
            )
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": "An unexpected error occurred. Please try again.",
                },
            )

    @staticmethod
    async def delete_analytics(interview_id: str, current_user: dict) -> JSONResponse:
        """
        DELETE /api/analytics/interview/{interview_id}

        Deletes the analytics report for the given interview.
        """
        try:
            user_id = str(current_user["id"])
            user_role = str(current_user["role"])

            result = interview_analytics_service.delete_analytics(
                interview_id=interview_id,
                user_id=user_id,
                user_role=user_role,
            )

            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "Interview analytics deleted successfully.",
                    "data": result,
                },
            )

        except ValueError as error:
            return _handle_value_error(error)
        except Exception as error:
            logger.error(
                "Unexpected error deleting analytics for interview %s: %s",
                interview_id,
                error,
            )
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": "An unexpected error occurred. Please try again.",
                },
            )
