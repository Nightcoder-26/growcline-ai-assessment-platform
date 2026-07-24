"""
Recording Routes
FastAPI APIRouter for the Video Recording module.
"""

import logging
from typing import Optional
from datetime import datetime
from bson import ObjectId

from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException, Header
from fastapi.responses import JSONResponse

from app.config.database import Database
from app.controllers.recording_controller import RecordingController
from app.utils.jwt_utils import decode_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/recordings", tags=["Recordings"])


# ---------------------------------------------------------------------------
# JWT authentication dependency
# ---------------------------------------------------------------------------

async def get_current_user(authorization: Optional[str] = Header(None)):
    """
    Validate a Bearer JWT from the Authorization header.
    If no header is provided or token is invalid, automatically resolves to the
    default candidate user to enable guest recording uploads.
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
