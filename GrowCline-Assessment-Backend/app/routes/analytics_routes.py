"""
Analytics Routes Module
Registers endpoints for Analytics dashboards, user trends, and candidate analytics.
"""

from typing import Optional
from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse

try:
    from controllers.analytics_controller import AnalyticsController
except ImportError:
    from app.controllers.analytics_controller import AnalyticsController

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


# Dashboard Analytics — Global (GET & POST without user_id)
@router.get("/dashboard")
async def get_dashboard():
    result, status_code = AnalyticsController.get_dashboard_get()
    return JSONResponse(content=result, status_code=status_code)


@router.post("/dashboard")
async def post_dashboard(request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    result, status_code = AnalyticsController.get_dashboard_post(payload)
    return JSONResponse(content=result, status_code=status_code)


# Dashboard Analytics — Per User ID (GET & POST with user_id)
@router.get("/dashboard/{user_id}")
async def get_dashboard_by_user(user_id: str):
    result, status_code = AnalyticsController.get_dashboard_get(user_id=user_id)
    return JSONResponse(content=result, status_code=status_code)


@router.post("/dashboard/{user_id}")
async def post_dashboard_by_user(user_id: str, request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    result, status_code = AnalyticsController.get_dashboard_post(payload, user_id=user_id)
    return JSONResponse(content=result, status_code=status_code)


# Candidate Analytics
@router.get("/candidate/{user_id}")
async def get_candidate_analytics(user_id: str):
    result, status_code = AnalyticsController.get_candidate_analytics(user_id)
    return JSONResponse(content=result, status_code=status_code)


# Assessment Analytics
@router.get("/assessment/{assessment_id}")
async def get_assessment_analytics(assessment_id: str):
    result, status_code = AnalyticsController.get_assessment_analytics(assessment_id)
    return JSONResponse(content=result, status_code=status_code)


# Performance Trends
@router.get("/performance-trends")
async def get_performance_trends():
    result, status_code = AnalyticsController.get_performance_trends()
    return JSONResponse(content=result, status_code=status_code)


# Skill Analysis (Global & Per User ID)
@router.get("/skill-analysis")
async def get_skill_analysis():
    result, status_code = AnalyticsController.get_skill_analysis()
    return JSONResponse(content=result, status_code=status_code)


@router.get("/skill-analysis/{user_id}")
async def get_skill_analysis_by_user(user_id: str):
    result, status_code = AnalyticsController.get_skill_analysis(user_id=user_id)
    return JSONResponse(content=result, status_code=status_code)


# Backward-compatible alias
analytics_bp = router