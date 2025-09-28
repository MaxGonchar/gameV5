"""
Application configuration settings.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings."""
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # CORS Configuration
    ALLOWED_ORIGINS: list = ["http://localhost:3000"]
    
    # Character Configuration
    DEFAULT_CHARACTER: str = "nira"
    CHARACTERS_DIR: str = "data/characters"
    CHAT_HISTORY_FILE: str = "data/chat_history/chat_history.yaml"
    
    # Venice AI Configuration
    VENICE_API_KEY: str = os.getenv("VENICE_API_KEY", "")
    
    # Logging
    LOG_LEVEL: str = "INFO"

settings = Settings()