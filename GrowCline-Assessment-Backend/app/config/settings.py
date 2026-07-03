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
    PORT = int(os.getenv("PORT", 5000))
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"

    # MongoDB Configuration
    MONGO_URI = os.getenv("MONGO_URI")

    # JWT Configuration
    JWT_SECRET = os.getenv("JWT_SECRET")
    JWT_EXPIRATION = int(os.getenv("JWT_EXPIRATION", 86400))

    # Groq AI Configuration
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

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