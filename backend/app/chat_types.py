"""
Shared type definitions for the chat application.
"""

from typing_extensions import TypedDict


class ChatItem(TypedDict):
    id: str # id of the chat message (represents place in the chat history)
    author_id: str # id of the author
    author_type: str # type of the author ("user" or "bot")
    author_name: str # name of the author
    content: str # content of the chat message
    scene_description: dict[str, str] # dictionary with 'companion_side' and 'character_side' keys describing the scene after the content


class ProcessUserMessageResponse(TypedDict):
    """Response from processing a user message."""
    success: bool
    error: str | None
