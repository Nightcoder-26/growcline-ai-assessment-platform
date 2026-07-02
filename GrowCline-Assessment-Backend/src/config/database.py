"""
MongoDB Atlas Configuration
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError
from config.settings import Config


class Database:
    """MongoDB Database Connection"""

    client = None
    db = None

    @classmethod
    def connect(cls):
        """Connect to MongoDB Atlas"""

        try:
            cls.client = MongoClient(
                Config.MONGO_URI,
                serverSelectionTimeoutMS=5000,
            )

            # Verify Connection
            cls.client.admin.command("ping")

            # Database Name
            cls.db = cls.client["growcline_assessment"]

            print("✅ MongoDB Atlas Connected Successfully")

            return cls.db

        except ConnectionFailure as error:
            print(f"❌ MongoDB Connection Failed: {error}")
            raise

        except PyMongoError as error:
            print(f"❌ MongoDB Error: {error}")
            raise

    @classmethod
    def get_db(cls):
        """Return Database Instance"""

        if cls.db is None:
            cls.connect()

        return cls.db

    @classmethod
    def close_connection(cls):
        """Close MongoDB Connection"""

        if cls.client:
            cls.client.close()
            print("🔒 MongoDB Connection Closed")