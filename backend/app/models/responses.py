"""
Pydantic models for API responses.
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ChatMessage(BaseModel):
    """Model for a single chat message."""
    id: str
    author_id: str
    author_type: str  # "user" or "bot"
    author_name: str
    content: str

class BotResponse(BaseModel):
    """Model for bot response data."""
    id: str
    content: str
    author_name: str
    scene_description: str
    story_id: Optional[str] = None

class SendMessageResponse(BaseModel):
    """Response model for sending a message."""
    success: bool
    bot_response: Optional[BotResponse] = None
    error: Optional[str] = None

class ChatHistoryResponse(BaseModel):
    """Response model for chat history."""
    messages: List[ChatMessage]
    scene_description: str
    story_id: Optional[str] = None

class SummarizeChatResponse(BaseModel):
    """Response model for chat summarization."""
    success: bool
    story_id: Optional[str] = None
    error: Optional[str] = None

class CharacterSummary(BaseModel):
    """Model for character summary data."""
    id: str
    name: str

class CharactersResponse(BaseModel):
    """Response model for characters list."""
    characters: List[CharacterSummary]

class LocationSummary(BaseModel):
    """Model for location summary data."""
    id: str
    name: str

class LocationsResponse(BaseModel):
    """Response model for locations list."""
    locations: List[LocationSummary]

class StorySummary(BaseModel):
    """Model for story summary data."""
    id: str
    title: str

class StoriesResponse(BaseModel):
    """Response model for stories list."""
    stories: List[StorySummary]

class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    version: str
    timestamp: datetime