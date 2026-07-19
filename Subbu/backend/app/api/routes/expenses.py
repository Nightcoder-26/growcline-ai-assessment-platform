from fastapi import APIRouter, HTTPException, status
from typing import List
from ...models.expense import ExpenseResponse, ExpenseCreate
from ...services.expense_service import ExpenseService

router = APIRouter(
    prefix="/expenses",
    tags=["expenses"]
)

@router.get("/", response_model=List[ExpenseResponse])
async def get_expenses():
    return await ExpenseService.get_all_expenses()

@router.post("/", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(expense: ExpenseCreate):
    return await ExpenseService.create_expense(expense)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(id: str):
    success = await ExpenseService.delete_expense(id)
    if not success:
        raise HTTPException(status_code=404, detail="Expense not found or invalid ID")
    return None

@router.put("/{id}", response_model=ExpenseResponse)
async def update_expense(id: str, expense: ExpenseCreate):
    updated = await ExpenseService.update_expense(id, expense)
    if not updated:
        raise HTTPException(status_code=404, detail="Expense not found or invalid ID")
    return updated
