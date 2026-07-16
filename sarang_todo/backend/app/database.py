from pymongo import MongoClient
from dotenv import load_dotenv
import certifi
import os

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")

client = MongoClient(
    MONGODB_URI,
    tlsCAFile=certifi.where(),
    serverSelectionTimeoutMS=5000,
)

client.admin.command("ping")
print("✅ MongoDB Connected Successfully")

db = client[DATABASE_NAME]

# Todos Collection
todos_collection = db["todos"]