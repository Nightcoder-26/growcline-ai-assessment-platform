"""
User Routes Module
Registers endpoints for User Management CRUD under /api/users.
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

try:
    from controllers.user_controller import UserController
    from middleware.auth_middleware import get_current_user
except ImportError:
    from app.controllers.user_controller import UserController
    from app.middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/api/users", tags=["Users"])


# 1. Create User (POST /api/users)
@router.post("")
@router.post("/")
async def create_user(request: Request):
    try:
        data = await request.json()
    except Exception:
        data = {}
    result, status_code = UserController.create_user(data)
    return JSONResponse(content=result, status_code=status_code)


# 2. Get All Users (GET /api/users)
@router.get("")
@router.get("/")
async def get_all_users():
    result, status_code = UserController.get_all_users()
    return JSONResponse(content=result, status_code=status_code)


# 3. Get User By ID (GET /api/users/<user_id>)
@router.get("/{user_id}")
async def get_user_by_id(user_id: str):
    result, status_code = UserController.get_user_by_id(user_id)
    return JSONResponse(content=result, status_code=status_code)


# 4. Update User (PUT /api/users/<user_id>) - Protected Route
@router.put("/{user_id}")
async def update_user(user_id: str, request: Request, current_user: dict = Depends(get_current_user)):
    try:
        data = await request.json()
    except Exception:
        data = {}
    result, status_code = UserController.update_user(user_id, data)
    return JSONResponse(content=result, status_code=status_code)


# 5. Delete User (DELETE /api/users/<user_id>) - Protected Route
@router.delete("/{user_id}")
async def delete_user(user_id: str, current_user: dict = Depends(get_current_user)):
    result, status_code = UserController.delete_user(user_id)
    return JSONResponse(content=result, status_code=status_code)


# Backward-compatible alias
user_bp = router
