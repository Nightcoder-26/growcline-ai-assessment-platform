"""
Authentication Routes Module
Registers endpoints for registration, login, and profile operations under /api/auth.
"""

from typing import Optional
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

try:
    from controllers.auth_controller import AuthController
    from middleware.auth_middleware import get_current_user
    from schemas.request_models import (
        RegisterRequest, LoginRequest,
        UpdateProfileRequest, ChangePasswordRequest
    )
except ImportError:
    from app.controllers.auth_controller import AuthController
    from app.middleware.auth_middleware import get_current_user
    from app.schemas.request_models import (
        RegisterRequest, LoginRequest,
        UpdateProfileRequest, ChangePasswordRequest
    )

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/register", summary="Register a new user")
async def register(body: RegisterRequest):
    result, status_code = AuthController.register(body.model_dump())
    return JSONResponse(content=result, status_code=status_code)


@router.post("/login", summary="Login with email and password")
async def login(body: LoginRequest):
    result, status_code = AuthController.login(body.model_dump())
    return JSONResponse(content=result, status_code=status_code)


@router.get("/profile", summary="Get authenticated user profile")
async def get_profile_protected(current_user: dict = Depends(get_current_user)):
    result, status_code = AuthController.get_profile(current_user=current_user)
    return JSONResponse(content=result, status_code=status_code)


@router.get("/profile/{user_id}", summary="Get user profile by ID")
async def get_profile_by_id(user_id: str):
    result, status_code = AuthController.get_profile(user_id=user_id)
    return JSONResponse(content=result, status_code=status_code)


@router.put("/profile", summary="Update authenticated user profile")
async def update_profile_protected(
    body: UpdateProfileRequest,
    current_user: dict = Depends(get_current_user)
):
    result, status_code = AuthController.update_profile(
        data=body.model_dump(exclude_none=True),
        current_user=current_user
    )
    return JSONResponse(content=result, status_code=status_code)


@router.put("/profile/{user_id}", summary="Update user profile by ID")
async def update_profile_by_id(user_id: str, body: UpdateProfileRequest):
    result, status_code = AuthController.update_profile(
        data=body.model_dump(exclude_none=True),
        user_id=user_id
    )
    return JSONResponse(content=result, status_code=status_code)


@router.put("/change-password", summary="Change authenticated user password")
async def change_password(
    body: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user)
):
    result, status_code = AuthController.change_password(
        data=body.model_dump(),
        current_user=current_user
    )
    return JSONResponse(content=result, status_code=status_code)


# Backward-compatible alias
auth_bp = router