"""
Recording Routes
FastAPI APIRouter for the Video Recording module.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException, Header
from fastapi.responses import JSONResponse

try:
    from controllers.recording_controller import RecordingController
    from middleware.jwt_utils import decode_token
except ImportError:
    from app.controllers.recording_controller import RecordingController
    from app.middleware.jwt_utils import decode_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/recordings", tags=["Recordings"])


# ---------------------------------------------------------------------------
# JWT authentication dependency
# ---------------------------------------------------------------------------

async def get_current_user(authorization: str = Header(...)):
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

@router.post("/upload")
async def upload_recording(
    interview_id: str = Form(...),
    duration: Optional[float] = Form(None),
    video_file: Optional[UploadFile] = File(None),
    audio_file: Optional[UploadFile] = File(None),
    current_user: dict = Depends(get_current_user),
):
    """
    POST /api/recordings/upload

    Upload a completed recording file (video and/or audio) for an interview.
    Accepts multipart/form-data with fields: interview_id, duration, video_file, audio_file.
    """
    return await RecordingController.upload_recording(
        interview_id=interview_id,
        duration=duration,
        video_file=video_file,
        audio_file=audio_file,
        current_user=current_user,
    )


@router.get("/interview/{interview_id}")
async def get_interview_recordings(
    interview_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    GET /api/recordings/interview/{interview_id}

    List all recordings for the specified interview.
    Validates interview ownership before returning results.
    """
    return await RecordingController.get_interview_recordings(interview_id, current_user)


@router.get("/{recording_id}/url")
async def get_recording_url(
    recording_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    GET /api/recordings/{recording_id}/url

    Generate temporary presigned S3 GET URLs for the recording's media objects.
    """
    return await RecordingController.get_recording_url(recording_id, current_user)


@router.get("/{recording_id}")
async def get_recording(
    recording_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    GET /api/recordings/{recording_id}

    Retrieve metadata for a single recording.
    Does not return presigned media URLs — use /url for playback access.
    """
    return await RecordingController.get_recording(recording_id, current_user)


@router.delete("/{recording_id}")
async def delete_recording(
    recording_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    DELETE /api/recordings/{recording_id}

    Delete a recording's S3 objects and its MongoDB metadata.
    Only the recording owner may perform this operation.
    """
    return await RecordingController.delete_recording(recording_id, current_user)
