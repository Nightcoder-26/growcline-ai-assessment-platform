"""
Recording Model
Defines the video_recordings document structure and MongoDB document operations.
"""

from datetime import datetime
from bson import ObjectId


class Recording:
    """
    Represents a video_recordings MongoDB document.

    A recording belongs to one interview and one authenticated user.
    The actual media objects live in AWS S3; this model stores metadata only.
    """

    COLLECTION = "video_recordings"

    @staticmethod
    def create_recording(
        interview_id,
        user_id,
        video_key=None,
        audio_key=None,
        video_url=None,
        audio_url=None,
        duration=None,
    ):
        """
        Build a new video_recordings document dict ready for MongoDB insertion.

        Args:
            interview_id: str or ObjectId — the parent interview identifier.
            user_id: str or ObjectId — the authenticated candidate identifier.
            video_key: str or None — S3 object key for the video file.
            audio_key: str or None — S3 object key for the audio file.
            video_url: str or None — stable S3 URI reference (not a presigned URL).
            audio_url: str or None — stable S3 URI reference (not a presigned URL).
            duration: float or None — recording duration in seconds.

        Returns:
            dict ready to pass to collection.insert_one().
        """
        return {
            "_id": ObjectId(),

            "interviewId": ObjectId(interview_id),

            "userId": ObjectId(user_id),

            "videoKey": video_key,

            "audioKey": audio_key,

            "videoUrl": video_url,

            "audioUrl": audio_url,

            "duration": duration,

            "createdAt": datetime.utcnow(),
        }

    @staticmethod
    def response(recording):
        """
        Serialize a video_recordings MongoDB document for an API response.

        Converts ObjectId values to strings and exposes only safe metadata fields.
        Does NOT include S3 keys or presigned URLs — use the /url endpoint for access.

        Args:
            recording: dict — a raw MongoDB document from the video_recordings collection.

        Returns:
            dict safe for JSON serialisation.
        """
        return {
            "id": str(recording["_id"]),

            "interviewId": str(recording["interviewId"]),

            "userId": str(recording["userId"]),

            "hasVideo": recording.get("videoKey") is not None,

            "hasAudio": recording.get("audioKey") is not None,

            "duration": recording.get("duration"),

            "videoUrl": recording.get("videoUrl"),

            "audioUrl": recording.get("audioUrl"),

            "createdAt": recording.get("createdAt").isoformat() if recording.get("createdAt") else None,
        }
