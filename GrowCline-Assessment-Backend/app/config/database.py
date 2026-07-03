"""
MongoDB Atlas Configuration
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError

from app.config.settings import Config
import sys
import io

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass


class Database:
    """MongoDB Database Connection"""

    client = None
    db = None

    @classmethod
    def connect(cls):
        try:
            cls.client = MongoClient(
                Config.MONGO_URI,
                serverSelectionTimeoutMS=5000,
            )

            cls.client.admin.command("ping")

            try:
                cls.db = cls.client.get_default_database()
            except Exception:
                # Default to 'growcline_assessment' if no default database in URI
                cls.db = cls.client["growcline_assessment"]

            cls.init_collections()

            print("✅ MongoDB Atlas Connected Successfully")
            print(f"📊 Active Database: {cls.db.name}")

            return cls.db

        except ConnectionFailure as error:
            print(f"❌ MongoDB Connection Failed: {error}")
            raise

        except PyMongoError as error:
            print(f"❌ MongoDB Error: {error}")
            raise

    @classmethod
    def init_collections(cls):
        """Explicitly create required collections in MongoDB Atlas if they do not exist."""
        if cls.db is None:
            return

        required_collections = [
            "users",
            "assessments",
            "assessment_results",
            "aptitude_questions",
            "technical_questions",
            "coding_questions"
        ]

        try:
            existing = cls.db.list_collection_names()
            for col in required_collections:
                if col not in existing:
                    cls.db.create_collection(col)
                    print(f"📦 Created collection: '{col}'")
        except Exception as e:
            print(f"⚠️ Warning: Could not initialize collections: {e}")

    @classmethod
    def get_db(cls):
        if cls.db is None:
            cls.connect()

        return cls.db

    @classmethod
    def close_connection(cls):
        if cls.client:
            cls.client.close()
            print("🔒 MongoDB Connection Closed")