"""
User Routes Module
Registers endpoints for User Management CRUD under /api/users.
"""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.controllers.user_controller import UserController
from app.middleware.auth_middleware import get_current_user
from app.schemas.request_models import CreateUserRequest, UpdateUserRequest

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.post("", summary="Create a new user")
@router.post("/", include_in_schema=False)
async def create_user(body: CreateUserRequest):
    result, status_code = UserController.create_user(body.model_dump())
    return JSONResponse(content=result, status_code=status_code)


@router.get("", summary="Get all users")
@router.get("/", include_in_schema=False)
async def get_all_users():
    result, status_code = UserController.get_all_users()
    return JSONResponse(content=result, status_code=status_code)


@router.get("/{user_id}", summary="Get user by ID")
async def get_user_by_id(user_id: str):
    result, status_code = UserController.get_user_by_id(user_id)
    return JSONResponse(content=result, status_code=status_code)


@router.put("/{user_id}", summary="Update user by ID")
async def update_user(
    user_id: str,
    body: UpdateUserRequest,
    current_user: dict = Depends(get_current_user)
):
    result, status_code = UserController.update_user(user_id, body.model_dump(exclude_none=True))
    return JSONResponse(content=result, status_code=status_code)


@router.delete("/{user_id}", summary="Delete user by ID")
async def delete_user(user_id: str, current_user: dict = Depends(get_current_user)):
    result, status_code = UserController.delete_user(user_id)
    return JSONResponse(content=result, status_code=status_code)


# Backward-compatible alias for test imports
user_bp = router
