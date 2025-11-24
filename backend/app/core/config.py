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
    
    # Server Configuration
    SERVER_HOST: str = Field(
        default="0.0.0.0",
        description="Server host address"
    )
    SERVER_PORT: int = Field(
        default=8000,
        description="Server port number"
    )
    SERVER_RELOAD: bool = Field(
        default=True,
        description="Enable auto-reload for development"
    )
    
    # Venice AI Configuration - The only external dependency we need to configure
    VENICE_API_KEY: str = Field(
        default_factory=lambda: os.getenv("VENICE_API_KEY", ""),
        description="Venice AI API key (required)"
    )
    
    # LLM Model Configuration
    DEFAULT_STORY_MODEL: str = Field(
        default_factory=lambda: os.getenv("DEFAULT_STORY_MODEL", "venice-uncensored"),
        description="Default model for story generation"
    )
    DEFAULT_SUMMARY_MODEL: str = Field(
        default_factory=lambda: os.getenv("DEFAULT_SUMMARY_MODEL", "mistral-31-24b"),
        description="Default model for dialogue summaries"
    )
    DEFAULT_STORY_CONTEXT_MODEL: str = Field(
        default_factory=lambda: os.getenv("DEFAULT_STORY_CONTEXT_MODEL", "mistral-31-24b"),
        description="Default model for story context generation"
    )
    DEFAULT_STORY_TEMPERATURE: float = Field(
        default_factory=lambda: float(os.getenv("DEFAULT_STORY_TEMPERATURE", "0.7")),
        description="Default temperature for story generation (0.0-2.0)"
    )
    DEFAULT_SUMMARY_TEMPERATURE: float = Field(
        default_factory=lambda: float(os.getenv("DEFAULT_SUMMARY_TEMPERATURE", "0.3")),
        description="Default temperature for dialogue summaries (0.0-2.0)"
    )
    DEFAULT_STORY_CONTEXT_TEMPERATURE: float = Field(
        default_factory=lambda: float(os.getenv("DEFAULT_STORY_CONTEXT_TEMPERATURE", "0.7")),
        description="Default temperature for story context generation (0.0-2.0)"
    )
    
    # Logging Configuration
    LOG_LEVEL: str = Field(
        default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"),
        description="Application log level"
    )
    
    # Data Paths - Base directory only
    DATA_BASE_DIR: str = Field(default="data", description="Base directory for all application data")
    
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
    
    @validator('DEFAULT_STORY_TEMPERATURE', 'DEFAULT_SUMMARY_TEMPERATURE', 'DEFAULT_STORY_CONTEXT_TEMPERATURE')
    def validate_temperature(cls, v: float) -> float:
        """Ensure temperature values are within valid range."""
        if not 0.0 <= v <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")
        return v
    
    @validator('DEFAULT_STORY_MODEL', 'DEFAULT_SUMMARY_MODEL', 'DEFAULT_STORY_CONTEXT_MODEL')
    def validate_model_name(cls, v: str) -> str:
        """Ensure model names are not empty."""
        if not v or not v.strip():
            raise ValueError("Model name cannot be empty")
        return v.strip()
    
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
