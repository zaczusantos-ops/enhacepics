"""
ChurchPhoto Pro - Configuration & Environment
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root or backend directory
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

class Settings:
    PROJECT_NAME: str = "ChurchPhoto Pro - Pós-Processamento Fotográfico"
    VERSION: str = "1.1.0"
    API_V1_STR: str = "/api"
    
    # Gemini API Key (Loaded securely from Server Environment Variables)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Gemini Models: Default to the most advanced PRO model for supreme colorimetry reasoning
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")
    GEMINI_FALLBACK_MODELS: list = [
        "gemini-2.5-pro",
        "gemini-1.5-pro",
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash"
    ]
    
    # Upload limits
    MAX_UPLOAD_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: set = {
        # Standard formats
        "jpg", "jpeg", "png", "webp", "tiff", "tif",
        # Camera RAW formats
        "cr2", "cr3", "nef", "arw", "dng", "orf", "rw2", "pef", "raf"
    }

settings = Settings()
