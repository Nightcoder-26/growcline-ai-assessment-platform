"""
Technical Routes Module
Registers endpoints for Technical Assessment CRUD, test generation, and submission.
"""

from typing import Optional
from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse

try:
    from controllers.technical_controller import TechnicalController
except ImportError:
    from app.controllers.technical_controller import TechnicalController

router = APIRouter(prefix="/api/technical", tags=["Technical"])


# Root CRUD routes
@router.post("")
@router.post("/")
@router.post("/questions")
async def create_question(request: Request):
    try:
        data = await request.json()
    except Exception:
        data = {}
    result, status_code = TechnicalController.create_question(data)
    return JSONResponse(content=result, status_code=status_code)


@router.get("")
@router.get("/")
@router.get("/questions")
async def get_all_questions(
    technology: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
):
    result, status_code = TechnicalController.get_all_questions(
        technology=technology,
        category=category,
        difficulty=difficulty,
    )
    return JSONResponse(content=result, status_code=status_code)


# Assessment Generation & Submission (must be before /{question_id} to avoid conflict)
@router.post("/generate")
async def generate_assessment(request: Request):
    try:
        data = await request.json()
    except Exception:
        data = {}
    result, status_code = TechnicalController.generate_assessment(data)
    return JSONResponse(content=result, status_code=status_code)


@router.post("/submit")
async def submit_assessment(request: Request):
    try:
        data = await request.json()
    except Exception:
        data = {}
    result, status_code = TechnicalController.submit_assessment(data)
    return JSONResponse(content=result, status_code=status_code)


# Single Question by ID
@router.get("/{question_id}")
@router.get("/questions/{question_id}")
async def get_question_by_id(question_id: str):
    result, status_code = TechnicalController.get_question_by_id(question_id)
    return JSONResponse(content=result, status_code=status_code)


@router.put("/{question_id}")
@router.put("/questions/{question_id}")
async def update_question(question_id: str, request: Request):
    try:
        data = await request.json()
    except Exception:
        data = {}
    result, status_code = TechnicalController.update_question(question_id, data)
    return JSONResponse(content=result, status_code=status_code)


@router.delete("/{question_id}")
@router.delete("/questions/{question_id}")
async def delete_question(question_id: str):
    result, status_code = TechnicalController.delete_question(question_id)
    return JSONResponse(content=result, status_code=status_code)


# Backward-compatible alias
technical_bp = router