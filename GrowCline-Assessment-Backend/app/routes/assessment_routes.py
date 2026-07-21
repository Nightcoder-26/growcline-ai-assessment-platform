"""
Assessment Routes Module
Registers endpoints for Assessment creation, listing, retrieval, starting, and submitting.
Supports both /api/assessment (singular) and /api/assessments (plural).
"""

from typing import Optional
from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse

try:
    from controllers.assessment_controller import AssessmentController
except ImportError:
    from app.controllers.assessment_controller import AssessmentController

# Singular prefix router
router = APIRouter(prefix="/api/assessment", tags=["Assessment"])

# Plural prefix router
router_plural = APIRouter(prefix="/api/assessments", tags=["Assessments"])


def _make_routes(r: APIRouter):
    """Register all assessment routes on a given router."""

    @r.post("")
    @r.post("/")
    async def create_assessment(request: Request):
        try:
            data = await request.json()
        except Exception:
            data = {}
        result, status_code = AssessmentController.create_assessment(data)
        return JSONResponse(content=result, status_code=status_code)

    @r.get("")
    @r.get("/")
    async def get_all_assessments(
        userId: Optional[str] = Query(None),
        user_id: Optional[str] = Query(None),
    ):
        uid = userId or user_id
        result, status_code = AssessmentController.get_all_assessments(user_id=uid)
        return JSONResponse(content=result, status_code=status_code)

    @r.post("/{assessment_id}/start")
    async def start_assessment(assessment_id: str):
        result, status_code = AssessmentController.start_assessment(assessment_id)
        return JSONResponse(content=result, status_code=status_code)

    @r.post("/{assessment_id}/submit")
    async def submit_assessment(assessment_id: str, request: Request):
        try:
            data = await request.json()
        except Exception:
            data = {}
        result, status_code = AssessmentController.submit_assessment(assessment_id, data)
        return JSONResponse(content=result, status_code=status_code)

    @r.get("/{assessment_id}")
    async def get_assessment_by_id(assessment_id: str):
        result, status_code = AssessmentController.get_assessment_by_id(assessment_id)
        return JSONResponse(content=result, status_code=status_code)

    @r.put("/{assessment_id}")
    async def update_assessment(assessment_id: str, request: Request):
        try:
            data = await request.json()
        except Exception:
            data = {}
        result, status_code = AssessmentController.update_assessment(assessment_id, data)
        return JSONResponse(content=result, status_code=status_code)

    @r.delete("/{assessment_id}")
    async def delete_assessment(assessment_id: str):
        result, status_code = AssessmentController.delete_assessment(assessment_id)
        return JSONResponse(content=result, status_code=status_code)


_make_routes(router)
_make_routes(router_plural)

# Backward-compatible aliases
assessment_bp = router
assessments_plural_bp = router_plural