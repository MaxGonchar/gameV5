"""
Centralized application configuration settings.
Single source of truth for all environment variables and configuration.
"""

import os
import logging
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
    
    # Logging Configuration
    LOG_LEVEL: str = Field(
        default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"),
        description="Application log level"
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
    
    @validator('LOG_LEVEL')
    def validate_log_level(cls, v: str) -> str:
        """Ensure log level is valid."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of: {', '.join(valid_levels)}")
        return v_upper
    
    class Config:
        """Pydantic config."""
        case_sensitive = True
        validate_assignment = True

def configure_logging(log_level: str = "INFO") -> None:
    """
    Configure application-wide logging settings.
    
    This should be called once at application startup to avoid conflicts
    from multiple basicConfig() calls throughout the codebase.
    
    Args:
        log_level: The logging level to use (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Configure root logger only once
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        force=True  # Override any existing configuration
    )
    
    # Set specific loggers to appropriate levels
    # Reduce noise from external libraries if needed
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    
    # Create app logger to confirm configuration
    app_logger = logging.getLogger("app.core.config")
    app_logger.info(f"Logging configured with level: {log_level}")

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the given name.
    
    This is a centralized way to get loggers throughout the application.
    Ensures consistent logger configuration.
    
    Args:
        name: Usually __name__ from the calling module
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)

# Create single instance of settings
try:
    settings = Settings()
    # Configure logging immediately after settings are loaded
    configure_logging(settings.LOG_LEVEL)
except ValueError as e:
    print(f"❌ Configuration Error: {e}")
    print("Please check your .env file and ensure all required environment variables are set.")
    raise
