"""
Cheating Detection Service
Core business logic for calculating cheating risk scores and generating reports.
"""

import logging
from datetime import datetime
from bson import ObjectId
from bson.errors import InvalidId

try:
    from config.database import Database
except ImportError:
    from app.config.database import Database

try:
    from models.cheating_report_model import CheatingReport
except ImportError:
    from app.models.cheating_report_model import CheatingReport


logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Centralized Heuristic Scoring Rules and Caps
# ---------------------------------------------------------------------------

EVENT_WEIGHTS = {
    "PROCTORING_STARTED": 0,
    "PROCTORING_STOPPED": 0,
    "WINDOW_BLUR": 1,
    "TAB_SWITCH": 3,
    "WINDOW_MINIMIZED": 3,
    "FULLSCREEN_EXIT": 3,
    "NO_FACE": 3,
    "BACKGROUND_VOICE": 5,
    "CAMERA_DISABLED": 5,
    "MICROPHONE_DISABLED": 5,
    "CAMERA_PERMISSION_DENIED": 5,
    "MICROPHONE_PERMISSION_DENIED": 5,
    "MULTIPLE_FACES": 7,
}

EVENT_CAPS = {
    "WINDOW_BLUR": 5,
    "TAB_SWITCH": 10,
    "WINDOW_MINIMIZED": 5,
    "FULLSCREEN_EXIT": 5,
    "NO_FACE": 10,
    "BACKGROUND_VOICE": 10,
    "CAMERA_DISABLED": 3,
    "MICROPHONE_DISABLED": 3,
    "MULTIPLE_FACES": 5,
    "CAMERA_PERMISSION_DENIED": 2,
    "MICROPHONE_PERMISSION_DENIED": 2,
}

MAX_RAW_SCORE = 100.0


# ---------------------------------------------------------------------------
# Internal Helpers
# ---------------------------------------------------------------------------

def _validate_object_id(id_str: str, label: str = "ID") -> ObjectId:
    """Ensure the provided string is a valid 24-character hex ObjectId."""
    if not id_str or not ObjectId.is_valid(id_str):
        raise ValueError(f"Invalid {label}: '{id_str}' is not a valid ObjectId.")
    return ObjectId(id_str)


def _validate_admin_role(user_role: str) -> None:
    """Ensure the user has admin role permissions."""
    if user_role != "admin":
        raise ValueError("Access denied. Only administrators can access cheating reports.")


# ---------------------------------------------------------------------------
# Pure Scoring Engine (Deterministic, Transparent, and Explainable)
# ---------------------------------------------------------------------------

def calculate_risk_score(event_counts: dict) -> tuple:
    """
    Calculate risk score, risk level, and event contributions.
    This function is pure and does not touch MongoDB, facilitating testability.

    Args:
        event_counts: dict mapping eventType (str) -> count (int).

    Returns:
        tuple containing:
            - risk_score: float (0 to 100)
            - risk_level: str (LOW, MEDIUM, HIGH, CRITICAL)
            - contributions: dict details for scored events
            - suspicious_events: int total count of positive-weighted events
    """
    raw_score = 0.0
    contributions = {}
    suspicious_events = 0

    for event_type, count in event_counts.items():
        # Prevent negative counts (precautionary)
        count = max(0, int(count))

        weight = EVENT_WEIGHTS.get(event_type, 0)
        cap = EVENT_CAPS.get(event_type, 0)

        # Track suspicious events based on actual count of non-zero weight events
        if weight > 0:
            suspicious_events += count

            # Calculate capped contribution
            effective_count = min(count, cap) if cap > 0 else count
            contribution = effective_count * weight
            raw_score += contribution

            contributions[event_type] = {
                "count": count,
                "effectiveCount": effective_count,
                "weight": weight,
                "contribution": contribution
            }

    # Normalize risk score
    risk_score = min(round((raw_score / MAX_RAW_SCORE) * 100, 2), 100.0)
    # Clamp score floor
    risk_score = max(0.0, risk_score)

    # Centralized thresholds mapping to risk levels
    if risk_score < 20.0:
        risk_level = "LOW"
    elif risk_score < 50.0:
        risk_level = "MEDIUM"
    elif risk_score < 75.0:
        risk_level = "HIGH"
    else:
        risk_level = "CRITICAL"

    return risk_score, risk_level, contributions, suspicious_events


