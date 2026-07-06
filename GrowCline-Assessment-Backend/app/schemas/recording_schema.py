"""
Recording Schemas
Pydantic v2 response schemas for the Video Recording module.

These schemas are used for documentation and response validation only.
Multipart/form-data uploads are handled directly by FastAPI Form and File,
consistent with FastAPI request parameters.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class RecordingResponse(BaseModel):
    """
    Serialised representation of a single video_recordings document.

    Returned by upload, get-by-id, and list-by-interview endpoints.
    Media access URLs are intentionally excluded; use the /url endpoint.
    """

    id: str
    interviewId: str
    userId: str
    hasVideo: bool
    hasAudio: bool
    duration: Optional[float]
    createdAt: Optional[datetime]


class RecordingListResponse(BaseModel):
    """
    Response envelope for listing all recordings that belong to an interview.
    """

    interviewId: str
    recordings: list[RecordingResponse]
    count: int


class RecordingAccessUrlResponse(BaseModel):
    """
    Temporary presigned S3 access URLs for a recording.

    Both video_url and audio_url may be null when the corresponding
    media object was not uploaded for that recording document.
    URLs expire after expires_in seconds; do not cache them permanently.
    """

    recordingId: str
    videoUrl: Optional[str]
    audioUrl: Optional[str]
    expiresIn: int
