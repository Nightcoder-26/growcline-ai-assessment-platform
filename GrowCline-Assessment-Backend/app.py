from flask import Flask
from flask_cors import CORS

from app.config.database import Database
from app.config.settings import Config

app = Flask(__name__)
app.config.from_object(Config)

CORS(app)

# Connect MongoDB
Database.connect()

# Register Route Blueprints
from app.routes import (
    auth_bp,
    technical_bp,
    result_bp,
    analytics_bp,
    aptitude_bp,
    assessment_bp,
    assessments_plural_bp,
    coding_bp,
    user_bp,
)

app.register_blueprint(auth_bp)
app.register_blueprint(technical_bp, url_prefix="/api/technical")
app.register_blueprint(result_bp)
app.register_blueprint(analytics_bp, url_prefix="/api/analytics")
app.register_blueprint(aptitude_bp, url_prefix="/api/aptitude")
app.register_blueprint(assessment_bp, url_prefix="/api/assessment")
app.register_blueprint(assessments_plural_bp, url_prefix="/api/assessments")
app.register_blueprint(coding_bp, url_prefix="/api/coding")
app.register_blueprint(
    user_bp,
    url_prefix="/api/users"
)



@app.route("/")
def home():
    return {
        "success": True,
        "message": "GrowCline Backend is Running 🚀"
    }


if __name__ == "__main__":
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG,
        use_reloader=False
    )