"""
Proctoring Service
Business logic for the Live Proctoring backend module.
"""

import logging
from datetime import datetime, timezone
from bson import ObjectId
from bson.errors import InvalidId

try:
    from config.database import Database
    from config.settings import Config
except ImportError:
    from app.config.database import Database
    from app.config.settings import Config

try:
    from models.proctoring_model import ProctoringLog
except ImportError:
    from app.models.proctoring_model import ProctoringLog


logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Allowed Event Types and Server-Side Severity Mapping
# ---------------------------------------------------------------------------

ALLOWED_EVENT_TYPES = {
    "PROCTORING_STARTED",
    "PROCTORING_STOPPED",
    "TAB_SWITCH",
    "WINDOW_BLUR",
    "WINDOW_MINIMIZED",
    "FULLSCREEN_EXIT",
    "MULTIPLE_FACES",
    "NO_FACE",
    "BACKGROUND_VOICE",
    "CAMERA_DISABLED",
    "MICROPHONE_DISABLED",
    "CAMERA_PERMISSION_DENIED",
    "MICROPHONE_PERMISSION_DENIED",
}

SEVERITY_MAPPING = {
    "PROCTORING_STARTED": "INFO",
    "PROCTORING_STOPPED": "INFO",
    "WINDOW_BLUR": "LOW",
    "TAB_SWITCH": "MEDIUM",
    "WINDOW_MINIMIZED": "MEDIUM",
    "FULLSCREEN_EXIT": "MEDIUM",
    "NO_FACE": "MEDIUM",
    "FACE_MISSING": "MEDIUM",
    "CAMERA_DISABLED": "HIGH",
    "MICROPHONE_DISABLED": "HIGH",
    "MULTIPLE_FACES": "HIGH",
    "BACKGROUND_VOICE": "HIGH",
    "CAMERA_PERMISSION_DENIED": "HIGH",
    "MICROPHONE_PERMISSION_DENIED": "HIGH",
}

# Per-event-type duplicate suppression window (seconds).
# Lifecycle events (INFO) use a short 2s window.
# Real violation events use a longer window so a new genuine occurrence
# (e.g., candidate leaves again 2 minutes later) is NOT suppressed.
DUPLICATE_COOLDOWN_SECONDS: dict = {
    "PROCTORING_STARTED":          2,
    "PROCTORING_STOPPED":          2,
    "WINDOW_BLUR":                  5,
    "TAB_SWITCH":                  30,
    "WINDOW_MINIMIZED":            30,
    "FULLSCREEN_EXIT":             30,
    "NO_FACE":                     30,
    "FACE_MISSING":                30,
    "CAMERA_DISABLED":             30,
    "MICROPHONE_DISABLED":         30,
    "MULTIPLE_FACES":              30,
    "BACKGROUND_VOICE":            30,
    "CAMERA_PERMISSION_DENIED":    30,
    "MICROPHONE_PERMISSION_DENIED": 30,
}

# ---------------------------------------------------------------------------
# Internal Helpers
# ---------------------------------------------------------------------------

def _validate_object_id(id_str: str, label: str = "ID") -> ObjectId:
    """
    Ensure the provided string is a valid 24-character hex ObjectId.
    """
    if not id_str or not ObjectId.is_valid(id_str):
        raise ValueError(f"Invalid {label}: '{id_str}' is not a valid ObjectId.")
    return ObjectId(id_str)


def _get_owned_interview(db, interview_id_str: str, user_id_str: str) -> dict:
    """
    Load an interview from the database and verify the candidate owns it.
    Also validates that the interview is not completed or cancelled.
    """
    interview_oid = _validate_object_id(interview_id_str, "interview ID")
    interview = db["interviews"].find_one({"_id": interview_oid})

    if not interview:
        raise ValueError("Interview not found.")

    # Validate ownership
    interview_user_id = str(interview.get("userId", ""))
    if interview_user_id != user_id_str:
        raise ValueError("You do not have permission to access this interview.")

    # Validate state (if status exists, reject completed or cancelled)
    status = interview.get("status")
    if status:
        normalized_status = str(status).upper()
        if normalized_status in {"COMPLETED", "CANCELLED", "SUBMITTED", "EVALUATED"}:
            raise ValueError(f"Cannot accept proctoring events for an interview that is {status}.")

    return interview


