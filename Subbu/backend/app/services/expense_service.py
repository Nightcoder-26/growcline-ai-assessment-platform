from bson import ObjectId
from datetime import datetime
from ..models.expense import ExpenseCreate
from ..core.database import Database

class ExpenseService:
    @staticmethod
    def get_collection():
        return Database.get_collection("expenses")

    @classmethod
    async def get_all_expenses(cls):
        expenses = []
        cursor = cls.get_collection().find()
        async for document in cursor:
            document["id"] = str(document["_id"])
            expenses.append(document)
        return expenses

    @classmethod
    async def create_expense(cls, expense_data: ExpenseCreate):
        expense_dict = expense_data.model_dump()
        expense_dict["date"] = datetime.utcnow()
        
        new_expense = await cls.get_collection().insert_one(expense_dict)
        created_expense = await cls.get_collection().find_one({"_id": new_expense.inserted_id})
        
        created_expense["id"] = str(created_expense["_id"])
        return created_expense

    @classmethod
    async def delete_expense(cls, expense_id: str):
        if not ObjectId.is_valid(expense_id):
            return False
            
        delete_result = await cls.get_collection().delete_one({"_id": ObjectId(expense_id)})
        return delete_result.deleted_count > 0

    @classmethod
    async def update_expense(cls, expense_id: str, expense_data: ExpenseCreate):
        if not ObjectId.is_valid(expense_id):
            return None
            
        update_data = expense_data.model_dump()
        result = await cls.get_collection().update_one(
            {"_id": ObjectId(expense_id)},
            {"$set": update_data}
        )
        
        if result.modified_count == 0 and result.matched_count == 0:
            return None
            
        updated = await cls.get_collection().find_one({"_id": ObjectId(expense_id)})
        updated["id"] = str(updated["_id"])
        return updated
