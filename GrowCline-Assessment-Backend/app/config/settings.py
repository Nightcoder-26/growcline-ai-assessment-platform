"""
Application Configuration
Loads all environment variables from the .env file.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application Configuration"""

    # Flask Configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "growcline-secret-key")

    # Server Configuration
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 5001))
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"

    # MongoDB Configuration
    MONGO_URI = os.getenv("MONGO_URI")

    # JWT Configuration
    JWT_SECRET = os.getenv("JWT_SECRET")
    JWT_EXPIRATION = int(os.getenv("JWT_EXPIRATION", 86400))

    # Groq AI Configuration
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    # AWS S3 Configuration (Video Recording Module)
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.getenv("AWS_REGION")
    AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")

    # Recording Upload Limits
    MAX_RECORDING_SIZE_MB = int(os.getenv("MAX_RECORDING_SIZE_MB", 500))

    # Presigned URL Expiry (seconds)
    RECORDING_URL_EXPIRY_SECONDS = int(os.getenv("RECORDING_URL_EXPIRY_SECONDS", 900))

    # Upload Configuration
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

    # Allowed File Extensions
    ALLOWED_EXTENSIONS = {
        "pdf",
        "doc",
        "docx",
        "txt",
        "csv",
        "png",
        "jpg",
        "jpeg",
    }