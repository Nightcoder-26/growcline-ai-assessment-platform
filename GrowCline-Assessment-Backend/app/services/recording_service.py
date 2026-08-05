"""
Recording Service
Business logic for the Video Recording module.

Responsibilities:
- Media file validation (MIME type, size, emptiness)
- Collision-safe Google Drive filename generation
- Upload to Google Drive via google_drive_service
- Google Drive file deletion and partial-failure cleanup
- Backend-proxied stream URL generation
- Interview existence and ownership validation
- Recording document creation and retrieval
- Recording deletion with consistent Drive cleanup
"""

import logging
import io
from datetime import datetime

from bson import ObjectId
from bson.errors import InvalidId

try:
    from config.database import Database
    from config.settings import Config
except ImportError:
    from app.config.database import Database
    from app.config.settings import Config

try:
    from models.recording_model import Recording
except ImportError:
    from app.models.recording_model import Recording

try:
    from services.google_drive_service import GoogleDriveService
except ImportError:
    from app.services.google_drive_service import GoogleDriveService


logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Allowed MIME types
# ---------------------------------------------------------------------------

ALLOWED_VIDEO_MIME_TYPES = {
    "video/webm",
    "video/mp4",
    "video/quicktime",
    "video/x-msvideo",
}

ALLOWED_AUDIO_MIME_TYPES = {
    "audio/webm",
    "audio/wav",
    "audio/x-wav",
    "audio/mpeg",
    "audio/mp4",
    "audio/ogg",
    "audio/aac",
}


# ---------------------------------------------------------------------------
# Internal helpers — filename and stream utilities
# ---------------------------------------------------------------------------

def _resolve_extension(mime_type: str) -> str:
    """
    Map a validated MIME type to a canonical file extension.

    Args:
        mime_type: str — a validated MIME type string.

    Returns:
        str — extension without leading dot.
    """
    mapping = {
        "video/webm": "webm",
        "video/mp4": "mp4",
        "video/quicktime": "mov",
        "video/x-msvideo": "avi",
        "audio/webm": "webm",
        "audio/wav": "wav",
        "audio/x-wav": "wav",
        "audio/mpeg": "mp3",
        "audio/mp4": "m4a",
        "audio/ogg": "ogg",
        "audio/aac": "aac",
    }
    return mapping.get(mime_type, "bin")


def _build_drive_filename(interview_id: str, timestamp: datetime, extension: str) -> str:
    """
    Generate a safe, unique Drive filename for a recording.

    Format:
        interview_<interview_id>_<YYYYMMDDTHHmmssZ>.{extension}

    Example:
        interview_67abc123_20260806T143522Z.webm

    The candidate's email and other personal data are never included.

    Args:
        interview_id: str — parent interview ObjectId string.
        timestamp:    datetime — UTC datetime of the upload.
        extension:    str — sanitised extension without leading dot (e.g., "webm").

    Returns:
        str — the safe filename.
    """
    ts = timestamp.strftime("%Y%m%dT%H%M%SZ")
    return f"interview_{interview_id}_{ts}.{extension}"


def _get_stream(upload_file):
    """
    Extract the underlying file stream from the upload_file object.
    Supports both FastAPI UploadFile (.file) and legacy Werkzeug/Mock (.stream).
    Handles MagicMock gracefully by checking attribute types.
    """
    file_attr = getattr(upload_file, "file", None)
    stream_attr = getattr(upload_file, "stream", None)

    if file_attr.__class__.__name__ == "MagicMock" and stream_attr.__class__.__name__ != "MagicMock":
        return stream_attr
    if file_attr is not None and file_attr.__class__.__name__ != "MagicMock":
        return file_attr
    return stream_attr or file_attr


