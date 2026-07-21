"""
Result Routes Module
Registers endpoints for Assessment Results under /api/results.
"""

from typing import Optional
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

try:
    from controllers.result_controller import ResultController
    from schemas.request_models import SaveResultRequest, UpdateResultRequest
except ImportError:
    from app.controllers.result_controller import ResultController
    from app.schemas.request_models import SaveResultRequest, UpdateResultRequest

router = APIRouter(prefix="/api/results", tags=["Results"])


@router.post("/calculate", summary="Calculate and save an assessment result")
async def calculate_result(body: SaveResultRequest):
    result, status_code = ResultController.calculate_result(body.model_dump())
    return JSONResponse(content=result, status_code=status_code)


@router.post("", summary="Save an assessment result")
@router.post("/", include_in_schema=False)
async def save_result(body: SaveResultRequest):
    result, status_code = ResultController.save_result(body.model_dump())
    return JSONResponse(content=result, status_code=status_code)


@router.get("", summary="Get all results")
@router.get("/", include_in_schema=False)
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


@router.get("/candidate/{user_id}", summary="Get all results for a candidate")
async def get_candidate_results(user_id: str):
    result, status_code = ResultController.get_candidate_results(user_id)
    return JSONResponse(content=result, status_code=status_code)


@router.get("/assessment/{assessment_id}", summary="Get all results for an assessment")
async def get_assessment_result(assessment_id: str):
    result, status_code = ResultController.get_assessment_result(assessment_id)
    return JSONResponse(content=result, status_code=status_code)


@router.get("/{result_id}", summary="Get result by ID")
async def get_result_by_id(result_id: str):
    result, status_code = ResultController.get_result_by_id(result_id)
    return JSONResponse(content=result, status_code=status_code)


@router.put("/{result_id}", summary="Update result by ID")
async def update_result(result_id: str, body: UpdateResultRequest):
    result, status_code = ResultController.update_result(result_id, body.model_dump(exclude_none=True))
    return JSONResponse(content=result, status_code=status_code)


@router.delete("/{result_id}", summary="Delete result by ID")
async def delete_result(result_id: str):
    result, status_code = ResultController.delete_result(result_id)
    return JSONResponse(content=result, status_code=status_code)


# Backward-compatible alias
result_bp = router