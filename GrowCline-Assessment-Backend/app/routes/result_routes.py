"""
Result Routes Module
Registers endpoints for Assessment Results under /api/results.
"""

from typing import Optional
from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse

try:
    from controllers.result_controller import ResultController
except ImportError:
    from app.controllers.result_controller import ResultController

router = APIRouter(prefix="/api/results", tags=["Results"])


# Calculate / Save Assessment Result (POST /)
@router.post("/calculate")
async def calculate_result(request: Request):
    try:
        data = await request.json()
    except Exception:
        data = {}
    result, status_code = ResultController.calculate_result(data)
    return JSONResponse(content=result, status_code=status_code)


@router.post("")
@router.post("/")
async def save_result(request: Request):
    try:
        data = await request.json()
    except Exception:
        data = {}
    result, status_code = ResultController.save_result(data)
    return JSONResponse(content=result, status_code=status_code)


# Get All Results (GET /)
@router.get("")
@router.get("/")
async def get_all_results(
    userId: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    assessmentId: Optional[str] = Query(None),
    assessment_id: Optional[str] = Query(None),
):
    uid = userId or user_id
    aid = assessmentId or assessment_id
    result, status_code = ResultController.get_all_results(user_id=uid, assessment_id=aid)
    return JSONResponse(content=result, status_code=status_code)


# Get Candidate Result History (must be before /{result_id} to avoid conflict)
@router.get("/candidate/{user_id}")
async def get_candidate_results(user_id: str):
    result, status_code = ResultController.get_candidate_results(user_id)
    return JSONResponse(content=result, status_code=status_code)


# Get Assessment Result (must be before /{result_id} to avoid conflict)
@router.get("/assessment/{assessment_id}")
async def get_assessment_result(assessment_id: str):
    result, status_code = ResultController.get_assessment_result(assessment_id)
    return JSONResponse(content=result, status_code=status_code)


# Get Result By ID
@router.get("/{result_id}")
async def get_result_by_id(result_id: str):
    result, status_code = ResultController.get_result_by_id(result_id)
    return JSONResponse(content=result, status_code=status_code)


# Delete Result
@router.delete("/{result_id}")
async def delete_result(result_id: str):
    result, status_code = ResultController.delete_result(result_id)
    return JSONResponse(content=result, status_code=status_code)


# Backward-compatible alias
result_bp = router