from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

from app.config.database import Database
from app.config.settings import Config

app = FastAPI(title="GrowCline AI Assessment & Interview Intelligence Platform")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect MongoDB
Database.connect()


# Standardise HTTPExceptions to match Team A's error response format: {"success": False, "message": "..."}
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail
        }
    )


# Register Route Blueprints (Teammates' Flask blueprints - dummy method to avoid crashes)
app.register_blueprint = lambda *args, **kwargs: None

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

# ── Team B: Video Recording Module ──────────────────────────────────────────
from app.routes.recording_routes import router as recording_router
app.include_router(recording_router)
# ────────────────────────────────────────────────────────────────────────────

# ── Team B: Live Proctoring Module ──────────────────────────────────────────
from app.routes.proctoring_routes import router as proctoring_router
app.include_router(proctoring_router)
# ────────────────────────────────────────────────────────────────────────────

# ── Team B: Cheating Detection Engine Module ────────────────────────────────
from app.routes.cheating_detection_routes import router as cheating_router
app.include_router(cheating_router)
# ────────────────────────────────────────────────────────────────────────────

# ── Team B: Interview Analytics Module ──────────────────────────────────────
from app.routes.interview_analytics_routes import router as interview_analytics_router
app.include_router(interview_analytics_router)
# ────────────────────────────────────────────────────────────────────────────

# ── Team B: AI Interview Module ──────────────────────────────────────────────
from app.routes.interview_routes import router as interview_router
app.include_router(interview_router)
# ────────────────────────────────────────────────────────────────────────────


@app.get("/")
async def home():
    return {
        "success": True,
        "message": "GrowCline Backend is Running 🚀"
    }


if __name__ == "__main__":
    import uvicorn
    # Pass the 'app' object directly to avoid namespace collision with the 'app/' directory
    uvicorn.run(
        app,
        host=Config.HOST,
        port=Config.PORT,
    )