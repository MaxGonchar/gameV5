"""
Pydantic models for API requests.
"""

# # Standard library imports
from typing import Optional

# # Third-party imports
from pydantic import BaseModel, Field


class SendMessageRequest(BaseModel):
    """Request model for sending a chat message."""

    message: str = Field(..., min_length=1, description="The message content")


class SummarizeChatRequest(BaseModel):
    """Request model for chat summarization (optional body)."""

    pass


class CreateStoryRequest(BaseModel):
    """Request model for creating a new story with session context generation."""

    character_id: str = Field(
        ..., description="UUID of the character for the new story"
    )

    # User context fields for SESSION CONTEXT GENERATION ASSISTANT
    story_title: str = Field(..., min_length=1, description="Title of the story")
    companion_name: str = Field(
        ..., min_length=1, description="User's name/preferred address"
    )
    companion_description: str = Field(
        ..., min_length=1, description="User character description/background"
    )
    companion_context: str = Field(
        ..., min_length=1, description="Background context/world information"
    )
    meeting_location_description: str = Field(
        ..., min_length=1, description="Description of the meeting location"
    )
    meeting_description: str = Field(
        ..., min_length=1, description="How the meeting happens/scenario"
    )
