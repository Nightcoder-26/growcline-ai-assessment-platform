"""
Resume Routes Module
Registers all resume-related API endpoints under /api/resume.
All endpoints require JWT authentication.
"""

from fastapi import APIRouter, Depends, UploadFile, File, Query
from fastapi.responses import JSONResponse

from app.middleware.auth_middleware import get_current_user
from app.controllers.resume_controller import ResumeController

router = APIRouter(prefix="/api/resume", tags=["Resume"])


@router.post("/upload", summary="Upload and analyze a resume (PDF or DOCX)")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """
    Upload a PDF or DOCX resume.
    Extracts text, analyzes via Groq AI, and stores a structured skill profile.
    Returns the extracted skill profile on success.
    """
    user_id = str(current_user["_id"])
    file_bytes = await file.read()
    filename = file.filename or "resume"
    result, status_code = ResumeController.upload_resume(file_bytes, filename, user_id)
    return JSONResponse(content=result, status_code=status_code)


@router.get("/status", summary="Get resume upload and analysis status")
async def get_resume_status(
    current_user: dict = Depends(get_current_user),
):
    """
    Returns whether the user has an uploaded and analyzed resume.
    Used by the frontend to decide whether to show the onboarding gate.
    """
    user_id = str(current_user["_id"])
    result, status_code = ResumeController.get_resume_status(user_id)
    return JSONResponse(content=result, status_code=status_code)


@router.get("/profile", summary="Get candidate skill profile extracted from resume")
async def get_skill_profile(
    current_user: dict = Depends(get_current_user),
):
    """
    Returns the full structured skill profile (skills, languages, frameworks, etc.)
    extracted from the candidate's uploaded resume.
    """
    user_id = str(current_user["_id"])
    result, status_code = ResumeController.get_skill_profile(user_id)
    return JSONResponse(content=result, status_code=status_code)


@router.post("/generate-assessment", summary="Generate personalized assessment based on resume")
async def generate_assessment(
    force_new: bool = Query(False, description="Force generation of a new assessment even if one exists"),
    current_user: dict = Depends(get_current_user),
):
    """
    Generates (or retrieves existing) personalized assessment:
    - 25 Aptitude questions (general reasoning, difficulty scaled by experience)
    - 25 Technical MCQs (personalized to resume skills)
    - 15 Coding problems (LeetCode-style, adapted to candidate's background)

    If a Pending or In-Progress assessment exists for the current resume version,
    it is returned immediately without regeneration.

    Set force_new=true to regenerate from scratch (e.g. after resume update).
    """
    user_id = str(current_user["_id"])
    result, status_code = ResumeController.generate_assessment(user_id, force_new=force_new)
    return JSONResponse(content=result, status_code=status_code)


@router.delete("", summary="Delete resume and candidate profile")
async def delete_resume(
    current_user: dict = Depends(get_current_user),
):
    """
    Deletes the candidate's resume file reference and skill profile.
    The candidate can then upload a new resume.
    Active in-progress assessments are NOT affected.
    """
    user_id = str(current_user["_id"])
    result, status_code = ResumeController.delete_resume(user_id)
    return JSONResponse(content=result, status_code=status_code)
