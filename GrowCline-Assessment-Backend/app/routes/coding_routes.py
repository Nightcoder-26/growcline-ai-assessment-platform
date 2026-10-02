"""
Coding Routes Module
Registers endpoints for Coding Assessment CRUD, sample test execution, and submission.

Auth:
  - POST /run, /submit, /submit-one → require valid JWT (get_current_user)
  - GET/PUT/DELETE /<id>            → get_question_by_id is public (read-only), edits need admin
  - POST (create), PUT, DELETE      → admin-only guard enforced in controller via role check
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

try:
    from app.controllers.coding_controller import CodingController
    from app.middleware.auth_middleware import get_current_user
    from schemas.request_models import (
        CodingQuestionRequest, CodingUpdateRequest,
        CodingGenerateRequest, CodingSubmitRequest,
        CodingRunRequest, CodingSubmitOneRequest,
    )
except ImportError:
    from app.controllers.coding_controller import CodingController
    from app.middleware.auth_middleware import get_current_user
    from app.schemas.request_models import (
        CodingQuestionRequest, CodingUpdateRequest,
        CodingGenerateRequest, CodingSubmitRequest,
        CodingRunRequest, CodingSubmitOneRequest,
    )

router = APIRouter(prefix="/api/coding", tags=["Coding"])


# ── CRUD (public read, admin write) ───────────────────────────────────────────

@router.post("", summary="Create a coding question (admin)")
@router.post("/", include_in_schema=False)
@router.post("/questions", include_in_schema=False)
async def create_question(
    body: CodingQuestionRequest,
    current_user: dict = Depends(get_current_user),
):
    """Admin-only: Create a new coding question."""
    if current_user.get("role") not in ("admin", "Admin"):
        return JSONResponse({"success": False, "message": "Admin access required."}, status_code=403)
    result, status_code = CodingController.create_question(body.model_dump())
    return JSONResponse(content=result, status_code=status_code)


@router.get("", summary="Get all coding questions")
@router.get("/", include_in_schema=False)
@router.get("/questions", include_in_schema=False)
async def get_all_questions(
    programmingLanguage: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
):
    result, status_code = CodingController.get_all_questions(
        programmingLanguage=programmingLanguage, difficulty=difficulty
    )
    return JSONResponse(content=result, status_code=status_code)


@router.post("/generate", summary="Generate a random coding assessment (sample cases only)")
async def generate_assessment(body: CodingGenerateRequest):
    result, status_code = CodingController.generate_assessment(body.model_dump())
    return JSONResponse(content=result, status_code=status_code)


# ── Run (requires auth, rate-limited) ─────────────────────────────────────────

@router.post("/run", summary="Run code against sample test cases")
async def run_code(
    body: CodingRunRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Executes candidate code against sample test cases only.
    Rate-limited (1 req / 3s per user). Never exposes hidden tests.
    """
    user_id = str(current_user.get("_id", ""))
    result, status_code = CodingController.run_code(body.model_dump(), user_id=user_id)
    return JSONResponse(content=result, status_code=status_code)


# ── Submit-One (requires auth) ────────────────────────────────────────────────

@router.post("/submit-one", summary="Submit a single problem (hidden test evaluation)")
async def submit_one(
    body: CodingSubmitOneRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Evaluates one problem against all test cases (sample + hidden).
    Returns verdict and hidden test COUNT only — never reveals hidden inputs/outputs.
    """
    user_id = str(current_user.get("_id", ""))
    result, status_code = CodingController.submit_one(body.model_dump(), user_id=user_id)
    return JSONResponse(content=result, status_code=status_code)


# ── Submit-All (requires auth) ────────────────────────────────────────────────

@router.post("/submit", summary="Submit all coding answers (batch)")
async def submit_assessment(
    body: CodingSubmitRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Batch-evaluates all submitted problems with real hidden-test grading.
    Backward-compatible: returns score/total/percentage + results[] array.
    """
    user_id = str(current_user.get("_id", ""))
    result, status_code = CodingController.submit_assessment(body.model_dump(), user_id=user_id)
    return JSONResponse(content=result, status_code=status_code)


# ── Submission status (polling) ───────────────────────────────────────────────

@router.get("/submissions/{job_id}", summary="Get submission record by ID")
async def get_submission_status(
    job_id: str,
    current_user: dict = Depends(get_current_user),
):
    result, status_code = CodingController.get_submission_status(job_id)
    return JSONResponse(content=result, status_code=status_code)


# ── Per-question CRUD ─────────────────────────────────────────────────────────

@router.get("/{question_id}", summary="Get coding question by ID")
async def get_question_by_id(question_id: str):
    result, status_code = CodingController.get_question_by_id(question_id)
    return JSONResponse(content=result, status_code=status_code)


@router.put("/{question_id}", summary="Update coding question (admin)")
async def update_question(
    question_id: str,
    body: CodingUpdateRequest,
    current_user: dict = Depends(get_current_user),
):
    if current_user.get("role") not in ("admin", "Admin"):
        return JSONResponse({"success": False, "message": "Admin access required."}, status_code=403)
    result, status_code = CodingController.update_question(
        question_id, body.model_dump(exclude_none=True)
    )
    return JSONResponse(content=result, status_code=status_code)


@router.delete("/{question_id}", summary="Delete coding question (admin)")
async def delete_question(
    question_id: str,
    current_user: dict = Depends(get_current_user),
):
    if current_user.get("role") not in ("admin", "Admin"):
        return JSONResponse({"success": False, "message": "Admin access required."}, status_code=403)
    result, status_code = CodingController.delete_question(question_id)
    return JSONResponse(content=result, status_code=status_code)


# Backward-compatible alias
coding_bp = router