# ---------------------------------------------------------------------------
# Public Service Functions
# ---------------------------------------------------------------------------

def analyze_interview(interview_id: str, user_role: str) -> dict:
    """
    Perform a complete cheating risk analysis for an interview from stored
    proctoring logs, and upsert a report in the cheating_reports collection.

    Restricted to authorized admin/recruiter roles.
    """
    _validate_admin_role(user_role)
    interview_oid = _validate_object_id(interview_id, "interview ID")

    db = Database.get_db()

    # Find interview to ensure existence
    interview = db["interviews"].find_one({"_id": interview_oid})
    if not interview:
        raise ValueError("Interview not found.")

    user_oid = interview.get("userId")

    # Aggregate proctoring events by eventType
    pipeline = [
        {"$match": {"interviewId": interview_oid}},
        {"$group": {
            "_id": "$eventType",
            "count": {"$sum": 1}
        }}
    ]

    cursor = db["proctoring_logs"].aggregate(pipeline)

    event_counts = {}
    total_events = 0

    for doc in cursor:
        evt_type = doc["_id"]
        count = doc["count"]
        if evt_type:
            event_counts[evt_type] = count
            total_events += count

    # Run deterministic scoring
    risk_score, risk_level, contributions, suspicious_events = calculate_risk_score(event_counts)

    # Upsert report
    now = datetime.utcnow()
    report_data = {
        "interviewId": interview_oid,
        "userId": user_oid,
        "riskScore": risk_score,
        "riskLevel": risk_level,
        "totalEvents": total_events,
        "suspiciousEvents": suspicious_events,
        "eventCounts": event_counts,
        "eventContributions": contributions,
        "updatedAt": now
    }

    # Atomically update existing or insert new report, maintaining initial createdAt timestamp
    db[CheatingReport.COLLECTION].update_one(
        {"interviewId": interview_oid},
        {
            "$set": report_data,
            "$setOnInsert": {
                "_id": ObjectId(),
                "createdAt": now
            }
        },
        upsert=True
    )

    # Load and return the final report
    report = db[CheatingReport.COLLECTION].find_one({"interviewId": interview_oid})
    return CheatingReport.response(report)


def get_cheating_report(interview_id: str, user_role: str) -> dict:
    """
    Retrieve an existing cheating report for the specified interview.

    Restricted to authorized admin/recruiter roles.
    """
    _validate_admin_role(user_role)
    interview_oid = _validate_object_id(interview_id, "interview ID")

    db = Database.get_db()

    # Find interview to ensure existence
    interview = db["interviews"].find_one({"_id": interview_oid})
    if not interview:
        raise ValueError("Interview not found.")

    report = db[CheatingReport.COLLECTION].find_one({"interviewId": interview_oid})
    if not report:
        raise ValueError("Cheating report not found for this interview.")

    return CheatingReport.response(report)


def get_cheating_report_for_candidate(interview_id: str, user_id: str) -> dict:
    """
    Retrieve an existing cheating report for the specified interview.

    Unlike get_cheating_report(), this function does NOT require admin role.
    Instead it verifies that the requesting user is the interview owner
    (i.e. the candidate who sat the interview).

    Args:
        interview_id: str — the interview ObjectId as a string.
        user_id: str — the authenticated user's ObjectId as a string.

    Returns:
        dict — serialized CheatingReport document.

    Raises:
        ValueError — if the interview or report is not found, or if the
                     requesting user does not own the interview.
    """
    interview_oid = _validate_object_id(interview_id, "interview ID")
    user_oid = _validate_object_id(user_id, "user ID")

    db = Database.get_db()

    # Verify interview exists
    interview = db["interviews"].find_one({"_id": interview_oid})
    if not interview:
        raise ValueError("Interview not found.")

    # Verify ownership — only the candidate who owns the interview may read their report
    interview_user_id = interview.get("userId")
    if str(interview_user_id) != str(user_oid):
        raise ValueError("Access denied. You do not have permission to access this report.")

    report = db[CheatingReport.COLLECTION].find_one({"interviewId": interview_oid})
    if not report:
        raise ValueError("Cheating report not found for this interview.")

    return CheatingReport.response(report)
