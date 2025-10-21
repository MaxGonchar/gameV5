"""
Pydantic models for API requests.
"""

from pydantic import BaseModel, Field
from typing import Optional

class SendMessageRequest(BaseModel):
    """Request model for sending a chat message."""
    message: str = Field(..., min_length=1, description="The message content")
    story_id: Optional[str] = Field(None, description="UUID of the story (optional for backward compatibility)")

class SummarizeChatRequest(BaseModel):
    """Request model for chat summarization (optional body)."""
    pass