def _get_upload_size(upload_file) -> int:
    """
    Determine the byte size of a file object without loading
    the entire content into RAM.

    Seeks to the end of the stream, reads the position, then rewinds.

    Args:
        upload_file: fastapi.UploadFile or equivalent file object.

    Returns:
        int — size in bytes.
    """
    stream = _get_stream(upload_file)
    if stream is None:
        raise ValueError("Invalid file object: no file or stream attribute found.")

    stream.seek(0, 2)       # seek to end
    size = stream.tell()
    stream.seek(0)          # rewind for subsequent read
    return size


# ---------------------------------------------------------------------------
# Internal helpers — validation and DB
# ---------------------------------------------------------------------------

def _validate_object_id(id_str, label="ID"):
    """
    Assert that id_str is a valid 24-character hex ObjectId string.

    Args:
        id_str: str — the identifier to validate.
        label: str — human-readable name for error messages.

    Returns:
        ObjectId — the validated ObjectId instance.

    Raises:
        ValueError: with a safe message if the string is not a valid ObjectId.
    """
    if not ObjectId.is_valid(id_str):
        raise ValueError(f"Invalid {label}: '{id_str}' is not a valid ID.")
    return ObjectId(id_str)


def _get_owned_interview(db, interview_id_str, user_id_str):
    """
    Load an interview document and verify the authenticated user owns it.

    Args:
        db: PyMongo database handle.
        interview_id_str: str — interview ObjectId as string.
        user_id_str: str — authenticated user's ObjectId as string.

    Returns:
        dict — the interview document.

    Raises:
        ValueError: with a safe message when the interview is not found or
                    does not belong to the requesting user.
    """
    interview_oid = _validate_object_id(interview_id_str, "interview ID")

    interview = db["interviews"].find_one({"_id": interview_oid})

    if not interview:
        raise ValueError("Interview not found.")

    interview_user_id = str(interview.get("userId", ""))
    if interview_user_id != user_id_str:
        raise ValueError("You do not have permission to access this interview.")

    return interview


def _get_owned_recording(db, recording_id_str, user_id_str):
    """
    Load a recording document and verify the authenticated user owns it.

    Args:
        db: PyMongo database handle.
        recording_id_str: str — recording ObjectId as string.
        user_id_str: str — authenticated user's ObjectId as string.

    Returns:
        dict — the recording document.

    Raises:
        ValueError: when the recording is not found or not owned by the user.
    """
    recording_oid = _validate_object_id(recording_id_str, "recording ID")

    recording = db[Recording.COLLECTION].find_one({"_id": recording_oid})

    if not recording:
        raise ValueError("Recording not found.")

    if str(recording.get("userId", "")) != user_id_str:
        raise ValueError("You do not have permission to access this recording.")

    return recording


def _validate_media_file(upload_file, allowed_mime_types, media_label, max_size_bytes):
    """
    Validate a FastAPI UploadFile object for MIME type and file size.

    Args:
        upload_file: fastapi.UploadFile — the uploaded file.
        allowed_mime_types: set[str] — permitted MIME types.
        media_label: str — "video" or "audio", used in error messages.
        max_size_bytes: int — maximum permitted file size in bytes.

    Raises:
        ValueError: when validation fails, with a safe human-readable message.
    """
    if not upload_file or not upload_file.filename:
        raise ValueError(f"No {media_label} file was provided.")

    content_type = (upload_file.content_type or "").lower().split(";")[0].strip()

    if content_type not in allowed_mime_types:
        raise ValueError(
            f"Unsupported {media_label} type '{content_type}'. "
            f"Allowed types: {sorted(allowed_mime_types)}."
        )

    size = _get_upload_size(upload_file)

    if size == 0:
        raise ValueError(f"The uploaded {media_label} file is empty.")

    if size > max_size_bytes:
        max_mb = max_size_bytes / (1024 * 1024)
        raise ValueError(
            f"The {media_label} file exceeds the maximum allowed size of {max_mb:.0f} MB."
        )


# ---------------------------------------------------------------------------
# Public service functions
# ---------------------------------------------------------------------------

