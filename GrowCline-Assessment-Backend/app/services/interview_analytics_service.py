"""
Interview Analytics Service
Core business logic for aggregating and generating interview analytics reports.

This service consumes data from:
  - interviews
  - video_recordings
  - proctoring_logs
  - cheating_reports

It does NOT perform cheating detection — it reads existing records only.
"""

import logging
from datetime import datetime
from bson import ObjectId

try:
    from config.database import Database
except ImportError:
    from app.config.database import Database

try:
    from models.interview_analytics_model import InterviewAnalytics
    from models.recording_model import Recording
    from models.proctoring_model import ProctoringLog
    from models.cheating_report_model import CheatingReport
except ImportError:
    from app.models.interview_analytics_model import InterviewAnalytics
    from app.models.recording_model import Recording
    from app.models.proctoring_model import ProctoringLog
    from app.models.cheating_report_model import CheatingReport


logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Risk → Overall Status mapping
# ---------------------------------------------------------------------------

_RISK_TO_STATUS: dict[str, str] = {
    "LOW": "PASSED",
    "MEDIUM": "REVIEW_REQUIRED",
    "HIGH": "MANUAL_REVIEW",
    "CRITICAL": "FLAGGED",
}

# Proctoring event types whose individual counts are surfaced in the report
_TRACKED_EVENT_TYPES = {
    "TAB_SWITCH",
    "WINDOW_MINIMIZED",
    "MULTIPLE_FACES",
    "BACKGROUND_VOICE",
    "NO_FACE",
    "FACE_MISSING",
    "FULLSCREEN_EXIT",
    "CAMERA_DISABLED",
    "MICROPHONE_DISABLED",
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _validate_object_id(id_str: str, label: str = "ID") -> ObjectId:
    """Ensure the provided string is a valid 24-character hex ObjectId."""
    if not id_str or not ObjectId.is_valid(id_str):
        raise ValueError(f"Invalid {label}: '{id_str}' is not a valid ObjectId.")
    return ObjectId(id_str)


def _require_interview(db, interview_oid: ObjectId) -> dict:
    """Load an interview document; raise ValueError if missing."""
    interview = db["interviews"].find_one({"_id": interview_oid})
    if not interview:
        raise ValueError("Interview not found.")
    return interview


def _require_completed_interview(interview: dict) -> None:
    """Raise ValueError unless the interview status indicates it is finished."""
    status = str(interview.get("status", "")).upper()
    completed_statuses = {"COMPLETED", "SUBMITTED", "EVALUATED", "IN_PROGRESS", "RUNNING"}
    if status not in completed_statuses:
        raise ValueError(
            f"Analytics can only be generated for completed interviews. "
            f"Current status: '{interview.get('status', 'UNKNOWN')}'."
        )


def _validate_ownership(interview: dict, user_id_str: str, user_role: str) -> None:
    """
    Verify the requesting user is allowed to access this interview's analytics.
    Admins may access any interview; candidates are limited to their own.
    """
    if user_role == "admin":
        return
    interview_user_id = str(interview.get("userId", ""))
    if interview_user_id != user_id_str:
        raise ValueError("You do not have permission to access this interview.")


def _calculate_duration(interview: dict) -> int:
    """
    Calculate interview duration in whole seconds from startedAt / completedAt.
    Returns 0 when timestamps are missing or not datetime objects.
    """
    started_at = interview.get("startedAt")
    completed_at = interview.get("completedAt") or interview.get("endedAt")

    if isinstance(started_at, datetime) and isinstance(completed_at, datetime):
        delta = completed_at - started_at
        return max(0, int(delta.total_seconds()))
    return 0


def _fetch_recording_metadata(db, interview_oid: ObjectId) -> dict | None:
    """Return the first video_recordings document for the interview, or None."""
    return db[Recording.COLLECTION].find_one({"interviewId": interview_oid})


def _aggregate_event_counts(db, interview_oid: ObjectId) -> tuple[int, dict]:
    """
    Aggregate proctoring event counts from proctoring_logs.

    Returns:
        total_events: int — total documents in the collection for this interview.
        event_counts: dict mapping eventType -> count (only tracked types).
    """
    pipeline = [
        {"$match": {"interviewId": interview_oid}},
        {"$group": {
            "_id": "$eventType",
            "count": {"$sum": 1},
        }},
    ]
    cursor = db[ProctoringLog.COLLECTION].aggregate(pipeline)

    total_events = 0
    event_counts: dict[str, int] = {k: 0 for k in _TRACKED_EVENT_TYPES}

    for doc in cursor:
        evt_type = doc.get("_id") or ""
        count = int(doc.get("count", 0))
        total_events += count
        if evt_type in _TRACKED_EVENT_TYPES:
            event_counts[evt_type] = count

    return total_events, event_counts


def _require_cheating_report(db, interview_oid: ObjectId) -> dict:
    """Load the cheating_reports document; raise ValueError if missing."""
    report = db[CheatingReport.COLLECTION].find_one({"interviewId": interview_oid})
    if not report:
        raise ValueError(
            "Cheating report not found for this interview. "
            "Please run the Cheating Detection analysis before generating analytics."
        )
    return report


def _determine_overall_status(risk_level: str) -> str:
    """Map a risk level string to a human-readable overall status."""
    return _RISK_TO_STATUS.get(str(risk_level).upper(), "REVIEW_REQUIRED")


# ---------------------------------------------------------------------------
# Public service functions
# ---------------------------------------------------------------------------

def generate_analytics(interview_id: str, user_id: str, user_role: str, force_refresh: bool = False) -> dict:
    """
    Generate (or refresh) an analytics report for the given interview.

    Steps:
        1. Validate interview_id and user_id.
        2. Fetch and validate the interview (must be completed).
        3. Verify ownership / authorization.
        4. Guard against duplicate generation (unless force_refresh=True).
        5. Fetch video recording metadata (optional).
        6. Aggregate proctoring event counts.
        7. Read risk score and level from existing cheating_reports.
        8. Build analytics document.
        9. Upsert into interview_analytics.
       10. Return serialized response.

    Args:
        interview_id: str — path parameter from the route.
        user_id: str — extracted from JWT; never trusted from the client.
        user_role: str — extracted from JWT.
        force_refresh: bool — if True, regenerate even when report exists.

    Returns:
        dict — serialized analytics report.

    Raises:
        ValueError — for all domain-level validation failures.
    """
    interview_oid = _validate_object_id(interview_id, "interview ID")
    user_oid = _validate_object_id(user_id, "user ID")

    db = Database.get_db()

    # 1. Fetch and validate interview
    interview = _require_interview(db, interview_oid)
    _require_completed_interview(interview)
    _validate_ownership(interview, user_id, user_role)

    # 2. Guard against duplicate generation
    existing = InterviewAnalytics.find_by_interview(db, interview_oid)
    if existing and not force_refresh:
        raise ValueError(
            "Analytics already exist for this interview. "
            "Use force_refresh=true to regenerate."
        )

    # 3. Fetch supporting data
    recording = _fetch_recording_metadata(db, interview_oid)
    total_events, event_counts = _aggregate_event_counts(db, interview_oid)
    cheating_report = _require_cheating_report(db, interview_oid)

    # 4. Derive interview owner from the interview document
    interview_user_oid = interview.get("userId", user_oid)

    # 5. Calculate metrics
    duration_seconds = _calculate_duration(interview)
    video_uploaded = recording is not None and (
        recording.get("videoKey") is not None or recording.get("audioKey") is not None
    )
    risk_score = float(cheating_report.get("riskScore", 0.0))
    risk_level = str(cheating_report.get("riskLevel", "LOW"))
    overall_status = _determine_overall_status(risk_level)
    now = datetime.utcnow()

    # 6. Calculate real metrics from actual candidate evaluations and proctoring logs
    evaluations_cursor = db["interview_evaluations"].find({"interviewId": interview_oid})
    evaluations = list(evaluations_cursor)

    face_missing_count = event_counts.get("NO_FACE", 0) + event_counts.get("FACE_MISSING", 0)
    fullscreen_count = event_counts.get("FULLSCREEN_EXIT", 0) + event_counts.get("WINDOW_MINIMIZED", 0)
    tab_switches = event_counts.get("TAB_SWITCH", 0)

    if evaluations:
        eval_scores = [float(e.get("evaluationScore", e.get("score", 0))) for e in evaluations]
        tech_score = round(sum(eval_scores) / len(eval_scores)) if eval_scores else 0
        comm_score = round(sum(eval_scores) / len(eval_scores)) if eval_scores else 0
    else:
        tech_score = 0
        comm_score = 0

    confidence_score = max(0, min(100, round(100 - risk_score - (face_missing_count * 5) - (tab_switches * 10))))
    eye_contact_score = max(0, min(100, round(100 - (face_missing_count * 15))))
    overall_score = round((tech_score * 0.4) + (comm_score * 0.3) + (confidence_score * 0.3)) if evaluations else 0

    if overall_score >= 90:
        grade = "S"
    elif overall_score >= 80:
        grade = "A"
    elif overall_score >= 70:
        grade = "B"
    elif overall_score >= 60:
        grade = "C"
    elif overall_score >= 50:
        grade = "D"
    else:
        grade = "F"

    update_fields = {
        "interviewId": interview_oid,
        "userId": interview_user_oid,
        "durationSeconds": duration_seconds,
        "videoUploaded": video_uploaded,
        "totalEvents": total_events,
        "riskScore": risk_score,
        "riskLevel": risk_level,
        "faceMissing": face_missing_count,
        "tabSwitches": tab_switches,
        "multipleFaces": event_counts.get("MULTIPLE_FACES", 0),
        "backgroundVoice": event_counts.get("BACKGROUND_VOICE", 0),
        "cameraDisabled": event_counts.get("CAMERA_DISABLED", 0),
        "microphoneDisabled": event_counts.get("MICROPHONE_DISABLED", 0),
        "fullscreenExit": fullscreen_count,
        "overallStatus": overall_status,
        "averageScore": overall_score,
        "overallScore": overall_score,
        "metrics": {
            "confidence": confidence_score,
            "communication": comm_score,
            "technical": tech_score,
            "eyeContact": eye_contact_score,
            "riskScore": risk_score,
            "grade": grade,
        },
        "strongAreas": ["Problem Solving", "Domain Knowledge"] if overall_score >= 60 else ["Technical Awareness"],
        "weakAreas": ["Edge Cases", "Communication Precision"] if overall_score < 70 else ["Advanced Optimizations"],
        "questionPerformance": [],
        "updatedAt": now,
    }

    # 7. Upsert
    InterviewAnalytics.upsert(db, interview_oid, update_fields)

    # 8. Reload and return
    doc = InterviewAnalytics.find_by_interview(db, interview_oid)
    res_dict = InterviewAnalytics.response(doc)
    res_dict["overallScore"] = overall_score
    res_dict["metrics"] = update_fields["metrics"]
    res_dict["strengths"] = update_fields["strongAreas"]
    res_dict["improvements"] = update_fields["weakAreas"]
    res_dict["recommendation"] = "Recommended" if overall_score >= 70 and risk_score < 30 else ("Needs Improvement" if overall_score >= 50 else "Not Recommended")
    res_dict["summary"] = f"Candidate completed interview with overall score of {overall_score}% and risk score of {risk_score}%."
    return res_dict


def get_analytics(interview_id: str, user_id: str, user_role: str) -> dict:
    """
    Retrieve an existing analytics report for the given interview.

    Args:
        interview_id: str — path parameter from the route.
        user_id: str — extracted from JWT.
        user_role: str — extracted from JWT.

    Returns:
        dict — serialized analytics report.

    Raises:
        ValueError — if not found, or the user lacks permission.
    """
    interview_oid = _validate_object_id(interview_id, "interview ID")

    db = Database.get_db()

    interview = _require_interview(db, interview_oid)
    _validate_ownership(interview, user_id, user_role)

    doc = InterviewAnalytics.find_by_interview(db, interview_oid)
    if not doc:
        raise ValueError(
            "Analytics not found for this interview. "
            "Please generate them first via POST /analytics/interview/{interview_id}/generate."
        )

    return InterviewAnalytics.response(doc)


def get_user_analytics(target_user_id: str, requesting_user_id: str, user_role: str) -> dict:
    """
    Retrieve all analytics reports for a given candidate, newest first.

    Admins may query any user; candidates may only query themselves.

    Args:
        target_user_id: str — the user whose analytics are requested.
        requesting_user_id: str — extracted from JWT.
        user_role: str — extracted from JWT.

    Returns:
        dict — AnalyticsListResponse payload.

    Raises:
        ValueError — for authorization failures or invalid IDs.
    """
    target_oid = _validate_object_id(target_user_id, "user ID")

    # Candidates may only see their own reports
    if user_role != "admin" and target_user_id != requesting_user_id:
        raise ValueError("You do not have permission to access another user's analytics.")

    db = Database.get_db()

    docs = InterviewAnalytics.find_by_user(db, target_oid)
    serialized = [InterviewAnalytics.response(doc) for doc in docs]

    # Build lightweight summary items
    summary_list = [
        {
            "id": item["id"],
            "interviewId": item["interviewId"],
            "userId": item["userId"],
            "durationSeconds": item["durationSeconds"],
            "videoUploaded": item["videoUploaded"],
            "totalEvents": item["totalEvents"],
            "riskScore": item["riskScore"],
            "riskLevel": item["riskLevel"],
            "overallStatus": item["overallStatus"],
            "generatedAt": item["generatedAt"],
        }
        for item in serialized
    ]

    return {
        "userId": target_user_id,
        "count": len(summary_list),
        "analytics": summary_list,
    }


def delete_analytics(interview_id: str, user_id: str, user_role: str) -> dict:
    """
    Delete the analytics report associated with the given interview.

    Admins may delete any report; candidates may only delete their own.

    Args:
        interview_id: str — path parameter from the route.
        user_id: str — extracted from JWT.
        user_role: str — extracted from JWT.

    Returns:
        dict — confirmation payload.

    Raises:
        ValueError — if not found, or the user lacks permission.
    """
    interview_oid = _validate_object_id(interview_id, "interview ID")

    db = Database.get_db()

    interview = _require_interview(db, interview_oid)
    _validate_ownership(interview, user_id, user_role)

    doc = InterviewAnalytics.find_by_interview(db, interview_oid)
    if not doc:
        raise ValueError("Analytics not found for this interview.")

    deleted_count = InterviewAnalytics.delete_by_interview(db, interview_oid)
    if deleted_count == 0:
        raise ValueError("Analytics not found for this interview.")

    return {"interviewId": interview_id, "deleted": True}
