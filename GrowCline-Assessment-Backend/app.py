from flask import Flask
from flask_cors import CORS

from app.config.database import Database
from app.config.settings import Config

app = Flask(__name__)
app.config.from_object(Config)

CORS(app)

# Connect MongoDB
Database.connect()

# ── Team B: Video Recording Module ──────────────────────────────────────────
from app.routes.recording_routes import recording_bp
app.register_blueprint(recording_bp)
# ────────────────────────────────────────────────────────────────────────────


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