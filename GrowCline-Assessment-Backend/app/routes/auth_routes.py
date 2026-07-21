"""
Authentication Routes Module
Registers endpoints for registration, login, and profile operations under /api/auth.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

try:
    from controllers.auth_controller import AuthController
    from middleware.auth_middleware import get_current_user
except ImportError:
    from app.controllers.auth_controller import AuthController
    from app.middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Auth"])


# Register User
@router.post("/register")
async def register(request: Request):
    data = await request.json() if request.headers.get("content-type", "").startswith("application/json") else {}
    try:
        data = await request.json()
    except Exception:
        data = {}
    result, status_code = AuthController.register(data)
    return JSONResponse(content=result, status_code=status_code)


# Login User
@router.post("/login")
async def login(request: Request):
    try:
        data = await request.json()
    except Exception:
        data = {}
    result, status_code = AuthController.login(data)
    return JSONResponse(content=result, status_code=status_code)


# Get Profile (Protected Route)
@router.get("/profile")
async def get_profile_protected(current_user: dict = Depends(get_current_user)):
    result, status_code = AuthController.get_profile(current_user=current_user)
    return JSONResponse(content=result, status_code=status_code)


# Get Profile by ID (Unprotected - for admin use)
@router.get("/profile/{user_id}")
async def get_profile_by_id(user_id: str):
    result, status_code = AuthController.get_profile(user_id=user_id)
    return JSONResponse(content=result, status_code=status_code)


# Update Profile (Protected Route)
@router.put("/profile")
async def update_profile_protected(request: Request, current_user: dict = Depends(get_current_user)):
    try:
        data = await request.json()
    except Exception:
        data = {}
    result, status_code = AuthController.update_profile(data=data, current_user=current_user)
    return JSONResponse(content=result, status_code=status_code)


# Update Profile by ID
@router.put("/profile/{user_id}")
async def update_profile_by_id(user_id: str, request: Request):
    try:
        data = await request.json()
    except Exception:
        data = {}
    result, status_code = AuthController.update_profile(data=data, user_id=user_id)
    return JSONResponse(content=result, status_code=status_code)


# Change Password (Protected Route)
@router.put("/change-password")
async def change_password(request: Request, current_user: dict = Depends(get_current_user)):
    try:
        data = await request.json()
    except Exception:
        data = {}
    result, status_code = AuthController.change_password(data=data, current_user=current_user)
    return JSONResponse(content=result, status_code=status_code)


# Keep backward-compatible Blueprint export for existing imports
auth_bp = router