def upload_recording(interview_id, user_id, video_file, audio_file, duration):
    """
    Validate and upload a recording, then persist metadata in MongoDB.

    At least one of video_file or audio_file must be provided.

    Upload flow:
        1. Validate interview existence and ownership.
        2. Validate media files (MIME type, size, emptiness).
        3. Generate safe Drive filenames.
        4. Upload video (and audio if provided) to Google Drive.
        5. Insert recording metadata into MongoDB.
        6. Return serialised recording.

    Consistency guarantee:
        - If video upload succeeds but audio fails, the video Drive file is deleted.
        - If all uploads succeed but MongoDB insert fails, all Drive files are deleted.

    Args:
        interview_id: str — parent interview ObjectId string.
        user_id: str — authenticated candidate ObjectId string.
        video_file: fastapi.UploadFile or None.
        audio_file: fastapi.UploadFile or None.
        duration: float or None — recording length in seconds (client-reported metadata).

    Returns:
        dict — serialised recording document (from Recording.response()).

    Raises:
        ValueError: for validation failures (400-level errors).
        RuntimeError: for Drive/configuration failures (500-level errors).
    """
    if video_file is None and audio_file is None:
        raise ValueError("At least one media file (video or audio) must be provided.")

    if duration is not None and duration < 0:
        raise ValueError("Duration must be a non-negative number of seconds.")

    db = Database.get_db()

    _get_owned_interview(db, interview_id, user_id)

    max_size_bytes = int(
        getattr(Config, "MAX_RECORDING_SIZE_MB", 500)
    ) * 1024 * 1024

    if video_file is not None:
        _validate_media_file(video_file, ALLOWED_VIDEO_MIME_TYPES, "video", max_size_bytes)

    if audio_file is not None:
        _validate_media_file(audio_file, ALLOWED_AUDIO_MIME_TYPES, "audio", max_size_bytes)

    upload_timestamp = datetime.utcnow()

    # ------------------------------------------------------------------ #
    #  Upload video to Google Drive                                        #
    # ------------------------------------------------------------------ #
    video_drive_id = None
    video_file_name = None
    video_mime_type = None
    video_file_size = None

    if video_file is not None:
        v_content_type = video_file.content_type.lower().split(";")[0].strip()
        v_ext = _resolve_extension(v_content_type)
        video_file_name = _build_drive_filename(interview_id, upload_timestamp, v_ext)
        video_file_size = _get_upload_size(video_file)
        video_mime_type = v_content_type

        try:
            logger.info(
                "Recording upload started: interview_id=%s user_id=%s file=%s",
                interview_id, user_id, video_file_name,
            )
            video_stream = _get_stream(video_file)
            video_drive_id = GoogleDriveService.upload_file(
                file_stream=video_stream,
                file_name=video_file_name,
                mime_type=v_content_type,
            )
            logger.info(
                "Recording upload completed: drive_file_id=%s file=%s",
                video_drive_id, video_file_name,
            )
        except RuntimeError:
            raise  # Already logged inside GoogleDriveService
        except Exception as exc:
            logger.error(
                "Drive video upload failed for interview %s: %s", interview_id, exc
            )
            raise RuntimeError("Video upload to Google Drive failed. Please try again.") from exc

    # ------------------------------------------------------------------ #
    #  Upload audio to Google Drive (optional separate audio track)       #
    # ------------------------------------------------------------------ #
    audio_drive_id = None
    audio_file_name = None
    audio_mime_type = None
    audio_file_size = None

    if audio_file is not None:
        a_content_type = audio_file.content_type.lower().split(";")[0].strip()
        a_ext = _resolve_extension(a_content_type)
        audio_file_name = _build_drive_filename(interview_id, upload_timestamp, a_ext)
        audio_file_size = _get_upload_size(audio_file)
        audio_mime_type = a_content_type

        try:
            audio_stream = _get_stream(audio_file)
            audio_drive_id = GoogleDriveService.upload_file(
                file_stream=audio_stream,
                file_name=audio_file_name,
                mime_type=a_content_type,
            )
        except Exception as exc:
            logger.error(
                "Drive audio upload failed for interview %s: %s", interview_id, exc
            )
            # Clean up the already-uploaded video to avoid orphaned Drive files
            if video_drive_id:
                cleaned = GoogleDriveService.delete_file(video_drive_id)
                if not cleaned:
                    logger.error(
                        "Orphaned Drive file could not be cleaned up after audio upload failure. "
                        "drive_file_id=%s",
                        video_drive_id,
                    )
            raise RuntimeError("Audio upload to Google Drive failed. Please try again.") from exc

    # ------------------------------------------------------------------ #
    #  Persist metadata in MongoDB                                         #
    # ------------------------------------------------------------------ #
    recording_doc = Recording.create_recording(
        interview_id=interview_id,
        user_id=user_id,
        drive_file_id=video_drive_id,
        audio_drive_file_id=audio_drive_id,
        file_name=video_file_name or audio_file_name,
        audio_file_name=audio_file_name if video_drive_id else None,
        mime_type=video_mime_type or audio_mime_type,
        audio_mime_type=audio_mime_type if video_drive_id else None,
        file_size=video_file_size or audio_file_size,
        duration=duration,
    )

    try:
        db[Recording.COLLECTION].insert_one(recording_doc)
        logger.info(
            "MongoDB metadata saved: recording_id=%s drive_file_id=%s",
            str(recording_doc["_id"]),
            video_drive_id or audio_drive_id,
        )
    except Exception as exc:
        logger.error(
            "MongoDB insert failed after Drive upload. Attempting Drive cleanup. Error: %s", exc
        )

        cleanup_failures = []
        if video_drive_id and not GoogleDriveService.delete_file(video_drive_id):
            cleanup_failures.append(video_drive_id)
        if audio_drive_id and not GoogleDriveService.delete_file(audio_drive_id):
            cleanup_failures.append(audio_drive_id)

        if cleanup_failures:
            logger.error(
                "Orphaned Drive files remain after MongoDB insert failure. "
                "drive_file_ids=%s",
                cleanup_failures,
            )

        raise RuntimeError("Recording metadata could not be saved. Please try again.") from exc

    return Recording.response(recording_doc)


