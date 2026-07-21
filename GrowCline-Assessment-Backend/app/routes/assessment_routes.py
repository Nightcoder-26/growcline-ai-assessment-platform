"""
Assessment Routes Module
Registers endpoints for Assessment creation, listing, retrieval, starting, and submitting.
Supports both /api/assessment (singular) and /api/assessments (plural).
"""

from typing import Optional
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

try:
    from controllers.assessment_controller import AssessmentController
    from schemas.request_models import (
        AssessmentCreateRequest, AssessmentUpdateRequest, AssessmentSubmitRequest
    )
except ImportError:
    from app.controllers.assessment_controller import AssessmentController
    from app.schemas.request_models import (
        AssessmentCreateRequest, AssessmentUpdateRequest, AssessmentSubmitRequest
    )

# Singular prefix router (primary)
router = APIRouter(prefix="/api/assessment", tags=["Assessment"])

# Plural prefix router (alias)
router_plural = APIRouter(prefix="/api/assessments", tags=["Assessments"])


def _register(r: APIRouter, primary: bool = True):
    """Register all assessment routes on a given router."""

    @r.post("", summary="Create an assessment", include_in_schema=primary)
    @r.post("/", include_in_schema=False)
    async def create_assessment(body: AssessmentCreateRequest):
        result, status_code = AssessmentController.create_assessment(body.model_dump())
        return JSONResponse(content=result, status_code=status_code)

    @r.get("", summary="Get all assessments", include_in_schema=primary)
    @r.get("/", include_in_schema=False)
    async def get_all_assessments(
        userId: Optional[str] = Query(None),
        user_id: Optional[str] = Query(None),
    ):
        uid = userId or user_id
        result, status_code = AssessmentController.get_all_assessments(user_id=uid)
        return JSONResponse(content=result, status_code=status_code)

    @r.post("/{assessment_id}/start", summary="Start an assessment session", include_in_schema=primary)
    async def start_assessment(assessment_id: str):
        result, status_code = AssessmentController.start_assessment(assessment_id)
        return JSONResponse(content=result, status_code=status_code)

    @r.post("/{assessment_id}/submit", summary="Submit assessment answers", include_in_schema=primary)
    async def submit_assessment(assessment_id: str, body: AssessmentSubmitRequest):
        result, status_code = AssessmentController.submit_assessment(assessment_id, body.model_dump())
        return JSONResponse(content=result, status_code=status_code)

    @r.get("/{assessment_id}", summary="Get assessment by ID", include_in_schema=primary)
    async def get_assessment_by_id(assessment_id: str):
        result, status_code = AssessmentController.get_assessment_by_id(assessment_id)
        return JSONResponse(content=result, status_code=status_code)

    @r.put("/{assessment_id}", summary="Update assessment by ID", include_in_schema=primary)
    async def update_assessment(assessment_id: str, body: AssessmentUpdateRequest):
        result, status_code = AssessmentController.update_assessment(assessment_id, body.model_dump(exclude_none=True))
        return JSONResponse(content=result, status_code=status_code)

    @r.delete("/{assessment_id}", summary="Delete assessment by ID", include_in_schema=primary)
    async def delete_assessment(assessment_id: str):
        result, status_code = AssessmentController.delete_assessment(assessment_id)
        return JSONResponse(content=result, status_code=status_code)


_register(router, primary=True)
_register(router_plural, primary=False)

# Backward-compatible aliases
assessment_bp = router
assessments_plural_bp = router_plural