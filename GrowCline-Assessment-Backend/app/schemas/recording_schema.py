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
    Google Drive file IDs are intentionally excluded from responses;
    use the /url endpoint for playback access URLs.
    """

    id: str
    interviewId: str
    userId: str
    storageProvider: str
    fileName: Optional[str]
    mimeType: Optional[str]
    fileSize: Optional[int]
    hasVideo: bool
    hasAudio: bool
    duration: Optional[float]
    status: str
    createdAt: Optional[str]
    updatedAt: Optional[str]


class RecordingListResponse(BaseModel):
    """
    Response envelope for listing all recordings that belong to an interview.
    """

    interviewId: str
    recordings: list[RecordingResponse]
    count: int


class RecordingStreamUrlResponse(BaseModel):
    """
    Backend-proxied stream/download URLs for a recording.

    videoUrl points to GET /api/recordings/{id}/stream — the backend
    proxies the Google Drive content through JWT-authenticated endpoints.
    The Google Drive file ID is never exposed to the frontend.

    Both videoUrl and audioUrl may be null when the corresponding
    media track was not uploaded for that recording document.
    """

    recordingId: str
    videoUrl: Optional[str]
    audioUrl: Optional[str]


# Keep backward-compatible alias so any existing imports of
# RecordingAccessUrlResponse continue to resolve without errors.
RecordingAccessUrlResponse = RecordingStreamUrlResponse
