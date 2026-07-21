"""
FastAPI Pydantic Request Models
Replaces Marshmallow schemas for FastAPI route body validation and Swagger docs.
These models are used ONLY in route function signatures.
Controllers still receive plain dicts via .model_dump().
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, EmailStr


# ── Auth ─────────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    fullName: str
    email: EmailStr
    password: str
    role: str = "candidate"

    model_config = {"json_schema_extra": {
        "example": {
            "fullName": "John Doe",
            "email": "john@example.com",
            "password": "Password123",
            "role": "candidate"
        }
    }}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    model_config = {"json_schema_extra": {
        "example": {
            "email": "john@example.com",
            "password": "Password123"
        }
    }}


class UpdateProfileRequest(BaseModel):
    fullName: Optional[str] = None
    email: Optional[EmailStr] = None

    model_config = {"json_schema_extra": {
        "example": {
            "fullName": "John Doe",
            "email": "john@example.com"
        }
    }}


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

    model_config = {"json_schema_extra": {
        "example": {
            "current_password": "OldPassword123",
            "new_password": "NewPassword123"
        }
    }}


# ── User ─────────────────────────────────────────────────────────────────────

class CreateUserRequest(BaseModel):
    fullName: str
    email: EmailStr
    password: str
    role: str = "candidate"

    model_config = {"json_schema_extra": {
        "example": {
            "fullName": "Jane Doe",
            "email": "jane@example.com",
            "password": "Password123",
            "role": "candidate"
        }
    }}


class UpdateUserRequest(BaseModel):
    fullName: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None

    model_config = {"json_schema_extra": {
        "example": {
            "fullName": "Jane Doe Updated",
            "email": "jane_new@example.com"
        }
    }}


# ── Aptitude ─────────────────────────────────────────────────────────────────

class AptitudeQuestionRequest(BaseModel):
    question: str
    category: str
    difficulty: str
    options: List[str]
    correctAnswer: Optional[str] = None
    correct_answer: Optional[str] = None
    explanation: str = ""
    marks: int = 1
    questionType: str = "MCQ"
    tags: List[str] = []

    model_config = {"json_schema_extra": {
        "example": {
            "question": "What is 2 + 2?",
            "category": "Math",
            "difficulty": "Easy",
            "options": ["3", "4", "5", "6"],
            "correctAnswer": "4",
            "explanation": "Basic arithmetic.",
            "marks": 1,
            "questionType": "MCQ",
            "tags": ["math", "arithmetic"]
        }
    }}


class AptitudeGenerateRequest(BaseModel):
    numberOfQuestions: int = 10
    difficulty: Optional[str] = None

    model_config = {"json_schema_extra": {
        "example": {"numberOfQuestions": 10, "difficulty": "Easy"}
    }}


class AptitudeSubmitRequest(BaseModel):
    answers: List[Dict[str, Any]] = []

    model_config = {"json_schema_extra": {
        "example": {"answers": [{"questionId": "abc123", "selectedAnswer": "4"}]}
    }}


class AptitudeUpdateRequest(BaseModel):
    question: Optional[str] = None
    category: Optional[str] = None
    difficulty: Optional[str] = None
    options: Optional[List[str]] = None
    correctAnswer: Optional[str] = None
    explanation: Optional[str] = None
    marks: Optional[int] = None
    isActive: Optional[bool] = None


# ── Technical ─────────────────────────────────────────────────────────────────

class TechnicalQuestionRequest(BaseModel):
    question: str
    technology: str = "Python"
    category: Optional[str] = None
    difficulty: str = "Easy"
    options: List[str]
    correctAnswer: Optional[str] = None
    correct_answer: Optional[str] = None
    explanation: str = ""
    marks: int = 1
    questionType: str = "MCQ"
    tags: List[str] = []

    model_config = {"json_schema_extra": {
        "example": {
            "question": "What is a Python list?",
            "technology": "Python",
            "difficulty": "Easy",
            "options": ["A sequence", "A dictionary", "A set", "A tuple"],
            "correctAnswer": "A sequence",
            "marks": 1,
            "questionType": "MCQ"
        }
    }}


class TechnicalGenerateRequest(BaseModel):
    numberOfQuestions: int = 10
    difficulty: Optional[str] = None
    technology: Optional[str] = None

    model_config = {"json_schema_extra": {
        "example": {"numberOfQuestions": 10, "technology": "Python", "difficulty": "Easy"}
    }}


class TechnicalSubmitRequest(BaseModel):
    answers: List[Dict[str, Any]] = []

    model_config = {"json_schema_extra": {
        "example": {"answers": [{"questionId": "abc123", "selectedAnswer": "A sequence"}]}
    }}


class TechnicalUpdateRequest(BaseModel):
    question: Optional[str] = None
    technology: Optional[str] = None
    category: Optional[str] = None
    difficulty: Optional[str] = None
    options: Optional[List[str]] = None
    correctAnswer: Optional[str] = None
    explanation: Optional[str] = None
    marks: Optional[int] = None
    isActive: Optional[bool] = None


# ── Coding ────────────────────────────────────────────────────────────────────

class CodingQuestionRequest(BaseModel):
    title: str
    problemStatement: str
    programmingLanguage: str = "Python"
    difficulty: str = "Easy"
    inputFormat: str = ""
    outputFormat: str = ""
    constraints: str = ""
    sampleInput: str = ""
    sampleOutput: str = ""
    testCases: List[Dict[str, Any]] = []
    hiddenTestCases: List[Dict[str, Any]] = []
    marks: int = 10
    category: str = "Algorithms"
    tags: List[str] = []

    model_config = {"json_schema_extra": {
        "example": {
            "title": "Two Sum",
            "problemStatement": "Given an array, find two numbers that add to target.",
            "programmingLanguage": "Python",
            "difficulty": "Easy",
            "marks": 10,
            "category": "Algorithms"
        }
    }}


class CodingGenerateRequest(BaseModel):
    numberOfQuestions: int = 3
    difficulty: Optional[str] = None

    model_config = {"json_schema_extra": {
        "example": {"numberOfQuestions": 3, "difficulty": "Easy"}
    }}


class CodingSubmitRequest(BaseModel):
    answers: List[Dict[str, Any]] = []

    model_config = {"json_schema_extra": {
        "example": {"answers": [{"questionId": "abc123", "code": "def solution(): pass"}]}
    }}


class CodingUpdateRequest(BaseModel):
    title: Optional[str] = None
    programmingLanguage: Optional[str] = None
    difficulty: Optional[str] = None
    problemStatement: Optional[str] = None
    inputFormat: Optional[str] = None
    outputFormat: Optional[str] = None
    constraints: Optional[str] = None
    sampleInput: Optional[str] = None
    sampleOutput: Optional[str] = None
    testCases: Optional[List[Dict[str, Any]]] = None
    hiddenTestCases: Optional[List[Dict[str, Any]]] = None
    marks: Optional[int] = None
    isActive: Optional[bool] = None


# ── Assessment ────────────────────────────────────────────────────────────────

class AssessmentCreateRequest(BaseModel):
    title: str
    description: str = ""
    duration: int = 60
    status: str = "Draft"

    model_config = {"json_schema_extra": {
        "example": {
            "title": "Python Assessment",
            "description": "Full Python skills test",
            "duration": 60,
            "status": "Draft"
        }
    }}


class AssessmentUpdateRequest(BaseModel):
    title: Optional[str] = None
    duration: Optional[int] = None
    status: Optional[str] = None


class AssessmentSubmitRequest(BaseModel):
    answers: Optional[Dict[str, Any]] = {}
    userId: Optional[str] = None

    model_config = {"json_schema_extra": {
        "example": {"userId": "user123", "answers": {}}
    }}


# ── Results ────────────────────────────────────────────────────────────────────

class SaveResultRequest(BaseModel):
    assessmentId: str
    userId: str
    aptitudeScore: float = 0.0
    technicalScore: float = 0.0
    codingScore: float = 0.0
    totalScore: float = 0.0
    percentage: float = 0.0
    totalQuestions: int = 0
    correctAnswers: int = 0
    wrongAnswers: int = 0
    unansweredQuestions: int = 0
    totalTime: int = 0
    strongestSkill: str = ""
    weakestSkill: str = ""
    recommendation: str = ""
    status: str = "Completed"
    aptitudeAnswers: List[Dict[str, Any]] = []
    technicalAnswers: List[Dict[str, Any]] = []
    codingSubmissions: List[Dict[str, Any]] = []
    rank: Optional[int] = None

    model_config = {"json_schema_extra": {
        "example": {
            "assessmentId": "assess123",
            "userId": "user456",
            "aptitudeScore": 80.0,
            "technicalScore": 70.0,
            "codingScore": 60.0,
            "totalScore": 70.0,
            "percentage": 70.0,
            "status": "Completed"
        }
    }}


class UpdateResultRequest(BaseModel):
    status: Optional[str] = None
    rank: Optional[int] = None
    recommendation: Optional[str] = None


# ── Analytics ─────────────────────────────────────────────────────────────────

class DashboardAnalyticsRequest(BaseModel):
    userId: Optional[str] = None

    model_config = {"json_schema_extra": {
        "example": {"userId": "user123"}
    }}
