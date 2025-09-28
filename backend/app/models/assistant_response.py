"""
Pydantic models for LLM responses.
"""

from pydantic import BaseModel, Field


class AssistantResponse(BaseModel):
    """Pydantic model for the assistant character's structured response."""
    
    action: str = Field(
        description="The physical action or gesture that the assistant character performs. IMPORTANT: if the action is repeated, or it is not supposed the character to perform it, the action can be just an empty string.",
        default=""
    )
    speech: str = Field(
        description="What the assistant character says in response",
        min_length=1
    )
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "action": "tilts head curiously",
                "speech": "I'm glad you asked! Let me explain..."
            },
            "example with no action": {
                "action": "",
                "speech": "Please, continue, I'm listening."
            }
        }
