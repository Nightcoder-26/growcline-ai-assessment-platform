"""
Recording Controller
Handles service delegation and response formatting
for all Video Recording endpoints using FastAPI JSONResponse.
"""

import logging

from fastapi.responses import JSONResponse, StreamingResponse

try:
    from services import recording_service
except ImportError:
    from app.services import recording_service

logger = logging.getLogger(__name__)


class RecordingController:
    """Video Recording Controller"""

    @staticmethod
    async def upload_recording(interview_id, duration, video_file, audio_file, current_user):
        """
        POST /api/recordings/upload

        Accepts multipart/form-data parameters, validates request fields,
        delegates logic to recording_service, and returns a JSONResponse.
        """
        try:
            if not interview_id:
                return JSONResponse(
                    status_code=400,
                    content={
                        "success": False,
                        "message": "interview_id is required."
                    }
                )

            user_id = str(current_user["id"])

            recording = recording_service.upload_recording(
                interview_id=interview_id,
                user_id=user_id,
                video_file=video_file,
                audio_file=audio_file,
                duration=duration,
            )

            return JSONResponse(
                status_code=201,
                content={
                    "success": True,
                    "message": "Recording uploaded successfully.",
                    "data": recording,
                }
            )

        except ValueError as error:
            err_msg = str(error)
            status_code = 413 if "exceeds the maximum" in err_msg.lower() else 400
            return JSONResponse(
                status_code=status_code,
                content={
                    "success": False,
                    "message": err_msg,
                }
            )

        except RuntimeError as error:
            logger.error("Recording upload error: %s", error)
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": str(error),
                }
            )

        except Exception as error:
            logger.error("Unexpected error during recording upload: %s", error)
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": "An unexpected error occurred. Please try again.",
                }
            )

    @staticmethod
    async def get_recording(recording_id, current_user):
        """
        GET /api/recordings/<recording_id>

        Returns recording metadata for the authenticated owner.
        """
        try:
            user_id = str(current_user["id"])

            recording = recording_service.get_recording(
                recording_id=recording_id,
                user_id=user_id,
            )

            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "data": recording,
                }
            )

        except ValueError as error:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "message": str(error),
                }
            )

        except Exception as error:
            logger.error("Unexpected error fetching recording %s: %s", recording_id, error)
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": "An unexpected error occurred. Please try again.",
                }
            )

    @staticmethod
    async def get_interview_recordings(interview_id, current_user):
        """
        GET /api/recordings/interview/<interview_id>

        Returns all recording documents for an interview, ordered by createdAt ascending.
        """
        try:
            user_id = str(current_user["id"])

            result = recording_service.get_recordings_for_interview(
                interview_id=interview_id,
                user_id=user_id,
            )

            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "data": result,
                }
            )

        except ValueError as error:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "message": str(error),
                }
            )

        except Exception as error:
            logger.error(
                "Unexpected error listing recordings for interview %s: %s",
                interview_id, error,
            )
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": "An unexpected error occurred. Please try again.",
                }
            )

    @staticmethod
    async def get_recording_url(recording_id, current_user):
        """
        GET /api/recordings/<recording_id>/url

        Returns backend-proxied stream URLs for the recording's media objects.
        The Google Drive file ID is never exposed to the frontend.
        """
        try:
            user_id = str(current_user["id"])

            url_data = recording_service.get_recording_access_urls(
                recording_id=recording_id,
                user_id=user_id,
            )

            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "data": url_data,
                }
            )

        except ValueError as error:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "message": str(error),
                }
            )

        except RuntimeError as error:
            logger.error("Stream URL generation error for %s: %s", recording_id, error)
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": str(error),
                }
            )

        except Exception as error:
            logger.error(
                "Unexpected error generating URLs for recording %s: %s",
                recording_id, error,
            )
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": "An unexpected error occurred. Please try again.",
                }
            )

    @staticmethod
    async def stream_recording(recording_id, current_user):
        """
        GET /api/recordings/<recording_id>/stream

        Proxies the Google Drive video content through the backend so the
        frontend can embed it in a <video> element without making the Drive
        file or folder publicly accessible.
        """
        try:
            user_id = str(current_user["id"])

            buffer, mime_type, file_name = recording_service.stream_recording(
                recording_id=recording_id,
                user_id=user_id,
            )

            def _iter_content():
                chunk_size = 1024 * 1024  # 1 MB
                while True:
                    chunk = buffer.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk

            return StreamingResponse(
                _iter_content(),
                media_type=mime_type,
                headers={
                    "Content-Disposition": f'inline; filename="{file_name}"',
                    "Cache-Control": "no-store",
                },
            )

        except ValueError as error:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "message": str(error),
                }
            )

        except RuntimeError as error:
            logger.error("Stream error for recording %s: %s", recording_id, error)
            return JSONResponse(
                status_code=502,
                content={
                    "success": False,
                    "message": str(error),
                }
            )

        except Exception as error:
            logger.error(
                "Unexpected error streaming recording %s: %s",
                recording_id, error,
            )
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": "An unexpected error occurred. Please try again.",
                }
            )

    @staticmethod
    async def delete_recording(recording_id, current_user):
        """
        DELETE /api/recordings/<recording_id>

        Deletes a recording's Google Drive file(s) and its MongoDB metadata.
        Only the recording owner may perform this operation.
        """
        try:
            user_id = str(current_user["id"])

            result = recording_service.delete_recording(
                recording_id=recording_id,
                user_id=user_id,
            )

            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": result["message"],
                }
            )

        except ValueError as error:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "message": str(error),
                }
            )

        except RuntimeError as error:
            logger.error("Recording deletion error for %s: %s", recording_id, error)
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": str(error),
                }
            )

        except Exception as error:
            logger.error(
                "Unexpected error deleting recording %s: %s",
                recording_id, error,
            )
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": "An unexpected error occurred. Please try again.",
                }
            )
