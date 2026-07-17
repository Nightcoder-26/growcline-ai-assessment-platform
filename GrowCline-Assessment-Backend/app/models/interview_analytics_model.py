"""
Interview Analytics Model
Defines the interview_analytics document structure and all MongoDB document operations.
"""

from datetime import datetime
from bson import ObjectId


class InterviewAnalytics:
    """
    Represents an interview_analytics MongoDB document.

    An analytics report is derived from interview session data, video recordings,
    proctoring logs, and cheating detection results.  It provides a single
    consolidated view for reviewers.
    """

    COLLECTION = "interview_analytics"

    # ---------------------------------------------------------------------------
    # Document builders
    # ---------------------------------------------------------------------------

    @staticmethod
    def create_analytics(
        interview_id,
        user_id,
        duration_seconds: int,
        video_uploaded: bool,
        total_events: int,
        risk_score: float,
        risk_level: str,
        tab_switches: int,
        multiple_faces: int,
        background_voice: int,
        camera_disabled: int,
        microphone_disabled: int,
        fullscreen_exit: int,
        overall_status: str,
    ) -> dict:
        """
        Build a new interview_analytics document ready for MongoDB insertion.

        Args:
            interview_id: str or ObjectId — parent interview identifier.
            user_id: str or ObjectId — candidate identifier.
            duration_seconds: int — interview duration in seconds.
            video_uploaded: bool — whether a video recording was uploaded.
            total_events: int — total proctoring event count.
            risk_score: float — risk score (0–100) from cheating_reports.
            risk_level: str — LOW | MEDIUM | HIGH | CRITICAL.
            tab_switches: int — TAB_SWITCH event count.
            multiple_faces: int — MULTIPLE_FACES event count.
            background_voice: int — BACKGROUND_VOICE event count.
            camera_disabled: int — CAMERA_DISABLED event count.
            microphone_disabled: int — MICROPHONE_DISABLED event count.
            fullscreen_exit: int — FULLSCREEN_EXIT event count.
            overall_status: str — PASSED | REVIEW_REQUIRED | MANUAL_REVIEW | FLAGGED.

        Returns:
            dict ready for collection.insert_one().
        """
        now = datetime.utcnow()
        return {
            "_id": ObjectId(),
            "interviewId": ObjectId(interview_id),
            "userId": ObjectId(user_id),
            "durationSeconds": int(duration_seconds),
            "videoUploaded": bool(video_uploaded),
            "totalEvents": int(total_events),
            "riskScore": float(risk_score),
            "riskLevel": str(risk_level),
            "tabSwitches": int(tab_switches),
            "multipleFaces": int(multiple_faces),
            "backgroundVoice": int(background_voice),
            "cameraDisabled": int(camera_disabled),
            "microphoneDisabled": int(microphone_disabled),
            "fullscreenExit": int(fullscreen_exit),
            "overallStatus": str(overall_status),
            "generatedAt": now,
            "updatedAt": now,
        }

    # ---------------------------------------------------------------------------
    # Response serialization
    # ---------------------------------------------------------------------------

    @staticmethod
    def response(doc: dict) -> dict:
        """
        Serialize an interview_analytics MongoDB document for an API response.

        Converts ObjectId and datetime values to JSON-safe strings.

        Args:
            doc: dict — raw MongoDB document from interview_analytics collection.

        Returns:
            dict safe for JSON serialization.
        """
        generated_at = doc.get("generatedAt")
        updated_at = doc.get("updatedAt")

        return {
            "id": str(doc["_id"]),
            "interviewId": str(doc["interviewId"]),
            "userId": str(doc["userId"]),
            "durationSeconds": doc.get("durationSeconds", 0),
            "videoUploaded": doc.get("videoUploaded", False),
            "totalEvents": doc.get("totalEvents", 0),
            "riskScore": doc.get("riskScore", 0.0),
            "riskLevel": doc.get("riskLevel", "LOW"),
            "tabSwitches": doc.get("tabSwitches", 0),
            "multipleFaces": doc.get("multipleFaces", 0),
            "backgroundVoice": doc.get("backgroundVoice", 0),
            "cameraDisabled": doc.get("cameraDisabled", 0),
            "microphoneDisabled": doc.get("microphoneDisabled", 0),
            "fullscreenExit": doc.get("fullscreenExit", 0),
            "overallStatus": doc.get("overallStatus", "PASSED"),
            "generatedAt": generated_at.isoformat() if isinstance(generated_at, datetime) else generated_at,
            "updatedAt": updated_at.isoformat() if isinstance(updated_at, datetime) else updated_at,
        }

    # ---------------------------------------------------------------------------
    # MongoDB helper queries (thin wrappers — no business logic)
    # ---------------------------------------------------------------------------

    @staticmethod
    def find_by_interview(db, interview_oid: ObjectId) -> dict | None:
        """Return the analytics document for an interview, or None."""
        return db[InterviewAnalytics.COLLECTION].find_one({"interviewId": interview_oid})

    @staticmethod
    def find_by_user(db, user_oid: ObjectId) -> list:
        """Return all analytics documents for a user, newest first."""
        cursor = db[InterviewAnalytics.COLLECTION].find(
            {"userId": user_oid}
        ).sort("generatedAt", -1)
        return list(cursor)

    @staticmethod
    def delete_by_interview(db, interview_oid: ObjectId) -> int:
        """Delete analytics for an interview. Returns the number of documents deleted."""
        result = db[InterviewAnalytics.COLLECTION].delete_one({"interviewId": interview_oid})
        return result.deleted_count

    @staticmethod
    def upsert(db, interview_oid: ObjectId, update_fields: dict) -> None:
        """
        Atomically update an existing analytics document or insert a new one.
        Preserves the original generatedAt on insert.

        Args:
            db: active MongoDB database handle.
            interview_oid: ObjectId of the parent interview.
            update_fields: dict of fields to set on the document.
        """
        now = datetime.utcnow()
        db[InterviewAnalytics.COLLECTION].update_one(
            {"interviewId": interview_oid},
            {
                "$set": update_fields,
                "$setOnInsert": {
                    "_id": ObjectId(),
                    "generatedAt": now,
                },
            },
            upsert=True,
        )
