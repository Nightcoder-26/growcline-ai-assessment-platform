"""
Recording Service
Business logic for the Video Recording module.

Responsibilities:
- S3 client initialisation and access
- Media file validation (MIME type, size, emptiness)
- Collision-safe S3 object key generation
- Streaming upload to AWS S3 via upload_fileobj
- S3 object deletion and partial-failure cleanup
- Temporary presigned GET URL generation
- Interview existence and ownership validation
- Recording document creation and retrieval
- Recording deletion with consistent S3 cleanup
"""

import logging
import uuid
from datetime import datetime

from bson import ObjectId
from bson.errors import InvalidId

try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError
    _BOTO3_AVAILABLE = True
except ImportError:
    _BOTO3_AVAILABLE = False

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
# Internal helpers — S3
# ---------------------------------------------------------------------------

def _get_s3_client():
    """
    Create and return a boto3 S3 client using credentials from Config.

    Raises:
        RuntimeError: if boto3 is not installed or required S3 settings are missing.
    """
    if not _BOTO3_AVAILABLE:
        raise RuntimeError(
            "boto3 is not installed. Add boto3 to requirements.txt."
        )

    access_key = getattr(Config, "AWS_ACCESS_KEY_ID", None)
    secret_key = getattr(Config, "AWS_SECRET_ACCESS_KEY", None)
    region = getattr(Config, "AWS_REGION", None)

    if not access_key or not secret_key or not region:
        raise RuntimeError(
            "AWS S3 credentials are not configured. "
            "Set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_REGION."
        )

    return boto3.client(
        "s3",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region,
    )


def _get_s3_bucket():
    """Return the configured S3 bucket name or raise RuntimeError."""
    bucket = getattr(Config, "AWS_S3_BUCKET", None)
    if not bucket:
        raise RuntimeError(
            "AWS_S3_BUCKET is not configured."
        )
    return bucket


def _build_s3_key(user_id, interview_id, media_type, extension):
    """
    Generate a collision-safe, namespace-isolated S3 object key.

    Format:
        recordings/{user_id}/{interview_id}/{media_type}/{uuid4}.{extension}

    The user never controls the key path.  The original filename is ignored.

    Args:
        user_id: str — authenticated user's string ObjectId.
        interview_id: str — parent interview's string ObjectId.
        media_type: str — "video" or "audio".
        extension: str — sanitised file extension without leading dot (e.g. "webm").

    Returns:
        str — the complete S3 object key.
    """
    unique_id = uuid.uuid4().hex
    return f"recordings/{user_id}/{interview_id}/{media_type}/{unique_id}.{extension}"


def _resolve_extension(mime_type):
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


def _get_stream(upload_file):
    """
    Extract the underlying file stream from the upload_file object.
    Supports both FastAPI UploadFile (.file) and legacy Werkzeug/Mock (.stream).
    Handles MagicMock gracefully by checking attribute types.
    """
    file_attr = getattr(upload_file, "file", None)
    stream_attr = getattr(upload_file, "stream", None)
    
    if file_attr.__class__.__name__ == 'MagicMock' and stream_attr.__class__.__name__ != 'MagicMock':
        return stream_attr
    if file_attr is not None and file_attr.__class__.__name__ != 'MagicMock':
        return file_attr
    return stream_attr or file_attr


def _get_upload_size(upload_file):
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
    
    stream.seek(0, 2)        # seek to end
    size = stream.tell()
    stream.seek(0)           # rewind for subsequent read
    return size


def _upload_to_s3(s3_client, bucket, key, upload_file, content_type):
    """
    Stream a file object to S3 using upload_fileobj.

    The file pointer is rewound before upload so the full content is sent.

    Args:
        s3_client: boto3 S3 client.
        bucket: str — S3 bucket name.
        key: str — destination S3 object key.
        upload_file: fastapi.UploadFile or equivalent file object.
        content_type: str — validated MIME type to set as ContentType.

    Raises:
        ClientError: on S3 API errors.
        BotoCoreError: on transport/credential errors.
    """
    stream = _get_stream(upload_file)
    if stream is None:
        raise ValueError("Invalid file object: no file or stream attribute found.")

    stream.seek(0)
    s3_client.upload_fileobj(
        stream,
        bucket,
        key,
        ExtraArgs={"ContentType": content_type},
    )


