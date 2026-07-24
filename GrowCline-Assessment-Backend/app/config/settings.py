"""
Application Configuration
Loads and standardizes all environment variables.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application Configuration"""

    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 5001))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

    # MongoDB Configuration
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017/growcline_assessment")

    # JWT Configuration
    JWT_SECRET: str = os.getenv("JWT_SECRET") or os.getenv("JWT_SECRET_KEY") or "growcline-jwt-secret-key"
    JWT_EXPIRATION: int = int(os.getenv("JWT_EXPIRATION", 86400))

    # Groq AI Configuration
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

    # AWS S3 Configuration (Video Recording Module)
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    AWS_S3_BUCKET: str = os.getenv("AWS_S3_BUCKET", "")

    # Recording Upload Limits
    MAX_RECORDING_SIZE_MB: int = int(os.getenv("MAX_RECORDING_SIZE_MB", 500))

    # Presigned URL Expiry (seconds)
    RECORDING_URL_EXPIRY_SECONDS: int = int(os.getenv("RECORDING_URL_EXPIRY_SECONDS", 900))

    # Upload Configuration
    UPLOAD_FOLDER: str = os.getenv("UPLOAD_FOLDER", "uploads")
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 16 MB

    # Allowed File Extensions
    ALLOWED_EXTENSIONS: set = {
        "pdf",
        "doc",
        "docx",
        "txt",
        "csv",
        "png",
        "jpg",
        "jpeg",
    }