from .auth_routes import auth_bp
from .technical_routes import technical_bp
from .result_routes import result_bp
from .analytics_routes import analytics_bp
from .aptitude_routes import aptitude_bp
from .assessment_routes import assessment_bp, assessments_plural_bp
from .coding_routes import coding_bp
from .user_routes import user_bp

__all__ = [
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

