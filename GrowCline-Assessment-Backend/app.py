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


# ── Team A: Migrated Flask → FastAPI Routers ────────────────────────────────
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

app.include_router(auth_router)
app.include_router(technical_router)
app.include_router(result_router)
app.include_router(analytics_router)
app.include_router(aptitude_router)
app.include_router(assessment_router)
app.include_router(assessment_plural_router)
app.include_router(coding_router)
app.include_router(user_router)
# ────────────────────────────────────────────────────────────────────────────

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