def _validate_client_timestamp(client_ts) -> None:
    """
    Validate that the client-reported timestamp is not too far in the future.
    """
    if not client_ts:
        return

    if isinstance(client_ts, str):
        try:
            client_ts = datetime.fromisoformat(client_ts.replace("Z", "+00:00"))
        except Exception:
            return

    if isinstance(client_ts, datetime):
        if client_ts.tzinfo is not None:
            client_ts = client_ts.astimezone(timezone.utc).replace(tzinfo=None)

        now = datetime.utcnow()
        time_diff = (client_ts - now).total_seconds()
        if time_diff > 300:
            raise ValueError("Client timestamp cannot be in the future.")


def _is_duplicate_event(db, interview_id: ObjectId, user_id: ObjectId, event_type: str, cooldown_seconds: int = None) -> bool:
    """
    Check if the same event type was logged within the per-event cooldown period.

    Uses DUPLICATE_COOLDOWN_SECONDS[event_type] by default, falling back to
    the value in Config (or 2 s) if no type-specific window is defined.
    """
    if cooldown_seconds is None:
        cooldown_seconds = DUPLICATE_COOLDOWN_SECONDS.get(
            event_type,
            int(getattr(Config, "PROCTORING_DUPLICATE_WINDOW_SECONDS", 2))
        )

    latest_event = db[ProctoringLog.COLLECTION].find_one(
        {
            "interviewId": interview_id,
            "userId": user_id,
            "eventType": event_type,
        },
        sort=[("timestamp", -1)]
    )

    if latest_event:
        latest_ts = latest_event.get("timestamp")
        if isinstance(latest_ts, datetime):
            elapsed = (datetime.utcnow() - latest_ts).total_seconds()
            if elapsed < cooldown_seconds:
                logger.debug(
                    "[ProctoringService] suppressing duplicate %s (last=%.1fs ago, cooldown=%ds)",
                    event_type, elapsed, cooldown_seconds
                )
                return True

    return False


# ---------------------------------------------------------------------------
# Public Service Functions
# ---------------------------------------------------------------------------

def create_proctoring_event(interview_id: str, user_id: str, event_type: str, client_timestamp: datetime = None) -> dict:
    """
    Validate, process, and persist a single live proctoring event.
    """
    db = Database.get_db()
    _get_owned_interview(db, interview_id, user_id)

    # Validate event type
    if event_type not in ALLOWED_EVENT_TYPES:
        raise ValueError(f"Unsupported event type '{event_type}'.")

    # Validate client timestamp
    if client_timestamp:
        _validate_client_timestamp(client_timestamp)

    interview_oid = ObjectId(interview_id)
    user_oid = ObjectId(user_id)

    # Duplicate suppression check (uses per-event cooldown from DUPLICATE_COOLDOWN_SECONDS)
    if _is_duplicate_event(db, interview_oid, user_oid, event_type):
        # Fetch and return the latest matching duplicate instead of raising an error
        latest = db[ProctoringLog.COLLECTION].find_one(
            {
                "interviewId": interview_oid,
                "userId": user_oid,
                "eventType": event_type,
            },
            sort=[("timestamp", -1)]
        )
        return ProctoringLog.response(latest)

    # Derive severity
    severity = SEVERITY_MAPPING.get(event_type, "MEDIUM")

    # Create document
    log_doc = ProctoringLog.create_log(
        interview_id=interview_oid,
        user_id=user_oid,
        event_type=event_type,
        severity=severity,
        client_timestamp=client_timestamp,
    )

    db[ProctoringLog.COLLECTION].insert_one(log_doc)
    return ProctoringLog.response(log_doc)


