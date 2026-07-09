"""
Proctoring Controller
Handles service delegation and response formatting
for all Live Proctoring endpoints using FastAPI JSONResponse.
"""

import logging
from datetime import datetime
from fastapi.responses import JSONResponse

try:
    from services import proctoring_service
except ImportError:
    from app.services import proctoring_service

logger = logging.getLogger(__name__)


def _handle_value_error(error: ValueError) -> JSONResponse:
    """
    Map ValueErrors to appropriate HTTP status codes based on message content.
    """
    msg = str(error)
    if "permission" in msg or "have permission" in msg or "access" in msg:
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


class ProctoringController:
    """Live Proctoring Controller"""

    @staticmethod
    async def create_event(event_data, current_user: dict) -> JSONResponse:
        """
        POST /api/proctoring/events

        Logs a single proctoring event.
        """
        try:
            user_id = str(current_user["id"])
            event = proctoring_service.create_proctoring_event(
                interview_id=event_data.interview_id,
                user_id=user_id,
                event_type=event_data.event_type,
                client_timestamp=event_data.client_timestamp,
            )

            return JSONResponse(
                status_code=201,
                content={
                    "success": True,
                    "message": "Event recorded successfully.",
                    "data": event,
                }
            )

        except ValueError as error:
            return _handle_value_error(error)
        except Exception as error:
            logger.error("Unexpected error during event creation: %s", error)
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": "An unexpected error occurred. Please try again.",
                }
            )

    @staticmethod
    async def create_event_batch(batch_data, current_user: dict) -> JSONResponse:
        """
        POST /api/proctoring/events/batch

        Logs a batch of proctoring events.
        """
        try:
            user_id = str(current_user["id"])
            events_in = [
                {
                    "event_type": item.event_type,
                    "client_timestamp": item.client_timestamp,
                }
                for item in batch_data.events
            ]

            inserted_events = proctoring_service.create_proctoring_events_batch(
                interview_id=batch_data.interview_id,
                user_id=user_id,
                events=events_in,
            )

            return JSONResponse(
                status_code=201,
                content={
                    "success": True,
                    "message": f"Successfully ingested {len(inserted_events)} events.",
                    "data": inserted_events,
                }
            )

        except ValueError as error:
            return _handle_value_error(error)
        except Exception as error:
            logger.error("Unexpected error during batch event ingestion: %s", error)
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": "An unexpected error occurred. Please try again.",
                }
            )

    @staticmethod
    async def get_interview_events(interview_id: str, limit: int, skip: int, current_user: dict) -> JSONResponse:
        """
        GET /api/proctoring/interview/<interview_id>/events

        Retrieves a paged list of events for the interview.
        """
        try:
            user_id = str(current_user["id"])
            result = proctoring_service.get_proctoring_events(
                interview_id=interview_id,
                user_id=user_id,
                limit=limit,
                skip=skip,
            )

            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "data": result,
                }
            )

        except ValueError as error:
            return _handle_value_error(error)
        except Exception as error:
            logger.error("Unexpected error fetching events for interview %s: %s", interview_id, error)
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": "An unexpected error occurred. Please try again.",
                }
            )

    @staticmethod
    async def get_interview_summary(interview_id: str, current_user: dict) -> JSONResponse:
        """
        GET /api/proctoring/interview/<interview_id>/summary

        Generates a summary of all proctoring events for the interview.
        """
        try:
            user_id = str(current_user["id"])
            result = proctoring_service.get_proctoring_summary(
                interview_id=interview_id,
                user_id=user_id,
            )

            # Format timestamps to ISO strings if they are datetime objects
            first_event_at = result["firstEventAt"]
            last_event_at = result["lastEventAt"]
            if isinstance(first_event_at, datetime):
                result["firstEventAt"] = first_event_at.isoformat()
            if isinstance(last_event_at, datetime):
                result["lastEventAt"] = last_event_at.isoformat()

            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "data": result,
                }
            )

        except ValueError as error:
            return _handle_value_error(error)
        except Exception as error:
            logger.error("Unexpected error generating proctoring summary for interview %s: %s", interview_id, error)
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": "An unexpected error occurred. Please try again.",
                }
            )
