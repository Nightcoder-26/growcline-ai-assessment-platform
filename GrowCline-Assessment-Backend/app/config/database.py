"""
MongoDB Atlas Configuration
"""

from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, PyMongoError

from app.config.settings import Config
import sys
import io


if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer,
            encoding="utf-8",
            errors="replace",
        )
        sys.stderr = io.TextIOWrapper(
            sys.stderr.buffer,
            encoding="utf-8",
            errors="replace",
        )
    except Exception:
        pass


class Database:
    """MongoDB Database Connection"""

    client = None
    db = None

    @classmethod
    def connect(cls):
        try:
            try:
                import certifi
                cls.client = MongoClient(
                    Config.MONGO_URI,
                    serverSelectionTimeoutMS=5000,
                    tlsCAFile=certifi.where(),
                )
                cls.client.admin.command("ping")
            except Exception:
                cls.client = MongoClient(
                    Config.MONGO_URI,
                    serverSelectionTimeoutMS=5000,
                    tlsAllowInvalidCertificates=True,
                )
                cls.client.admin.command("ping")

            try:
                cls.db = cls.client.get_default_database()
            except Exception:
                cls.db = cls.client["growcline_assessment"]

            cls.init_collections()
            cls.init_indexes()

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
            # Shared / Team A collections
            "users",
            "assessments",
            "assessment_results",
            "aptitude_questions",
            "technical_questions",
            "coding_questions",

            # Team B - AI Interview & Proctoring collections
            "interviews",
            "interview_questions",
            "video_recordings",
            "proctoring_logs",
            "cheating_reports",
            "interview_results",
            "interview_analytics",
        ]

        try:
            existing = cls.db.list_collection_names()

            for collection_name in required_collections:
                if collection_name not in existing:
                    cls.db.create_collection(collection_name)
                    print(f"📦 Created collection: '{collection_name}'")

        except PyMongoError as error:
            print(
                f"⚠️ Warning: Could not initialize collections: {error}"
            )

    @classmethod
    def init_indexes(cls):
        """Create indexes required by Team B interview and proctoring modules."""
        if cls.db is None:
            return

        try:
            cls.db.interviews.create_index(
                [
                    ("userId", ASCENDING),
                    ("createdAt", DESCENDING),
                ],
                name="idx_interviews_user_created",
            )

            cls.db.interviews.create_index(
                [
                    ("userId", ASCENDING),
                    ("status", ASCENDING),
                ],
                name="idx_interviews_user_status",
            )

            cls.db.interview_questions.create_index(
                [
                    ("interviewId", ASCENDING),
                    ("questionNumber", ASCENDING),
                ],
                unique=True,
                name="idx_interview_questions_number",
            )

            cls.db.video_recordings.create_index(
                [("interviewId", ASCENDING)],
                name="idx_video_recordings_interview",
            )

            cls.db.video_recordings.create_index(
                [
                    ("userId", ASCENDING),
                    ("createdAt", DESCENDING),
                ],
                name="idx_video_recordings_user_created",
            )

            cls.db.proctoring_logs.create_index(
                [
                    ("interviewId", ASCENDING),
                    ("timestamp", DESCENDING),
                ],
                name="idx_proctoring_logs_interview_timestamp",
            )

            cls.db.proctoring_logs.create_index(
                [
                    ("interviewId", ASCENDING),
                    ("eventType", ASCENDING),
                ],
                name="idx_proctoring_logs_interview_event",
            )

            cls.db.cheating_reports.create_index(
                [("interviewId", ASCENDING)],
                unique=True,
                name="idx_cheating_reports_interview",
            )

            cls.db.cheating_reports.create_index(
                [
                    ("userId", ASCENDING),
                    ("createdAt", DESCENDING),
                ],
                name="idx_cheating_reports_user_created",
            )

            cls.db.interview_results.create_index(
                [("interviewId", ASCENDING)],
                unique=True,
                name="idx_interview_results_interview",
            )

            cls.db.interview_results.create_index(
                [
                    ("userId", ASCENDING),
                    ("createdAt", DESCENDING),
                ],
                name="idx_interview_results_user_created",
            )

            cls.db.interview_analytics.create_index(
                [("interviewId", ASCENDING)],
                unique=True,
                name="idx_interview_analytics_interview",
            )

            cls.db.interview_analytics.create_index(
                [
                    ("userId", ASCENDING),
                    ("createdAt", DESCENDING),
                ],
                name="idx_interview_analytics_user_created",
            )

            print("🔎 Team B MongoDB indexes initialized")

        except PyMongoError as error:
            print(
                f"⚠️ Warning: Could not initialize indexes: {error}"
            )

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