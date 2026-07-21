"""
Aptitude Routes Module
Registers endpoints for Aptitude CRUD, test generation, and submission.
"""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

try:
    from controllers.aptitude_controller import AptitudeController
except ImportError:
    from app.controllers.aptitude_controller import AptitudeController

router = APIRouter(prefix="/api/aptitude", tags=["Aptitude"])


# Root CRUD routes
@router.post("")
@router.post("/")
@router.post("/questions")
async def create_question(request: Request):
    try:
        data = await request.json()
    except Exception:
        data = {}
    result, status_code = AptitudeController.create_question(data)
    return JSONResponse(content=result, status_code=status_code)


@router.get("")
@router.get("/")
@router.get("/questions")
async def get_all_questions():
    result, status_code = AptitudeController.get_all_questions()
    return JSONResponse(content=result, status_code=status_code)


# Assessment Generation & Submission (must be before /{question_id} to avoid conflict)
@router.post("/generate")
async def generate_assessment(request: Request):
    try:
        data = await request.json()
    except Exception:
        data = {}
    result, status_code = AptitudeController.generate_assessment(data)
    return JSONResponse(content=result, status_code=status_code)


@router.post("/submit")
async def submit_assessment(request: Request):
    try:
        data = await request.json()
    except Exception:
        data = {}
    result, status_code = AptitudeController.submit_assessment(data)
    return JSONResponse(content=result, status_code=status_code)


# Single Question by ID
@router.get("/{question_id}")
@router.get("/questions/{question_id}")
async def get_question_by_id(question_id: str):
    result, status_code = AptitudeController.get_question_by_id(question_id)
    return JSONResponse(content=result, status_code=status_code)


@router.put("/{question_id}")
@router.put("/questions/{question_id}")
async def update_question(question_id: str, request: Request):
    try:
        data = await request.json()
    except Exception:
        data = {}
    result, status_code = AptitudeController.update_question(question_id, data)
    return JSONResponse(content=result, status_code=status_code)


@router.delete("/{question_id}")
@router.delete("/questions/{question_id}")
async def delete_question(question_id: str):
    result, status_code = AptitudeController.delete_question(question_id)
    return JSONResponse(content=result, status_code=status_code)


# Backward-compatible alias
aptitude_bp = router