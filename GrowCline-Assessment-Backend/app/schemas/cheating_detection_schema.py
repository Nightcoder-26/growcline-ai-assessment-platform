"""
Cheating Detection Schemas
Pydantic v2 schemas for cheating report API serialization.
"""

from typing import Dict
from pydantic import BaseModel, Field


class EventContributionDetail(BaseModel):
    """
    Detailed statistics and contribution points for a specific event type.
    """
    count: int = Field(..., description="Actual occurrence count of the event type.")
    effectiveCount: int = Field(..., description="Capped count used for scoring.")
    weight: int = Field(..., description="Configured scoring weight for this event type.")
    contribution: int = Field(..., description="The calculated contribution (effectiveCount * weight) points.")


class CheatingReportResponse(BaseModel):
    """
    Response schema for serializing a single cheating report.
    """
    id: str
    interviewId: str
    userId: str
    riskScore: float
    riskLevel: str
    totalEvents: int
    suspiciousEvents: int
    eventCounts: Dict[str, int]
    eventContributions: Dict[str, EventContributionDetail]
    createdAt: str
    updatedAt: str
