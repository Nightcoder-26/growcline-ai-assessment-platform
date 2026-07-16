"""
Analytics Routes Module
Registers endpoints for Analytics dashboards, user trends, and candidate analytics.
"""

from flask import Blueprint

try:
    from controllers.analytics_controller import AnalyticsController
except ImportError:
    from app.controllers.analytics_controller import AnalyticsController

analytics_bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")

# Dashboard Analytics (Global & Per User ID - supports both GET and POST)
analytics_bp.route("/dashboard", methods=["GET", "POST"])(AnalyticsController.get_dashboard)
analytics_bp.route("/dashboard/<string:user_id>", methods=["GET", "POST"])(AnalyticsController.get_dashboard)

# Candidate Analytics
analytics_bp.route("/candidate/<string:user_id>", methods=["GET"])(AnalyticsController.get_candidate_analytics)

# Assessment Analytics
analytics_bp.route("/assessment/<string:assessment_id>", methods=["GET"])(AnalyticsController.get_assessment_analytics)

# Performance Trends
analytics_bp.route("/performance-trends", methods=["GET"])(AnalyticsController.get_performance_trends)

# Skill Analysis
analytics_bp.route("/skill-analysis", methods=["GET"])(AnalyticsController.get_skill_analysis)
analytics_bp.route("/skill-analysis/<string:user_id>", methods=["GET"])(AnalyticsController.get_skill_analysis)