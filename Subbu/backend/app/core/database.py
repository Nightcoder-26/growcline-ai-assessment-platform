from motor.motor_asyncio import AsyncIOMotorClient

# Simplified Database Connection
MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "expense_tracker"

class Database:
    client: AsyncIOMotorClient = None
    
    @classmethod
    def get_collection(cls, collection_name: str):
        if cls.client is None:
            cls.client = AsyncIOMotorClient(MONGODB_URL)
        return cls.client[DATABASE_NAME][collection_name]
