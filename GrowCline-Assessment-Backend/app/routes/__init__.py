from .auth_routes import router as auth_router, auth_bp
from .technical_routes import router as technical_router, technical_bp
from .result_routes import router as result_router, result_bp
from .analytics_routes import router as analytics_router, analytics_bp
from .aptitude_routes import router as aptitude_router, aptitude_bp
from .assessment_routes import router as assessment_router, router_plural as assessment_plural_router, assessment_bp, assessments_plural_bp
from .coding_routes import router as coding_router, coding_bp
from .user_routes import router as user_router, user_bp

__all__ = [
    # FastAPI APIRouter objects (used by app.py include_router)
    "auth_router",
    "technical_router",
    "result_router",
    "analytics_router",
    "aptitude_router",
    "assessment_router",
    "assessment_plural_router",
    "coding_router",
    "user_router",

    # Backward-compatible Blueprint aliases
    "auth_bp",
    "technical_bp",
    "result_bp",
    "analytics_bp",
    "aptitude_bp",
    "assessment_bp",
    "assessments_plural_bp",
    "coding_bp",
    "user_bp",
]