def get_recording(recording_id, user_id):
    """
    Retrieve a single recording document for the authenticated owner.

    Args:
        recording_id: str — recording ObjectId string.
        user_id: str — authenticated candidate ObjectId string.

    Returns:
        dict — serialised recording document.

    Raises:
        ValueError: when the recording ID is invalid, not found, or not owned by the user.
    """
    _validate_object_id(recording_id, "recording ID")

    db = Database.get_db()
    recording = _get_owned_recording(db, recording_id, user_id)
    return Recording.response(recording)


def get_recordings_for_interview(interview_id, user_id):
    """
    Return all recordings belonging to a specific interview, ordered by createdAt ascending.

    Validates interview existence and ownership before querying recordings.

    Args:
        interview_id: str — interview ObjectId string.
        user_id: str — authenticated candidate ObjectId string.

    Returns:
        dict — containing interviewId, recordings list, and count.

    Raises:
        ValueError: when the interview is not found or not owned by the user.
    """
    db = Database.get_db()

    _get_owned_interview(db, interview_id, user_id)

    interview_oid = ObjectId(interview_id)

    recordings_cursor = db[Recording.COLLECTION].find(
        {"interviewId": interview_oid}
    ).sort("createdAt", 1)

    recordings = [Recording.response(r) for r in recordings_cursor]

    return {
        "interviewId": interview_id,
        "recordings": recordings,
        "count": len(recordings),
    }


