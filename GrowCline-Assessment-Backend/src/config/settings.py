"""
Application configuration settings.
Loads all environment variables from the .env file.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application Configuration"""

    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key")

    # Server
    PORT = int(os.getenv("PORT", 5000))
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"

    # MongoDB
    MONGO_URI = os.getenv("MONGO_URI")

    # JWT
    JWT_SECRET = os.getenv("JWT_SECRET")
    JWT_EXPIRATION = int(os.getenv("JWT_EXPIRATION", 86400))  # 24 hours

    # Gemini AI
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    # Uploads
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")

    # File Upload Limits
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

    # Allowed Upload Extensions
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