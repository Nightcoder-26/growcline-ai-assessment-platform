"""
Resume Controller Module
Handles HTTP request/response for resume upload, analysis, profile retrieval,
personalized assessment generation, and resume deletion.

Architecture: Route → Controller → Service → MongoDB
"""

import logging
from typing import Tuple, Dict, Any, Optional

try:
    from services.resume_service import ResumeService
except ImportError:
    from app.services.resume_service import ResumeService

logger = logging.getLogger(__name__)


class ResumeController:
    """Resume & Personalized Assessment Controller"""

    @staticmethod
    def upload_resume(file_bytes: bytes, filename: str, user_id: str) -> Tuple[Dict[str, Any], int]:
        """
        POST /api/resume/upload
        Upload and analyze a candidate resume. Supports PDF and DOCX.
        """
        if not user_id:
            return {"success": False, "message": "Authentication required."}, 401

        if not file_bytes or not filename:
            return {"success": False, "message": "No file provided."}, 400

        filename_lower = filename.lower()
        if not (filename_lower.endswith(".pdf") or filename_lower.endswith(".docx") or filename_lower.endswith(".doc")):
            return {
                "success": False,
                "message": "Unsupported file format. Please upload a PDF or DOCX resume.",
            }, 400

        result = ResumeService.upload_and_analyze(user_id, file_bytes, filename)
        status_code = result.pop("status_code", 200)
        return result, status_code

    @staticmethod
    def get_resume_status(user_id: str) -> Tuple[Dict[str, Any], int]:
        """
        GET /api/resume/status
        Returns whether the user has an analyzed resume and summary info.
        """
        if not user_id:
            return {"success": False, "message": "Authentication required."}, 401

        result = ResumeService.get_resume_status(user_id)
        status_code = result.pop("status_code", 200)
        return result, status_code

    @staticmethod
    def get_skill_profile(user_id: str) -> Tuple[Dict[str, Any], int]:
        """
        GET /api/resume/profile
        Returns the full structured skill profile extracted from the resume.
        """
        if not user_id:
            return {"success": False, "message": "Authentication required."}, 401

        result = ResumeService.get_skill_profile(user_id)
        status_code = result.pop("status_code", 200)
        return result, status_code

    @staticmethod
    def generate_assessment(user_id: str, force_new: bool = False) -> Tuple[Dict[str, Any], int]:
        """
        POST /api/resume/generate-assessment
        Generate (or retrieve existing) personalized assessment:
        25 aptitude + 25 technical + 15 coding questions.

        If force_new=True, discard existing pending assessment and generate fresh.
        """
        if not user_id:
            return {"success": False, "message": "Authentication required."}, 401

        result = ResumeService.generate_assessment(user_id, force_new=force_new)
        status_code = result.pop("status_code", 200)
        return result, status_code

    @staticmethod
    def delete_resume(user_id: str) -> Tuple[Dict[str, Any], int]:
        """
        DELETE /api/resume
        Delete the candidate's resume and profile, allowing re-upload.
        """
        if not user_id:
            return {"success": False, "message": "Authentication required."}, 401

        result = ResumeService.delete_resume(user_id)
        status_code = result.pop("status_code", 200)
        return result, status_code
