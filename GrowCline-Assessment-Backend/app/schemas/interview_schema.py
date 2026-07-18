"""
Interview Schemas
Pydantic v2 request and response schemas for the AI Interview module.

Validates every inbound request body and documents every outbound response
shape for FastAPI automatic validation and OpenAPI generation.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------

class InterviewCreateRequest(BaseModel):
    """
    Request body for POST /api/interviews/start.

    Defines the parameters required to begin a new AI interview session.
    The userId is always sourced from the JWT token — never from this body.
    """

    jobRole: str = Field(
        ...,
        min_length=2,
        max_length=120,
        description="Target job role for the interview (e.g. 'Backend Developer').",
        examples=["Backend Developer"],
    )
    interviewType: str = Field(
        ...,
        description="Interview category: TECHNICAL | HR | BEHAVIORAL | RESUME_BASED.",
        examples=["TECHNICAL"],
    )
    difficulty: str = Field(
        default="MEDIUM",
        description="Question difficulty: EASY | MEDIUM | HARD.",
        examples=["MEDIUM"],
    )
    totalQuestions: int = Field(
        default=10,
        ge=1,
        le=20,
        description="Total number of questions for the session (1–20).",
        examples=[10],
    )
    durationSeconds: int = Field(
        default=1800,
        ge=300,
        le=7200,
        description="Allowed interview duration in seconds (5 min – 2 hrs).",
        examples=[1800],
    )
    resumeId: Optional[str] = Field(
        default=None,
        description="ObjectId string of the candidate's uploaded resume (required for RESUME_BASED type).",
        examples=[None],
    )

    @field_validator("interviewType")
    @classmethod
    def validate_interview_type(cls, v: str) -> str:
        allowed = {"TECHNICAL", "HR", "BEHAVIORAL", "RESUME_BASED"}
        if v.upper() not in allowed:
            raise ValueError(f"interviewType must be one of {allowed}.")
        return v.upper()

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, v: str) -> str:
        allowed = {"EASY", "MEDIUM", "HARD"}
        if v.upper() not in allowed:
            raise ValueError(f"difficulty must be one of {allowed}.")
        return v.upper()


class QuestionRequest(BaseModel):
    """
    Request body for POST /api/interviews/{interview_id}/question.

    Optionally carry a hint to the AI about what sub-topic to cover next.
    """

    topicHint: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Optional topic hint to guide question generation.",
        examples=["REST API design"],
    )


class AnswerRequest(BaseModel):
    """
    Request body for POST /api/interviews/{interview_id}/answer.

    Carries the candidate's textual answer to a specific question, triggering
    AI evaluation and progression to the next question.
    """

    questionId: str = Field(
        ...,
        description="ObjectId string of the question being answered.",
        examples=["64fa1c2e3b5a4d0012345678"],
    )
    candidateAnswer: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="The candidate's answer text (1–5000 characters).",
        examples=["REST APIs use HTTP verbs and stateless communication..."],
    )

    @field_validator("candidateAnswer")
    @classmethod
    def strip_answer(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("candidateAnswer must not be blank.")
        return stripped


# ---------------------------------------------------------------------------
# Response Schemas
# ---------------------------------------------------------------------------

class InterviewResponse(BaseModel):
    """Serialised representation of a single interview session document."""

    id: str
    userId: str
    jobRole: str
    interviewType: str
    status: str
    difficulty: str
    currentQuestion: int
    totalQuestions: int
    startedAt: Optional[str]
    endedAt: Optional[str]
    durationSeconds: int
    elapsedSeconds: Optional[int]
    remainingSeconds: Optional[int]
    resumeId: Optional[str]
    createdAt: Optional[str]
    updatedAt: Optional[str]


class QuestionResponse(BaseModel):
    """Serialised representation of an AI-generated interview question."""

    id: str
    interviewId: str
    questionNumber: int
    questionType: str
    questionText: str
    generatedBy: str
    createdAt: Optional[str]

    # Supplementary context for the frontend timer / progress bar
    remainingQuestions: Optional[int] = None
    totalQuestions: Optional[int] = None
    remainingSeconds: Optional[int] = None


class EvaluationResponse(BaseModel):
    """
    AI evaluation result returned after a candidate submits an answer.

    Includes the numeric score, narrative feedback, and structured
    strength / weakness / suggestion lists for display in the UI.
    """

    id: str
    interviewId: str
    questionId: str
    candidateAnswer: str
    evaluationScore: int
    feedback: str
    keywordsMatched: List[str]
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]
    answeredAt: Optional[str]

    # Current session progress after the answer was saved
    currentQuestion: Optional[int] = None
    totalQuestions: Optional[int] = None
    interviewComplete: Optional[bool] = None


class InterviewSummaryResponse(BaseModel):
    """Summary envelope returned when an interview session ends."""

    interviewId: str
    status: str
    jobRole: str
    interviewType: str
    difficulty: str
    totalQuestions: int
    questionsAnswered: int
    averageScore: Optional[float]
    startedAt: Optional[str]
    endedAt: Optional[str]
    durationSeconds: int
    actualDurationSeconds: Optional[int]


class InterviewHistoryItem(BaseModel):
    """A single question-answer pair within the interview history."""

    questionNumber: int
    question: str
    answer: Optional[str]
    evaluationScore: Optional[int]
    feedback: Optional[str]
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]
    answeredAt: Optional[str]


class InterviewHistoryResponse(BaseModel):
    """
    Complete interview history including all questions, answers, and evaluations.

    This is the authoritative data source for Video Recording, Live Proctoring,
    Cheating Detection, and Interview Analytics downstream modules.
    """

    interviewId: str
    userId: str
    jobRole: str
    interviewType: str
    difficulty: str
    status: str
    totalQuestions: int
    questionsAnswered: int
    averageScore: Optional[float]
    startedAt: Optional[str]
    endedAt: Optional[str]
    durationSeconds: int
    history: List[InterviewHistoryItem]
