"""
Centralized application configuration settings.
Single source of truth for all environment variables and configuration.
"""

import os
from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel, Field, validator

# Load environment variables once at module level
load_dotenv()

class Settings(BaseModel):
    """Application settings with validation and environment variable support."""
    
    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000"], 
        description="Allowed CORS origins"
    )
    
    # Venice AI Configuration - The only external dependency we need to configure
    VENICE_API_KEY: str = Field(
        default_factory=lambda: os.getenv("VENICE_API_KEY", ""),
        description="Venice AI API key (required)"
    )
    
    # Data Paths - Centralized path management
    DATA_BASE_DIR: str = Field(default="data", description="Base directory for all application data")
    
    @property
    def stories_base_dir(self) -> str:
        """Base directory for story data."""
        return f"{self.DATA_BASE_DIR}/stories"
    
    @property  
    def characters_base_dir(self) -> str:
        """Base directory for character data."""
        return f"{self.DATA_BASE_DIR}/characters"
    
    def get_story_characters_dir(self, story_id: str) -> str:
        """Get characters directory for a specific story."""
        return f"{self.stories_base_dir}/{story_id}/characters"
    
    def get_story_history_file(self, story_id: str) -> str:
        """Get history file path for a specific story."""
        return f"{self.stories_base_dir}/{story_id}/history.yaml"
    
    def get_story_meta_dir(self, story_id: str) -> str:
        """Get meta directory for a specific story."""
        return f"{self.stories_base_dir}/{story_id}"
    
    @validator('VENICE_API_KEY')
    def validate_venice_api_key(cls, v: str) -> str:
        """Ensure Venice API key is provided."""
        if not v or v.strip() == "":
            raise ValueError(
                "VENICE_API_KEY environment variable is required. "
                "Please set it in your .env file or environment."
            )
        return v.strip()
    
    class Config:
        """Pydantic config."""
        case_sensitive = True
        validate_assignment = True

# Create single instance of settings
try:
    settings = Settings()
except ValueError as e:
    print(f"❌ Configuration Error: {e}")
    print("Please check your .env file and ensure all required environment variables are set.")
    raise
