"""
Aptitude Routes Module
Registers endpoints for Aptitude CRUD, test generation, and submission.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

try:
    from app.controllers.aptitude_controller import AptitudeController
    from schemas.request_models import (
        AptitudeQuestionRequest, AptitudeUpdateRequest,
        AptitudeGenerateRequest, AptitudeSubmitRequest
    )
except ImportError:
    from app.controllers.aptitude_controller import AptitudeController
    from app.schemas.request_models import (
        AptitudeQuestionRequest, AptitudeUpdateRequest,
        AptitudeGenerateRequest, AptitudeSubmitRequest
    )

router = APIRouter(prefix="/api/aptitude", tags=["Aptitude"])


@router.post("", summary="Create an aptitude question")
@router.post("/", include_in_schema=False)
@router.post("/questions", include_in_schema=False)
async def create_question(body: AptitudeQuestionRequest):
    result, status_code = AptitudeController.create_question(body.model_dump())
    return JSONResponse(content=result, status_code=status_code)


@router.get("", summary="Get all aptitude questions")
@router.get("/", include_in_schema=False)
@router.get("/questions", include_in_schema=False)
async def get_all_questions():
    result, status_code = AptitudeController.get_all_questions()
    return JSONResponse(content=result, status_code=status_code)


@router.post("/generate", summary="Generate a random aptitude assessment")
async def generate_assessment(body: AptitudeGenerateRequest):
    result, status_code = AptitudeController.generate_assessment(body.model_dump())
    return JSONResponse(content=result, status_code=status_code)


@router.post("/submit", summary="Submit aptitude assessment answers")
async def submit_assessment(body: AptitudeSubmitRequest):
    result, status_code = AptitudeController.submit_assessment(body.model_dump())
    return JSONResponse(content=result, status_code=status_code)


@router.get("/{question_id}", summary="Get aptitude question by ID")
async def get_question_by_id(question_id: str):
    result, status_code = AptitudeController.get_question_by_id(question_id)
    return JSONResponse(content=result, status_code=status_code)


@router.put("/{question_id}", summary="Update aptitude question by ID")
async def update_question(question_id: str, body: AptitudeUpdateRequest):
    result, status_code = AptitudeController.update_question(question_id, body.model_dump(exclude_none=True))
    return JSONResponse(content=result, status_code=status_code)


@router.delete("/{question_id}", summary="Delete aptitude question by ID")
async def delete_question(question_id: str):
    result, status_code = AptitudeController.delete_question(question_id)
    return JSONResponse(content=result, status_code=status_code)


# Backward-compatible alias
aptitude_bp = router