"""
Coding Routes Module
Registers endpoints for Coding Assessment CRUD, test generation, and submission.
"""

from typing import Optional
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

try:
    from app.controllers.coding_controller import CodingController
    from schemas.request_models import (
        CodingQuestionRequest, CodingUpdateRequest,
        CodingGenerateRequest, CodingSubmitRequest
    )
except ImportError:
    from app.controllers.coding_controller import CodingController
    from app.schemas.request_models import (
        CodingQuestionRequest, CodingUpdateRequest,
        CodingGenerateRequest, CodingSubmitRequest
    )

router = APIRouter(prefix="/api/coding", tags=["Coding"])


@router.post("", summary="Create a coding question")
@router.post("/", include_in_schema=False)
@router.post("/questions", include_in_schema=False)
async def create_question(body: CodingQuestionRequest):
    result, status_code = CodingController.create_question(body.model_dump())
    return JSONResponse(content=result, status_code=status_code)


@router.get("", summary="Get all coding questions")
@router.get("/", include_in_schema=False)
@router.get("/questions", include_in_schema=False)
async def get_all_questions(
    programmingLanguage: Optional[str] = Query(None, description="Filter by programming language"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty: Easy, Medium, Hard"),
):
    result, status_code = CodingController.get_all_questions(
        programmingLanguage=programmingLanguage, difficulty=difficulty
    )
    return JSONResponse(content=result, status_code=status_code)


@router.post("/generate", summary="Generate a random coding assessment")
async def generate_assessment(body: CodingGenerateRequest):
    result, status_code = CodingController.generate_assessment(body.model_dump())
    return JSONResponse(content=result, status_code=status_code)


@router.post("/submit", summary="Submit coding assessment answers")
async def submit_assessment(body: CodingSubmitRequest):
    result, status_code = CodingController.submit_assessment(body.model_dump())
    return JSONResponse(content=result, status_code=status_code)


@router.get("/{question_id}", summary="Get coding question by ID")
async def get_question_by_id(question_id: str):
    result, status_code = CodingController.get_question_by_id(question_id)
    return JSONResponse(content=result, status_code=status_code)


@router.put("/{question_id}", summary="Update coding question by ID")
async def update_question(question_id: str, body: CodingUpdateRequest):
    result, status_code = CodingController.update_question(question_id, body.model_dump(exclude_none=True))
    return JSONResponse(content=result, status_code=status_code)


@router.delete("/{question_id}", summary="Delete coding question by ID")
async def delete_question(question_id: str):
    result, status_code = CodingController.delete_question(question_id)
    return JSONResponse(content=result, status_code=status_code)


# Backward-compatible alias
coding_bp = router