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

class SendMessageResponse(BaseModel):
    """Response model for sending a message."""
    success: bool
    bot_response: Optional[BotResponse] = None
    error: Optional[str] = None

class ChatHistoryResponse(BaseModel):
    """Response model for chat history."""
    messages: List[ChatMessage]
    scene_description: str

class SummarizeChatResponse(BaseModel):
    """Response model for chat summarization."""
    success: bool
    error: Optional[str] = None

class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    version: str
    timestamp: datetime