"""
Recording Controller
Handles HTTP request extraction, service delegation, and response formatting
for all Video Recording endpoints.

Follows Team A's controller pattern:
- Static methods on a class
- Uses flask.request to extract form fields, files, and query parameters
- Calls service layer for all business logic
- Returns (jsonify({...}), status_code) tuples
- Catches ValueError for client errors (400/404) and RuntimeError for server errors (500)
"""

import logging

from flask import request, jsonify

try:
    from services import recording_service
except ImportError:
    from app.services import recording_service


logger = logging.getLogger(__name__)


class RecordingController:
    """Video Recording Controller"""

    @staticmethod
    def upload_recording(current_user):
        """
        POST /api/recordings/upload

        Accepts a multipart/form-data request with:
            - interview_id (form field, required)
            - duration     (form field, optional float — seconds)
            - video_file   (file field, optional)
            - audio_file   (file field, optional)

        At least one of video_file or audio_file must be present.
        """
        try:
            interview_id = request.form.get("interview_id", "").strip()
            duration_raw = request.form.get("duration", None)

            if not interview_id:
                return jsonify({
                    "success": False,
                    "message": "interview_id is required."
                }), 400

            duration = None
            if duration_raw is not None and duration_raw.strip() != "":
                try:
                    duration = float(duration_raw)
                except ValueError:
                    return jsonify({
                        "success": False,
                        "message": "duration must be a numeric value representing seconds."
                    }), 400

            video_file = request.files.get("video_file")
            audio_file = request.files.get("audio_file")

            user_id = str(current_user["id"])

            recording = recording_service.upload_recording(
                interview_id=interview_id,
                user_id=user_id,
                video_file=video_file,
                audio_file=audio_file,
                duration=duration,
            )

            return jsonify({
                "success": True,
                "message": "Recording uploaded successfully.",
                "data": recording,
            }), 201

        except ValueError as error:
            return jsonify({
                "success": False,
                "message": str(error),
            }), 400

        except RuntimeError as error:
            logger.error("Recording upload error: %s", error)
            return jsonify({
                "success": False,
                "message": str(error),
            }), 500

        except Exception as error:
            logger.error("Unexpected error during recording upload: %s", error)
            return jsonify({
                "success": False,
                "message": "An unexpected error occurred. Please try again.",
            }), 500

    @staticmethod
    def get_recording(recording_id, current_user):
        """
        GET /api/recordings/<recording_id>

        Returns recording metadata for the authenticated owner.
        Does not include presigned media URLs — use the /url endpoint for playback.
        """
        try:
            user_id = str(current_user["id"])

            recording = recording_service.get_recording(
                recording_id=recording_id,
                user_id=user_id,
            )

            return jsonify({
                "success": True,
                "data": recording,
            }), 200

        except ValueError as error:
            return jsonify({
                "success": False,
                "message": str(error),
            }), 404

        except Exception as error:
            logger.error("Unexpected error fetching recording %s: %s", recording_id, error)
            return jsonify({
                "success": False,
                "message": "An unexpected error occurred. Please try again.",
            }), 500

    @staticmethod
    def get_interview_recordings(interview_id, current_user):
        """
        GET /api/recordings/interview/<interview_id>

        Returns all recording documents for an interview, ordered by createdAt ascending.
        Validates interview ownership before returning results.
        """
        try:
            user_id = str(current_user["id"])

            result = recording_service.get_recordings_for_interview(
                interview_id=interview_id,
                user_id=user_id,
            )

            return jsonify({
                "success": True,
                "data": result,
            }), 200

        except ValueError as error:
            return jsonify({
                "success": False,
                "message": str(error),
            }), 404

        except Exception as error:
            logger.error(
                "Unexpected error listing recordings for interview %s: %s",
                interview_id, error,
            )
            return jsonify({
                "success": False,
                "message": "An unexpected error occurred. Please try again.",
            }), 500

    @staticmethod
    def get_recording_url(recording_id, current_user):
        """
        GET /api/recordings/<recording_id>/url

        Generates and returns temporary presigned S3 GET URLs for the recording's
        media objects.  URLs expire after RECORDING_URL_EXPIRY_SECONDS seconds.
        """
        try:
            user_id = str(current_user["id"])

            url_data = recording_service.get_recording_access_urls(
                recording_id=recording_id,
                user_id=user_id,
            )

            return jsonify({
                "success": True,
                "data": url_data,
            }), 200

        except ValueError as error:
            return jsonify({
                "success": False,
                "message": str(error),
            }), 404

        except RuntimeError as error:
            logger.error("Presigned URL generation error for %s: %s", recording_id, error)
            return jsonify({
                "success": False,
                "message": str(error),
            }), 500

        except Exception as error:
            logger.error(
                "Unexpected error generating URLs for recording %s: %s",
                recording_id, error,
            )
            return jsonify({
                "success": False,
                "message": "An unexpected error occurred. Please try again.",
            }), 500

    @staticmethod
    def delete_recording(recording_id, current_user):
        """
        DELETE /api/recordings/<recording_id>

        Deletes a recording's S3 objects and its MongoDB metadata.
        S3 objects must be deleted successfully before the metadata is removed
        to prevent orphaned object references from being lost.
        """
        try:
            user_id = str(current_user["id"])

            result = recording_service.delete_recording(
                recording_id=recording_id,
                user_id=user_id,
            )

            return jsonify({
                "success": True,
                "message": result["message"],
            }), 200

        except ValueError as error:
            return jsonify({
                "success": False,
                "message": str(error),
            }), 404

        except RuntimeError as error:
            logger.error("Recording deletion error for %s: %s", recording_id, error)
            return jsonify({
                "success": False,
                "message": str(error),
            }), 500

        except Exception as error:
            logger.error(
                "Unexpected error deleting recording %s: %s",
                recording_id, error,
            )
            return jsonify({
                "success": False,
                "message": "An unexpected error occurred. Please try again.",
            }), 500
