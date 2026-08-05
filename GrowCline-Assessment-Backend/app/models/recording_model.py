"""
Recording Model
Defines the video_recordings document structure and MongoDB document operations.

Storage provider: Google Drive
The actual media files live in Google Drive; this model stores metadata only.
Binary video data is NEVER stored in MongoDB.
"""

from datetime import datetime
from bson import ObjectId


class Recording:
    """
    Represents a video_recordings MongoDB document.

    A recording belongs to one interview and one authenticated user.
    The actual media files live in Google Drive; this model stores metadata only.
    """

    COLLECTION = "video_recordings"

    @staticmethod
    def create_recording(
        interview_id,
        user_id,
        drive_file_id=None,
        audio_drive_file_id=None,
        file_name=None,
        audio_file_name=None,
        mime_type=None,
        audio_mime_type=None,
        file_size=None,
        duration=None,
    ):
        """
        Build a new video_recordings document dict ready for MongoDB insertion.

        Args:
            interview_id:        str or ObjectId — the parent interview identifier.
            user_id:             str or ObjectId — the authenticated candidate identifier.
            drive_file_id:       str or None — Google Drive file ID for the video.
            audio_drive_file_id: str or None — Google Drive file ID for a separate audio track.
            file_name:           str or None — server-generated video filename (e.g., interview_<id>_<ts>.webm).
            audio_file_name:     str or None — server-generated audio filename.
            mime_type:           str or None — validated MIME type of the video (e.g., "video/webm").
            audio_mime_type:     str or None — validated MIME type of the audio.
            file_size:           int or None — video file size in bytes.
            duration:            float or None — recording duration in seconds.

        Returns:
            dict ready to pass to collection.insert_one().
        """
        now = datetime.utcnow()
        return {
            "_id": ObjectId(),

            "interviewId": ObjectId(interview_id),

            "userId": ObjectId(user_id),

            # Google Drive storage fields
            "storageProvider": "google_drive",

            "driveFileId": drive_file_id,

            "audioDriveFileId": audio_drive_file_id,

            "fileName": file_name,

            "audioFileName": audio_file_name,

            "mimeType": mime_type,

            "audioMimeType": audio_mime_type,

            "fileSize": file_size,

            "duration": duration,

            "status": "UPLOADED",

            "createdAt": now,

            "updatedAt": now,
        }

    @staticmethod
    def response(recording):
        """
        Serialize a video_recordings MongoDB document for an API response.

        Converts ObjectId values to strings and exposes only safe metadata fields.
        Does NOT include Google Drive file IDs or any internal storage keys —
        use the /url endpoint for playback access.

        Args:
            recording: dict — a raw MongoDB document from the video_recordings collection.

        Returns:
            dict safe for JSON serialisation.
        """
        # Safely convert datetime to ISO string if present
        created_at = recording.get("createdAt")
        updated_at = recording.get("updatedAt")

        return {
            "id": str(recording["_id"]),

            "interviewId": str(recording["interviewId"]),

            "userId": str(recording["userId"]),

            "storageProvider": recording.get("storageProvider", "google_drive"),

            "fileName": recording.get("fileName"),

            "mimeType": recording.get("mimeType"),

            "fileSize": recording.get("fileSize"),

            "hasVideo": recording.get("driveFileId") is not None,

            "hasAudio": recording.get("audioDriveFileId") is not None,

            "duration": recording.get("duration"),

            "status": recording.get("status", "UPLOADED"),

            "createdAt": created_at.isoformat() if hasattr(created_at, "isoformat") else created_at,

            "updatedAt": updated_at.isoformat() if hasattr(updated_at, "isoformat") else updated_at,
        }
