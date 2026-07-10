"""
Cheating Detection Controller
Handles service delegation and response formatting
for all Cheating Detection endpoints using FastAPI JSONResponse.
"""

import logging
from fastapi.responses import JSONResponse

try:
    from services import cheating_detection_service
except ImportError:
    from app.services import cheating_detection_service

logger = logging.getLogger(__name__)


def _handle_value_error(error: ValueError) -> JSONResponse:
    """
    Map ValueErrors to appropriate HTTP status codes based on message content.
    """
    msg = str(error)
    if "permission" in msg or "denied" in msg or "access" in msg:
        status_code = 403
    elif "not found" in msg:
        status_code = 404
    else:
        status_code = 400

    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "message": msg,
        }
    )


class CheatingDetectionController:
    """Cheating Detection Controller"""

    @staticmethod
    async def analyze_interview(interview_id: str, current_user: dict) -> JSONResponse:
        """
        POST /api/cheating/interview/<interview_id>/analyze

        Runs cheating risk analysis on the proctoring events logged for the interview.
        """
        try:
            user_role = str(current_user["role"])
            report = cheating_detection_service.analyze_interview(
                interview_id=interview_id,
                user_role=user_role
            )

            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "Interview cheating risk analysis completed.",
                    "data": report,
                }
            )

        except ValueError as error:
            return _handle_value_error(error)
        except Exception as error:
            logger.error("Unexpected error during cheating risk analysis: %s", error)
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": "An unexpected error occurred. Please try again.",
                }
            )

    @staticmethod
    async def get_report(interview_id: str, current_user: dict) -> JSONResponse:
        """
        GET /api/cheating/interview/<interview_id>/report

        Retrieves the computed cheating report metadata for the interview.
        """
        try:
            user_role = str(current_user["role"])
            report = cheating_detection_service.get_cheating_report(
                interview_id=interview_id,
                user_role=user_role
            )

            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "data": report,
                }
            )

        except ValueError as error:
            return _handle_value_error(error)
        except Exception as error:
            logger.error("Unexpected error fetching cheating report for interview %s: %s", interview_id, error)
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": "An unexpected error occurred. Please try again.",
                }
            )
