"""
Main FastAPI Application Entrypoint for GrowCline Assessment & Interview Intelligence Platform.
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config.database import Database
from app.config.settings import Config
from app.services.google_drive_service import GoogleDriveService
from app.routes import (
    auth_router,
    technical_router,
    result_router,
    analytics_router,
    aptitude_router,
    assessment_router,
    assessment_plural_router,
    coding_router,
    user_router,
)
from app.routes.recording_routes import router as recording_router
from app.routes.proctoring_routes import router as proctoring_router
from app.routes.cheating_detection_routes import router as cheating_router
from app.routes.interview_analytics_routes import router as interview_analytics_router
from app.routes.interview_routes import router as interview_router
from app.routes.interview_session_routes import (
    router as interview_session_router,
    analytics_router as interview_session_analytics_router,
)
from app.routes.drive_routes import router as drive_router
from app.routes.resume_routes import router as resume_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for application startup and shutdown tasks."""
    # Startup
    try:
        Config.validate_google_drive_config()
        GoogleDriveService.verify_connection()
    except Exception as error:
        logger.warning(f"Google Drive initialization notice: {error}")
    yield
    # Shutdown


app = FastAPI(
    title="GrowCline AI Assessment & Interview Intelligence Platform",
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect MongoDB Atlas
Database.connect()


# Standardize HTTPExceptions format: {"success": False, "message": "..."}
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail
        }
    )


# Register all API routers
app.include_router(auth_router)
app.include_router(technical_router)
app.include_router(result_router)
app.include_router(analytics_router)
app.include_router(aptitude_router)
app.include_router(assessment_router)
app.include_router(assessment_plural_router)
app.include_router(coding_router)
app.include_router(user_router)
app.include_router(recording_router)
app.include_router(proctoring_router)
app.include_router(cheating_router)
app.include_router(interview_analytics_router)
app.include_router(interview_router)
app.include_router(interview_session_router)
app.include_router(interview_session_analytics_router)
app.include_router(drive_router)
app.include_router(resume_router)


# ── Local file uploads (fallback when S3 is not configured) ─────────────────
_upload_dir = os.path.join(os.path.dirname(__file__), Config.UPLOAD_FOLDER)
os.makedirs(_upload_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=_upload_dir), name="uploads")
# ────────────────────────────────────────────────────────────────────────────


@app.get("/", summary="Health check endpoint")
async def home():
    return {
        "success": True,
        "message": "GrowCline Backend is Running 🚀"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=Config.HOST,
        port=Config.PORT,
    )