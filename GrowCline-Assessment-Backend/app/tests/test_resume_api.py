"""
Resume & Personalized Assessment API Unit Tests
Tests resume endpoints, status check, profile retrieval, and assessment generation.
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from bson import ObjectId

from app import app
from app.middleware.auth_middleware import get_current_user

client = TestClient(app)

MOCK_USER = {
    "_id": ObjectId("507f1f77bcf86cd799439011"),
    "email": "test@candidate.com",
    "fullName": "Test Candidate",
    "role": "candidate",
}


@pytest.fixture(autouse=True)
def override_auth():
    app.dependency_overrides[get_current_user] = lambda: MOCK_USER
    yield
    app.dependency_overrides.clear()


def test_resume_status_unauthorized():
    # Clear overrides for unauthorized test
    app.dependency_overrides.clear()
    response = client.get("/api/resume/status")
    assert response.status_code == 401


@patch("app.controllers.resume_controller.ResumeService.get_resume_status")
def test_resume_status_success(mock_status):
    mock_status.return_value = {
        "success": True,
        "status_code": 200,
        "data": {
            "hasResume": True,
            "resumeFilename": "john_doe_resume.pdf",
            "resumeVersion": 1,
            "profileSummary": {"experienceLevel": "Junior", "topSkills": ["Python", "FastAPI"], "totalSkills": 5},
        },
    }

    response = client.get("/api/resume/status")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["hasResume"] is True


@patch("app.controllers.resume_controller.ResumeService.get_skill_profile")
def test_get_skill_profile_success(mock_profile):
    mock_profile.return_value = {
        "success": True,
        "status_code": 200,
        "data": {
            "experience_level": "Junior",
            "programming_languages": ["Python", "JavaScript"],
            "frameworks": ["FastAPI", "React"],
            "databases": ["MongoDB"],
        },
    }

    response = client.get("/api/resume/profile")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "programming_languages" in data["data"]


@patch("app.controllers.resume_controller.ResumeService.generate_assessment")
def test_generate_assessment_success(mock_gen):
    mock_gen.return_value = {
        "success": True,
        "status_code": 200,
        "message": "Personalized assessment ready.",
        "data": {
            "assessmentId": "607f1f77bcf86cd799439022",
            "isNew": True,
            "aptitudeCount": 25,
            "technicalCount": 25,
            "codingCount": 15,
        },
    }

    response = client.post("/api/resume/generate-assessment")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["aptitudeCount"] == 25
    assert data["data"]["technicalCount"] == 25
    assert data["data"]["codingCount"] == 15
