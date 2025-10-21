"""
Story API endpoints for interactive story application.
"""

from fastapi import APIRouter, HTTPException
import logging


from app.models.requests import SendMessageRequest
from app.models.responses import (
    ChatHistoryResponse, 
    ChatMessage,
    BotResponse
)
from app.services.story_service import StoryService
from app.services.dialogue_summary_service import DialogueSummaryService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Story service will be initialized lazily on first use
story_service = None
dialogue_summary_service = DialogueSummaryService()

async def get_story_service():
    """Get or create the story service instance."""
    global story_service
    if story_service is None:
        # TODO: This should be dynamic based on user session/request
        # For now using the test story ID as default
        default_story_id = "fdf6b8ce-57e0-4962-91bd-4f915c3f61e9"
        story_service = await StoryService(default_story_id)
    return story_service

@router.post("/story/message", response_model=BotResponse)
async def process_user_message(request: SendMessageRequest):
    try:
        logger.info(f"Processing message: {request.message[:50]}...")
        
        story_service = await get_story_service()
        await story_service.process_user_message(request.message)
        
        chat_history = story_service.get_chat_history()

        last_message = chat_history[-1]
        return BotResponse(
            id=last_message["id"],
            content=last_message["content"],
            author_name=last_message["author_name"],
            scene_description=last_message["scene_description"]
            )
    except Exception as e:
        logger.exception(f"Error processing message: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/story/history", response_model=ChatHistoryResponse)
async def get_story_history():
    logger.info("Fetching story history")
    try:
        story_service = await get_story_service()
        chat_history = story_service.get_chat_history()
        
        messages = [
            ChatMessage(
                id=item["id"],
                author_id=item["author_id"],
                author_type=item["author_type"],
                author_name=item["author_name"],
                content=item["content"]
            )
            for item in chat_history
        ]
        
        return ChatHistoryResponse(
            messages=messages,
            scene_description=chat_history[-1]["scene_description"]
        )

    except Exception as e:
        logger.error(f"Error getting story history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/story/summarize/{message_id}")
async def summarize_story(message_id: str):
    try:
        logger.info(f"Summarizing story up to message {message_id}")
        
        await dialogue_summary_service.summarize_chat_up_to_item(message_id)
        return {"message": "success"}
        
    except Exception as e:
        logger.error(f"Error summarizing story: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")