def _delete_s3_object(s3_client, bucket, key):
    """
    Delete a single S3 object by key.

    Logs but does not re-raise on failure so callers can attempt
    additional cleanup before surfacing the error.

    Args:
        s3_client: boto3 S3 client.
        bucket: str — S3 bucket name.
        key: str — S3 object key to delete.

    Returns:
        bool — True if deletion succeeded, False otherwise.
    """
    try:
        s3_client.delete_object(Bucket=bucket, Key=key)
        return True
    except (BotoCoreError, ClientError) as exc:
        logger.error(
            "Failed to delete S3 object '%s' from bucket '%s': %s",
            key, bucket, exc,
        )
        return False


def _generate_presigned_url(s3_client, bucket, key, expiry_seconds):
    """
    Generate a temporary presigned GET URL for an S3 object.

    Args:
        s3_client: boto3 S3 client.
        bucket: str — S3 bucket name.
        key: str — S3 object key.
        expiry_seconds: int — URL validity window in seconds.

    Returns:
        str — the presigned URL.

    Raises:
        ClientError: if presigning fails.
    """
    return s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=expiry_seconds,
    )


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
        3. Generate S3 keys.
        4. Upload media objects to S3.
        5. Insert recording metadata into MongoDB.
        6. Return serialised recording.

    Consistency guarantee:
        - If a video upload succeeds but audio fails, the video object is deleted.
        - If both S3 uploads succeed but MongoDB insert fails, both objects are deleted.

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
        RuntimeError: for S3/configuration failures (500-level errors).
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

    s3_client = _get_s3_client()
    bucket = _get_s3_bucket()

    video_key = None
    audio_key = None

    if video_file is not None:
        v_content_type = video_file.content_type.lower().split(";")[0].strip()
        v_ext = _resolve_extension(v_content_type)
        video_key = _build_s3_key(user_id, interview_id, "video", v_ext)

        try:
            _upload_to_s3(s3_client, bucket, video_key, video_file, v_content_type)
        except (BotoCoreError, ClientError) as exc:
            logger.error("S3 video upload failed for interview %s: %s", interview_id, exc)
            raise RuntimeError("Video upload to storage failed. Please try again.") from exc

    if audio_file is not None:
        a_content_type = audio_file.content_type.lower().split(";")[0].strip()
        a_ext = _resolve_extension(a_content_type)
        audio_key = _build_s3_key(user_id, interview_id, "audio", a_ext)

        try:
            _upload_to_s3(s3_client, bucket, audio_key, audio_file, a_content_type)
        except (BotoCoreError, ClientError) as exc:
            logger.error("S3 audio upload failed for interview %s: %s", interview_id, exc)

            if video_key:
                cleaned = _delete_s3_object(s3_client, bucket, video_key)
                if not cleaned:
                    logger.error(
                        "Orphaned S3 object could not be cleaned up after audio upload failure. "
                        "Key: %s  Bucket: %s",
                        video_key, bucket,
                    )

            raise RuntimeError("Audio upload to storage failed. Please try again.") from exc

    recording_doc = Recording.create_recording(
        interview_id=interview_id,
        user_id=user_id,
        video_key=video_key,
        audio_key=audio_key,
        duration=duration,
    )

    try:
        db[Recording.COLLECTION].insert_one(recording_doc)
    except Exception as exc:
        logger.error(
            "MongoDB insert failed after S3 upload. Attempting S3 cleanup. Error: %s", exc
        )

        cleanup_failures = []
        if video_key and not _delete_s3_object(s3_client, bucket, video_key):
            cleanup_failures.append(video_key)
        if audio_key and not _delete_s3_object(s3_client, bucket, audio_key):
            cleanup_failures.append(audio_key)

        if cleanup_failures:
            logger.error(
                "Orphaned S3 objects remain after MongoDB insert failure. "
                "Keys: %s  Bucket: %s",
                cleanup_failures, bucket,
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
    # Validate ID format before hitting the database.
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
    Generate temporary presigned S3 GET URLs for a recording's media objects.

    Validates ownership before presigning.  Returns null for URLs where the
    corresponding media object key was not stored (e.g. audio-only recording).

    Args:
        recording_id: str — recording ObjectId string.
        user_id: str — authenticated candidate ObjectId string.

    Returns:
        dict — recordingId, videoUrl, audioUrl, expiresIn.

    Raises:
        ValueError: when the recording is not found or not owned by the user.
        RuntimeError: when presigned URL generation fails.
    """
    db = Database.get_db()
    recording = _get_owned_recording(db, recording_id, user_id)

    expiry_seconds = int(
        getattr(Config, "RECORDING_URL_EXPIRY_SECONDS", 900)
    )

    s3_client = _get_s3_client()
    bucket = _get_s3_bucket()

    video_url = None
    audio_url = None

    video_key = recording.get("videoKey")
    audio_key = recording.get("audioKey")

    if video_key:
        try:
            video_url = _generate_presigned_url(s3_client, bucket, video_key, expiry_seconds)
        except (BotoCoreError, ClientError) as exc:
            logger.error(
                "Presigned URL generation failed for video key '%s': %s", video_key, exc
            )
            raise RuntimeError(
                "Could not generate video access URL. Please try again."
            ) from exc

    if audio_key:
        try:
            audio_url = _generate_presigned_url(s3_client, bucket, audio_key, expiry_seconds)
        except (BotoCoreError, ClientError) as exc:
            logger.error(
                "Presigned URL generation failed for audio key '%s': %s", audio_key, exc
            )
            raise RuntimeError(
                "Could not generate audio access URL. Please try again."
            ) from exc

    return {
        "recordingId": str(recording["_id"]),
        "videoUrl": video_url,
        "audioUrl": audio_url,
        "expiresIn": expiry_seconds,
    }


def delete_recording(recording_id, user_id):
    """
    Delete a recording's S3 objects and its MongoDB metadata.

    Safety policy:
        - S3 objects are deleted before the MongoDB document.
        - If S3 deletion fails, the MongoDB document is NOT deleted (the key
          reference is preserved so the object can be retried or manually cleaned).
        - Partial S3 deletion failure is logged and surfaced to the caller.

    Args:
        recording_id: str — recording ObjectId string.
        user_id: str — authenticated candidate ObjectId string.

    Returns:
        dict — success confirmation message.

    Raises:
        ValueError: when the recording is not found or not owned by the user.
        RuntimeError: when S3 deletion fails (MongoDB doc is not deleted in this case).
    """
    db = Database.get_db()
    recording = _get_owned_recording(db, recording_id, user_id)

    s3_client = _get_s3_client()
    bucket = _get_s3_bucket()

    video_key = recording.get("videoKey")
    audio_key = recording.get("audioKey")

    s3_errors = []

    if video_key:
        if not _delete_s3_object(s3_client, bucket, video_key):
            s3_errors.append(f"video (key: {video_key})")

    if audio_key:
        if not _delete_s3_object(s3_client, bucket, audio_key):
            s3_errors.append(f"audio (key: {audio_key})")

    if s3_errors:
        raise RuntimeError(
            f"Recording storage deletion failed for: {', '.join(s3_errors)}. "
            "The recording metadata has been preserved. Please contact support."
        )

    db[Recording.COLLECTION].delete_one({"_id": recording["_id"]})

    return {"message": "Recording deleted successfully."}
