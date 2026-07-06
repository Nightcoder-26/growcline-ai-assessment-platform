"""
Recording Routes
Flask Blueprint for the Video Recording module.

All endpoints require JWT authentication.
The authenticated user context is passed directly to the controller
so that ownership validation can be performed in the service layer.

Route ordering note:
    /api/recordings/upload         — registered before /<recording_id>
    /api/recordings/interview/<id> — registered before /<recording_id>
    /api/recordings/<id>/url       — registered with explicit suffix
    /api/recordings/<id>           — generic single-resource routes
"""

import logging
from functools import wraps

import jwt
from flask import Blueprint, request, jsonify

try:
    from config.settings import Config
    from controllers.recording_controller import RecordingController
except ImportError:
    from app.config.settings import Config
    from app.controllers.recording_controller import RecordingController


logger = logging.getLogger(__name__)

recording_bp = Blueprint("recordings", __name__, url_prefix="/api/recordings")


# ---------------------------------------------------------------------------
# JWT authentication decorator
# ---------------------------------------------------------------------------

def require_auth(f):
    """
    Decorator that validates a Bearer JWT token from the Authorization header.

    On success, injects `current_user` as the first positional argument to
    the decorated view function.  The current_user dict contains:
        {"id": str, "email": str, "role": str}

    On failure, returns the project's standard error response with 401.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return jsonify({
                "success": False,
                "message": "Authentication token is required.",
            }), 401

        token = auth_header.split(" ", 1)[1].strip()

        try:
            payload = jwt.decode(
                token,
                Config.JWT_SECRET,
                algorithms=["HS256"],
            )
        except jwt.ExpiredSignatureError:
            return jsonify({
                "success": False,
                "message": "Authentication token has expired.",
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                "success": False,
                "message": "Invalid authentication token.",
            }), 401

        current_user = {
            "id": payload.get("id"),
            "email": payload.get("email"),
            "role": payload.get("role"),
        }

        return f(current_user, *args, **kwargs)

    return decorated


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@recording_bp.route("/upload", methods=["POST"])
@require_auth
def upload_recording(current_user):
    """
    POST /api/recordings/upload

    Upload a completed recording file (video and/or audio) for an interview.
    Accepts multipart/form-data with fields: interview_id, duration, video_file, audio_file.
    """
    return RecordingController.upload_recording(current_user)


@recording_bp.route("/interview/<interview_id>", methods=["GET"])
@require_auth
def get_interview_recordings(current_user, interview_id):
    """
    GET /api/recordings/interview/<interview_id>

    List all recordings for the specified interview.
    Validates interview ownership before returning results.

    Registered before /<recording_id> to prevent Flask capturing
    the literal string "interview" as a recording_id parameter.
    """
    return RecordingController.get_interview_recordings(interview_id, current_user)


@recording_bp.route("/<recording_id>/url", methods=["GET"])
@require_auth
def get_recording_url(current_user, recording_id):
    """
    GET /api/recordings/<recording_id>/url

    Generate temporary presigned S3 GET URLs for the recording's media objects.
    """
    return RecordingController.get_recording_url(recording_id, current_user)


@recording_bp.route("/<recording_id>", methods=["GET"])
@require_auth
def get_recording(current_user, recording_id):
    """
    GET /api/recordings/<recording_id>

    Retrieve metadata for a single recording.
    Does not return presigned media URLs — use /url for playback access.
    """
    return RecordingController.get_recording(recording_id, current_user)


@recording_bp.route("/<recording_id>", methods=["DELETE"])
@require_auth
def delete_recording(current_user, recording_id):
    """
    DELETE /api/recordings/<recording_id>

    Delete a recording's S3 objects and its MongoDB metadata.
    Only the recording owner may perform this operation.
    """
    return RecordingController.delete_recording(recording_id, current_user)
