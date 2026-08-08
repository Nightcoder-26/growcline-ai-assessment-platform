"""
Proctoring Model
Defines the proctoring_logs document structure and MongoDB document operations.
"""

from datetime import datetime
from bson import ObjectId


class ProctoringLog:
    """
    Represents a proctoring_logs MongoDB document.

    A proctoring log registers a candidate behavior monitoring event
    (e.g., TAB_SWITCH, MULTIPLE_FACES) associated with a specific interview.
    """

    COLLECTION = "proctoring_logs"

    @staticmethod
    def create_log(
        interview_id,
        user_id,
        event_type,
        severity,
        client_timestamp=None,
    ):
        """
        Build a new proctoring_logs document dict ready for MongoDB insertion.

        Args:
            interview_id: str or ObjectId — the parent interview identifier.
            user_id: str or ObjectId — the authenticated candidate identifier.
            event_type: str — the type of proctoring event (e.g. TAB_SWITCH).
            severity: str — the server-derived severity level (e.g. MEDIUM).
            client_timestamp: datetime or None — client-reported event time.

        Returns:
            dict ready to pass to collection.insert_one().
        """
        now = datetime.utcnow()
        # Map frontend event type aliases to the canonical schema names stored in MongoDB.
        # Only aliases that need renaming are listed here; canonical names pass through unchanged.
        event_map = {
            "NO_FACE":        "FACE_MISSING",   # frontend sends NO_FACE, store as FACE_MISSING
            "CAMERA_DISABLED": "FACE_MISSING",  # camera off = face missing
            "WINDOW_BLUR":    "TAB_SWITCH",     # window blur is a weaker form of tab-switch
        }
        mapped_event_type = event_map.get(event_type, event_type)

        # Canonical event types stored in MongoDB
        valid_types = [
            "FACE_MISSING",
            "MULTIPLE_FACES",
            "TAB_SWITCH",
            "FULLSCREEN_EXIT",
            "WINDOW_MINIMIZED",
            "BACKGROUND_VOICE",
            "MICROPHONE_DISABLED",
            "CAMERA_PERMISSION_DENIED",
            "MICROPHONE_PERMISSION_DENIED",
            "PROCTORING_STARTED",
            "PROCTORING_STOPPED",
        ]
        if mapped_event_type not in valid_types:
            # Unknown event type — default to TAB_SWITCH as a safe fallback
            mapped_event_type = "TAB_SWITCH"

        valid_severities = ["INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"]
        mapped_severity = str(severity).upper()
        if mapped_severity not in valid_severities:
            mapped_severity = "LOW"

        return {
            "_id": ObjectId(),
            "interviewId": ObjectId(interview_id),
            "userId": ObjectId(user_id),
            "eventType": mapped_event_type,
            "severity": mapped_severity,
            "timestamp": now,
            "clientTimestamp": client_timestamp,
            "createdAt": now,
        }

    @staticmethod
    def response(log):
        """
        Serialize a proctoring_logs MongoDB document for an API response.

        Args:
            log: dict — raw MongoDB document from the proctoring_logs collection.

        Returns:
            dict safe for JSON serialisation.
        """
        timestamp_val = log.get("timestamp")
        client_timestamp_val = log.get("clientTimestamp")

        return {
            "id": str(log["_id"]),
            "interviewId": str(log["interviewId"]),
            "userId": str(log["userId"]),
            "eventType": log["eventType"],
            "severity": log["severity"],
            "timestamp": timestamp_val.isoformat() if isinstance(timestamp_val, datetime) else timestamp_val,
            "clientTimestamp": client_timestamp_val.isoformat() if isinstance(client_timestamp_val, datetime) else client_timestamp_val,
        }
