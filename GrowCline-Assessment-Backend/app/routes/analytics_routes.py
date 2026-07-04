from flask import Blueprint

from app.controllers.analytics_controller import (
    get_dashboard_analytics,
    get_candidate_analytics,
    get_assessment_analytics,
    get_performance_trends,
    get_skill_analysis,
)

analytics_bp = Blueprint(
    "analytics",
    __name__,
    url_prefix="/api/analytics"
)

# Dashboard Analytics
analytics_bp.route(
    "/dashboard",
    methods=["GET"]
)(get_dashboard_analytics)

# Candidate Analytics
analytics_bp.route(
    "/candidate/<string:user_id>",
    methods=["GET"]
)(get_candidate_analytics)

# Assessment Analytics
analytics_bp.route(
    "/assessment/<string:assessment_id>",
    methods=["GET"]
)(get_assessment_analytics)

# Performance Trends
analytics_bp.route(
    "/performance-trends",
    methods=["GET"]
)(get_performance_trends)

# Skill Analysis
analytics_bp.route(
    "/skill-analysis/<string:user_id>",
    methods=["GET"]
)(get_skill_analysis)