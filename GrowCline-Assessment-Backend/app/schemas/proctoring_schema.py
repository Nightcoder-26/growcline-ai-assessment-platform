"""
Proctoring Schemas
Pydantic v2 schemas for request validation and response serialization.
"""

from datetime import datetime
from typing import Optional, Dict

from pydantic import BaseModel, Field


from typing import Optional, Dict, Any, Union

class ProctoringEventCreate(BaseModel):
    interview_id: Optional[str] = None
    interviewId: Optional[str] = None
    event_type: Optional[str] = None
    eventType: Optional[str] = None
    client_timestamp: Optional[Union[datetime, str]] = None
    clientTimestamp: Optional[Union[datetime, str]] = None

    def get_interview_id(self) -> str:
        return self.interview_id or self.interviewId or ""

    def get_event_type(self) -> str:
        return self.event_type or self.eventType or ""


class ProctoringEventBatchItem(BaseModel):
    event_type: Optional[str] = None
    eventType: Optional[str] = None
    client_timestamp: Optional[Union[datetime, str]] = None
    clientTimestamp: Optional[Union[datetime, str]] = None

    def get_event_type(self) -> str:
        return self.event_type or self.eventType or ""


class ProctoringEventBatchCreate(BaseModel):
    interview_id: Optional[str] = None
    interviewId: Optional[str] = None
    events: list[Dict[str, Any]] = Field(default_factory=list)

    def get_interview_id(self) -> str:
        return self.interview_id or self.interviewId or ""


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
