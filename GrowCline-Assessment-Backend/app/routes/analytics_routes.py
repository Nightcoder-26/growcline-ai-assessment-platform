from flask import Blueprint

try:
    from controllers.analytics_controller import AnalyticsController
except ImportError:
    from app.controllers.analytics_controller import AnalyticsController

analytics_bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")

# Dashboard Analytics
analytics_bp.route("/dashboard", methods=["GET"])(AnalyticsController.get_dashboard)

# Candidate Analytics
analytics_bp.route("/candidate/<string:user_id>", methods=["GET"])(AnalyticsController.get_candidate_analytics)

# Assessment Analytics
analytics_bp.route("/assessment/<string:assessment_id>", methods=["GET"])(AnalyticsController.get_assessment_analytics)

# Performance Trends
analytics_bp.route("/performance-trends", methods=["GET"])(AnalyticsController.get_performance_trends)

# Skill Analysis
analytics_bp.route("/skill-analysis/<string:user_id>", methods=["GET"])(AnalyticsController.get_skill_analysis)