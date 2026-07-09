"""
Proctoring Schemas
Pydantic v2 schemas for request validation and response serialization.
"""

from datetime import datetime
from typing import Optional, Dict

from pydantic import BaseModel, Field


class ProctoringEventCreate(BaseModel):
    """
    Schema for creating a single proctoring event.
    """
    interview_id: str = Field(..., description="The parent interview ID.")
    event_type: str = Field(..., description="The type of proctoring event (e.g. TAB_SWITCH).")
    client_timestamp: Optional[datetime] = Field(None, description="Optional client-side event timestamp.")


class ProctoringEventBatchItem(BaseModel):
    """
    Schema for a single event inside a batch ingestion request.
    """
    event_type: str = Field(..., description="The type of proctoring event (e.g. TAB_SWITCH).")
    client_timestamp: Optional[datetime] = Field(None, description="Optional client-side event timestamp.")


class ProctoringEventBatchCreate(BaseModel):
    """
    Schema for creating a batch of proctoring events.
    """
    interview_id: str = Field(..., description="The parent interview ID.")
    events: list[ProctoringEventBatchItem] = Field(..., description="List of events in the batch.")


class ProctoringEventResponse(BaseModel):
    """
    Schema for serializing a single proctoring event log.
    """
    id: str
    interviewId: str
    userId: str
    eventType: str
    severity: str
    timestamp: datetime
    clientTimestamp: Optional[datetime] = None


class ProctoringEventListResponse(BaseModel):
    """
    Response envelope for a paged list of proctoring events.
    """
    interviewId: str
    events: list[ProctoringEventResponse]
    count: int


class ProctoringSummaryResponse(BaseModel):
    """
    Response schema for the aggregated session summary of proctoring events.
    """
    interviewId: str
    totalEvents: int
    eventCounts: Dict[str, int]
    severityCounts: Dict[str, int]
    firstEventAt: Optional[datetime] = None
    lastEventAt: Optional[datetime] = None