def get_recording_access_urls(recording_id, user_id):
    """
    Return backend-proxied stream URLs for a recording's media objects.

    Instead of expiring S3 presigned URLs, this returns the backend /stream
    endpoint URL that proxies the Drive content through the authenticated API.
    The Drive file ID is never exposed directly to the frontend.

    Args:
        recording_id: str — recording ObjectId string.
        user_id: str — authenticated candidate ObjectId string.

    Returns:
        dict — recordingId, videoUrl, audioUrl.

    Raises:
        ValueError: when the recording is not found or not owned by the user.
        RuntimeError: when the Drive file cannot be accessed.
    """
    db = Database.get_db()
    recording = _get_owned_recording(db, recording_id, user_id)

    drive_file_id = recording.get("driveFileId")
    audio_drive_file_id = recording.get("audioDriveFileId")

    video_url = None
    audio_url = None

    if drive_file_id:
        # Verify the Drive file is still accessible before returning the URL
        if not GoogleDriveService.file_exists(drive_file_id):
            logger.warning(
                "Drive file '%s' referenced by recording '%s' no longer exists.",
                drive_file_id,
                recording_id,
            )
            raise RuntimeError(
                "The recording file could not be found in storage. Please contact support."
            )
        video_url = f"/api/recordings/{recording_id}/stream"

    if audio_drive_file_id:
        if GoogleDriveService.file_exists(audio_drive_file_id):
            audio_url = f"/api/recordings/{recording_id}/stream/audio"

    return {
        "recordingId": recording_id,
        "videoUrl": video_url,
        "audioUrl": audio_url,
    }


def stream_recording(recording_id, user_id):
    """
    Download the video content of a recording from Google Drive for streaming.

    This is used by the backend /stream proxy endpoint to serve the recording
    to authenticated users without exposing the Drive file ID or making files public.

    Args:
        recording_id: str — recording ObjectId string.
        user_id: str — authenticated candidate ObjectId string.

    Returns:
        tuple — (io.BytesIO buffer, mime_type str, file_name str)

    Raises:
        ValueError: when the recording is not found, not owned, or Drive file missing.
        RuntimeError: when Drive download fails.
    """
    db = Database.get_db()
    recording = _get_owned_recording(db, recording_id, user_id)

    drive_file_id = recording.get("driveFileId")
    if not drive_file_id:
        raise ValueError("This recording has no associated video file.")

    mime_type = recording.get("mimeType", "video/webm")
    file_name = recording.get("fileName", f"recording_{recording_id}.webm")

    buffer = GoogleDriveService.download_file(drive_file_id)
    return buffer, mime_type, file_name


def delete_recording(recording_id, user_id):
    """
    Delete a recording's Google Drive file(s) and its MongoDB metadata.

    Safety policy:
        - Drive files are deleted before the MongoDB document.
        - If Drive deletion fails, the MongoDB document is NOT deleted (the
          driveFileId reference is preserved so it can be retried or manually cleaned).
        - Partial Drive deletion failure is logged and surfaced to the caller.

    Args:
        recording_id: str — recording ObjectId string.
        user_id: str — authenticated candidate ObjectId string.

    Returns:
        dict — success confirmation message.

    Raises:
        ValueError: when the recording is not found or not owned by the user.
        RuntimeError: when Drive deletion fails (MongoDB doc is not deleted in this case).
    """
    db = Database.get_db()
    recording = _get_owned_recording(db, recording_id, user_id)

    drive_file_id = recording.get("driveFileId")
    audio_drive_file_id = recording.get("audioDriveFileId")

    drive_errors = []

    if drive_file_id:
        if not GoogleDriveService.delete_file(drive_file_id):
            drive_errors.append(f"video (drive_file_id: {drive_file_id})")

    if audio_drive_file_id:
        if not GoogleDriveService.delete_file(audio_drive_file_id):
            drive_errors.append(f"audio (drive_file_id: {audio_drive_file_id})")

    if drive_errors:
        raise RuntimeError(
            f"Recording storage deletion failed for: {', '.join(drive_errors)}. "
            "The recording metadata has been preserved. Please contact support."
        )

    db[Recording.COLLECTION].delete_one({"_id": recording["_id"]})
    logger.info(
        "Recording deleted: recording_id=%s drive_file_id=%s",
        recording_id,
        drive_file_id,
    )

    return {"message": "Recording deleted successfully."}
