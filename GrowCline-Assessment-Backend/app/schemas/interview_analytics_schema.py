"""
Interview Analytics Schemas
Pydantic v2 schemas for request validation and response serialization
of the Interview Analytics module.
"""

from typing import Optional, List
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class AnalyticsGenerateRequest(BaseModel):
    """
    Optional request body for the POST /analytics/interview/{interview_id}/generate
    endpoint.  Currently no additional client-supplied fields are required —
    the service derives all data from server-side collections.  The schema is
    defined to allow future extensibility (e.g. forcing a refresh flag).
    """
    force_refresh: bool = Field(
        default=False,
        description="When true, regenerate analytics even if a report already exists.",
    )


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class AnalyticsSummary(BaseModel):
    """
    Lightweight summary of an interview's analytics, suitable for list views.
    """
    id: str
    interviewId: str
    userId: str
    durationSeconds: int
    videoUploaded: bool
    totalEvents: int
    riskScore: float
    riskLevel: str
    overallStatus: str
    generatedAt: str


class AnalyticsResponse(BaseModel):
    """
    Full response schema for a single interview analytics report.
    """
    id: str
    interviewId: str
    userId: str
    durationSeconds: int
    videoUploaded: bool
    totalEvents: int
    riskScore: float
    riskLevel: str
    tabSwitches: int
    multipleFaces: int
    backgroundVoice: int
    cameraDisabled: int
    microphoneDisabled: int
    fullscreenExit: int
    overallStatus: str
    generatedAt: str
    updatedAt: str


class AnalyticsListResponse(BaseModel):
    """
    Response envelope for a list of analytics summaries belonging to one user.
    """
    userId: str
    count: int
    analytics: List[AnalyticsSummary]
