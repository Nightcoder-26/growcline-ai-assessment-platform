"""
Analytics Routes Module
Registers endpoints for Analytics dashboards, user trends, and candidate analytics.
"""

from typing import Optional
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

try:
    from controllers.analytics_controller import AnalyticsController
    from schemas.request_models import DashboardAnalyticsRequest
except ImportError:
    from app.controllers.analytics_controller import AnalyticsController
    from app.schemas.request_models import DashboardAnalyticsRequest

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/dashboard", summary="Get global dashboard analytics")
async def get_dashboard():
    result, status_code = AnalyticsController.get_dashboard_get()
    return JSONResponse(content=result, status_code=status_code)


@router.post("/dashboard", summary="Save dashboard analytics record")
async def post_dashboard(body: DashboardAnalyticsRequest):
    result, status_code = AnalyticsController.get_dashboard_post(body.model_dump(exclude_none=True))
    return JSONResponse(content=result, status_code=status_code)


@router.get("/dashboard/{user_id}", summary="Get dashboard analytics for a user")
async def get_dashboard_by_user(user_id: str):
    result, status_code = AnalyticsController.get_dashboard_get(user_id=user_id)
    return JSONResponse(content=result, status_code=status_code)


@router.post("/dashboard/{user_id}", summary="Save dashboard analytics for a user")
async def post_dashboard_by_user(user_id: str, body: DashboardAnalyticsRequest):
    result, status_code = AnalyticsController.get_dashboard_post(body.model_dump(exclude_none=True), user_id=user_id)
    return JSONResponse(content=result, status_code=status_code)


@router.get("/candidate/{user_id}", summary="Get analytics for a candidate")
async def get_candidate_analytics(user_id: str):
    result, status_code = AnalyticsController.get_candidate_analytics(user_id)
    return JSONResponse(content=result, status_code=status_code)


@router.get("/assessment/{assessment_id}", summary="Get analytics for an assessment")
async def get_assessment_analytics(assessment_id: str):
    result, status_code = AnalyticsController.get_assessment_analytics(assessment_id)
    return JSONResponse(content=result, status_code=status_code)


@router.get("/performance-trends", summary="Get overall performance trends")
async def get_performance_trends():
    result, status_code = AnalyticsController.get_performance_trends()
    return JSONResponse(content=result, status_code=status_code)


@router.get("/skill-analysis", summary="Get global skill analysis averages")
async def get_skill_analysis():
    result, status_code = AnalyticsController.get_skill_analysis()
    return JSONResponse(content=result, status_code=status_code)


@router.get("/skill-analysis/{user_id}", summary="Get skill analysis for a user")
async def get_skill_analysis_by_user(user_id: str):
    result, status_code = AnalyticsController.get_skill_analysis(user_id=user_id)
    return JSONResponse(content=result, status_code=status_code)


# Backward-compatible alias
analytics_bp = router