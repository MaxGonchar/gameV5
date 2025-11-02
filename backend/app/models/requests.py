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
    """Request model for creating a new story."""
    character_id: str = Field(..., description="UUID of the character for the new story")
    location_id: str = Field(..., description="UUID of the location for the new story")
    init_scene_description: str = Field(..., description="Initial scene description for the new story")
