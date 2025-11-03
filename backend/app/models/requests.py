"""
Pydantic models for API requests.
"""

from pydantic import BaseModel, Field
from typing import Optional

class SendMessageRequest(BaseModel):
    """Request model for sending a chat message."""
    message: str = Field(..., min_length=1, description="The message content")

class SummarizeChatRequest(BaseModel):
    """Request model for chat summarization (optional body)."""
    pass


class CreateStoryRequest(BaseModel):
    """Request model for creating a new story with session context generation."""
    character_id: str = Field(..., description="UUID of the character for the new story")
    location_id: str = Field(..., description="UUID of the location for the new story")
    
    # User context fields for SESSION CONTEXT GENERATION ASSISTANT
    name: str = Field(..., min_length=1, description="User's name/preferred address")
    description: str = Field(..., min_length=1, description="User character description/background")
    context: str = Field(..., min_length=1, description="Background context/world information")
    meeting_location_description: str = Field(..., min_length=1, description="Where the meeting takes place")
    meeting_description: str = Field(..., min_length=1, description="How the meeting happens/scenario")
    
    # Legacy field - keeping for backward compatibility but will be replaced by meeting_description
    init_scene_description: Optional[str] = Field(None, description="Initial scene description (deprecated - use meeting_description)")
