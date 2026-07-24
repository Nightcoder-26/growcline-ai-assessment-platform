"""
Technical Routes Module
Registers endpoints for Technical Assessment CRUD, test generation, and submission.
"""

from typing import Optional
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

try:
    from app.controllers.technical_controller import TechnicalController
    from schemas.request_models import (
        TechnicalQuestionRequest, TechnicalUpdateRequest,
        TechnicalGenerateRequest, TechnicalSubmitRequest
    )
except ImportError:
    from app.controllers.technical_controller import TechnicalController
    from app.schemas.request_models import (
        TechnicalQuestionRequest, TechnicalUpdateRequest,
        TechnicalGenerateRequest, TechnicalSubmitRequest
    )

router = APIRouter(prefix="/api/technical", tags=["Technical"])


@router.post("", summary="Create a technical question")
@router.post("/", include_in_schema=False)
@router.post("/questions", include_in_schema=False)
async def create_question(body: TechnicalQuestionRequest):
    result, status_code = TechnicalController.create_question(body.model_dump())
    return JSONResponse(content=result, status_code=status_code)


@router.get("", summary="Get all technical questions")
@router.get("/", include_in_schema=False)
@router.get("/questions", include_in_schema=False)
async def get_all_questions(
    technology: Optional[str] = Query(None, description="Filter by technology (e.g. Python)"),
    category: Optional[str] = Query(None, description="Filter by category"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty: Easy, Medium, Hard"),
):
    result, status_code = TechnicalController.get_all_questions(
        technology=technology, category=category, difficulty=difficulty
    )
    return JSONResponse(content=result, status_code=status_code)


@router.post("/generate", summary="Generate a random technical assessment")
async def generate_assessment(body: TechnicalGenerateRequest):
    result, status_code = TechnicalController.generate_assessment(body.model_dump())
    return JSONResponse(content=result, status_code=status_code)


@router.post("/submit", summary="Submit technical assessment answers")
async def submit_assessment(body: TechnicalSubmitRequest):
    result, status_code = TechnicalController.submit_assessment(body.model_dump())
    return JSONResponse(content=result, status_code=status_code)


@router.get("/{question_id}", summary="Get technical question by ID")
async def get_question_by_id(question_id: str):
    result, status_code = TechnicalController.get_question_by_id(question_id)
    return JSONResponse(content=result, status_code=status_code)


@router.put("/{question_id}", summary="Update technical question by ID")
async def update_question(question_id: str, body: TechnicalUpdateRequest):
    result, status_code = TechnicalController.update_question(question_id, body.model_dump(exclude_none=True))
    return JSONResponse(content=result, status_code=status_code)


@router.delete("/{question_id}", summary="Delete technical question by ID")
async def delete_question(question_id: str):
    result, status_code = TechnicalController.delete_question(question_id)
    return JSONResponse(content=result, status_code=status_code)


# Backward-compatible alias
technical_bp = router