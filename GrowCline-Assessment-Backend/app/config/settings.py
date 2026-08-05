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

    # Google Drive Configuration (Video Recording Module)
    # Path to the Service Account JSON key file — must be excluded from Git.
    GOOGLE_APPLICATION_CREDENTIALS: str = (
        os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        or os.getenv("GOOGLE_DRIVE_CREDENTIALS_FILE")
        or "credentials/google-drive-credentials.json"
    )
    GOOGLE_DRIVE_CREDENTIALS_FILE: str = GOOGLE_APPLICATION_CREDENTIALS

    # Google Drive folder ID where all interview recordings are stored.
    GOOGLE_DRIVE_FOLDER_ID: str = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "")

    # Recording Upload Limits
    MAX_RECORDING_SIZE_MB: int = int(os.getenv("MAX_RECORDING_SIZE_MB", 500))

    # Recording URL / stream link TTL (seconds)
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

    @classmethod
    def validate_google_drive_config(cls):
        """
        Validate that required Google Drive configuration is present.
        Raises a clear RuntimeError if mandatory values are missing.
        """
        if not cls.GOOGLE_DRIVE_FOLDER_ID:
            raise RuntimeError(
                "Missing required configuration: GOOGLE_DRIVE_FOLDER_ID environment variable is not set."
            )
        if not cls.GOOGLE_APPLICATION_CREDENTIALS and not os.path.exists(cls.GOOGLE_DRIVE_CREDENTIALS_FILE):
            raise RuntimeError(
                "Missing required configuration: GOOGLE_APPLICATION_CREDENTIALS file not found."
            )