def create_proctoring_events_batch(interview_id: str, user_id: str, events: list) -> list:
    """
    Validate and batch insert multiple proctoring events.
    """
    max_batch_size = int(getattr(Config, "PROCTORING_BATCH_MAX_SIZE", 50))
    if not events:
        raise ValueError("Batch cannot be empty.")
    if len(events) > max_batch_size:
        raise ValueError(f"Batch size exceeds the maximum allowed limit of {max_batch_size} events.")

    db = Database.get_db()
    _get_owned_interview(db, interview_id, user_id)

    interview_oid = ObjectId(interview_id)
    user_oid = ObjectId(user_id)

    validated_docs = []
    
    # Track the last timestamp we inserted or validated for duplicate checks within this batch
    last_processed_timestamps: dict = {}

    for item in events:
        event_type = item.get("event_type")
        client_ts  = item.get("client_timestamp")

        # Validate event type
        if event_type not in ALLOWED_EVENT_TYPES:
            raise ValueError(f"Unsupported event type '{event_type}' in batch.")

        # Validate client timestamp
        if client_ts:
            _validate_client_timestamp(client_ts)

        # Per-event-type cooldown
        cooldown = DUPLICATE_COOLDOWN_SECONDS.get(
            event_type,
            int(getattr(Config, "PROCTORING_DUPLICATE_WINDOW_SECONDS", 2))
        )

        # Inner-batch duplicate suppression
        now = datetime.utcnow()
        if event_type in last_processed_timestamps:
            elapsed = (now - last_processed_timestamps[event_type]).total_seconds()
            if elapsed < cooldown:
                continue
        else:
            # Check against existing database records
            if _is_duplicate_event(db, interview_oid, user_oid, event_type):
                continue

        last_processed_timestamps[event_type] = now
        severity = SEVERITY_MAPPING.get(event_type, "MEDIUM")

        log_doc = ProctoringLog.create_log(
            interview_id=interview_oid,
            user_id=user_oid,
            event_type=event_type,
            severity=severity,
            client_timestamp=client_ts,
        )
        validated_docs.append(log_doc)

    if validated_docs:
        db[ProctoringLog.COLLECTION].insert_many(validated_docs)

    return [ProctoringLog.response(doc) for doc in validated_docs]


def get_proctoring_events(interview_id: str, user_id: str, limit: int = 50, skip: int = 0) -> dict:
    """
    Retrieve paged proctoring events for a specific interview.
    """
    # Validate pagination bounds
    if limit < 1 or limit > 100:
        raise ValueError("Limit must be between 1 and 100.")
    if skip < 0:
        raise ValueError("Skip must be a non-negative number.")

    db = Database.get_db()
    _get_owned_interview(db, interview_id, user_id)

    interview_oid = ObjectId(interview_id)

    cursor = db[ProctoringLog.COLLECTION].find(
        {"interviewId": interview_oid}
    ).sort("timestamp", 1).skip(skip).limit(limit)

    events_list = [ProctoringLog.response(doc) for doc in cursor]

    return {
        "interviewId": interview_id,
        "events": events_list,
        "count": len(events_list),
    }


def get_proctoring_summary(interview_id: str, user_id: str) -> dict:
    """
    Generate an aggregated summary of all proctoring events recorded for an interview.
    """
    db = Database.get_db()
    _get_owned_interview(db, interview_id, user_id)

    interview_oid = ObjectId(interview_id)

    # Aggregate total events, type counts, severity counts, and first/last timestamps
    pipeline = [
        {"$match": {"interviewId": interview_oid}},
        {"$facet": {
            "stats": [
                {"$group": {
                    "_id": None,
                    "totalEvents": {"$sum": 1},
                    "firstEventAt": {"$min": "$timestamp"},
                    "lastEventAt": {"$max": "$timestamp"}
                }}
            ],
            "byType": [
                {"$group": {
                    "_id": "$eventType",
                    "count": {"$sum": 1}
                }}
            ],
            "bySeverity": [
                {"$group": {
                    "_id": "$severity",
                    "count": {"$sum": 1}
                }}
            ]
        }}
    ]

    agg_result = list(db[ProctoringLog.COLLECTION].aggregate(pipeline))
    result = agg_result[0] if agg_result else {}

    # Parse aggregate results
    stats_list = result.get("stats", [])
    stats = stats_list[0] if stats_list else {}

    total_events = stats.get("totalEvents", 0)
    first_event_at = stats.get("firstEventAt", None)
    last_event_at = stats.get("lastEventAt", None)

    event_counts = {item["_id"]: item["count"] for item in result.get("byType", []) if item.get("_id")}
    severity_counts = {item["_id"]: item["count"] for item in result.get("bySeverity", []) if item.get("_id")}

    # Normalize response maps to guarantee default enums exist
    for ev_type in ALLOWED_EVENT_TYPES:
        if ev_type not in event_counts:
            event_counts[ev_type] = 0

    for sev in ["INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"]:
        if sev not in severity_counts:
            severity_counts[sev] = 0

    return {
        "interviewId": interview_id,
        "totalEvents": total_events,
        "eventCounts": event_counts,
        "severityCounts": severity_counts,
        "firstEventAt": first_event_at,
        "lastEventAt": last_event_at,
    }
