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
    coding_bp,
)

app.register_blueprint(auth_bp)
app.register_blueprint(technical_bp)
app.register_blueprint(result_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(aptitude_bp)
app.register_blueprint(assessment_bp)
app.register_blueprint(coding_bp)



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
        debug=Config.DEBUG
    )