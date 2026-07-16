from fastapi import APIRouter, HTTPException
from typing import List

from app.schemas import TodoCreate, TodoUpdate, TodoResponse
from app.crud import (
    create_todo,
    get_all_todos,
    get_todo_by_id,
    update_todo,
    delete_todo,
)

router = APIRouter()


@router.post("/todos", response_model=TodoResponse)
def add_todo(todo: TodoCreate):
    return create_todo(todo)


@router.get("/todos", response_model=List[TodoResponse])
def fetch_todos():
    return get_all_todos()


@router.get("/todos/{todo_id}", response_model=TodoResponse)
def fetch_todo(todo_id: str):
    todo = get_todo_by_id(todo_id)

    if todo == "invalid":
        raise HTTPException(
            status_code=400,
            detail="Invalid Todo ID"
        )

    if todo is None:
        raise HTTPException(
            status_code=404,
            detail="Todo not found"
        )

    return todo


@router.put("/todos/{todo_id}", response_model=TodoResponse)
def edit_todo(todo_id: str, todo: TodoUpdate):
    updated_todo = update_todo(todo_id, todo)

    if updated_todo == "invalid":
        raise HTTPException(
            status_code=400,
            detail="Invalid Todo ID"
        )

    if updated_todo is None:
        raise HTTPException(
            status_code=404,
            detail="Todo not found"
        )

    return updated_todo


@router.delete("/todos/{todo_id}")
def remove_todo(todo_id: str):
    deleted = delete_todo(todo_id)

    if deleted == "invalid":
        raise HTTPException(
            status_code=400,
            detail="Invalid Todo ID"
        )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Todo not found"
        )

    return {
        "message": "Todo deleted successfully"
    }