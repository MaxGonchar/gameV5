"""
Story API endpoints for interactive story application.
"""

from fastapi import APIRouter, HTTPException
import logging


from app.models.requests import SendMessageRequest, CreateStoryRequest
from app.models.responses import (
    ChatHistoryResponse, 
    ChatMessage,
    BotResponse,
    StoriesResponse,
)
from app.services.story_service import StoryService
from app.services.stories_service import StoriesService
from app.services.dialogue_summary_service import DialogueSummaryService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

async def get_story_service(story_id: str) -> StoryService:
    """Create a story service instance for the given story."""
    return await StoryService(story_id)

async def get_dialogue_summary_service(story_id: str) -> DialogueSummaryService:
    """Create a dialogue summary service instance for the given story."""
    return DialogueSummaryService(story_id)

@router.post("/stories/{story_id}/message", response_model=BotResponse)
async def process_user_message(story_id: str, request: SendMessageRequest):
    try:
        logger.info(f"Processing message for story {story_id}: {request.message[:50]}...")
        
        story_service = await get_story_service(story_id)
        await story_service.process_user_message(request.message)
        
        chat_history = story_service.get_chat_history()

        last_message = chat_history[-1]
        return BotResponse(
            id=last_message["id"],
            content=last_message["content"],
            author_name=last_message["author_name"],
            scene_description=last_message["scene_description"],
            story_id=story_id
            )
    except Exception as e:
        logger.exception(f"Error processing message: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/stories/{story_id}/history", response_model=ChatHistoryResponse)
async def get_story_history(story_id: str):
    logger.info(f"Fetching story history for story {story_id}")
    try:
        story_service = await get_story_service(story_id)
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
            scene_description=chat_history[-1]["scene_description"],
            story_id=story_id
        )

    except Exception as e:
        logger.error(f"Error getting story history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/stories/{story_id}/summarize/{message_id}")
async def summarize_story(story_id: str, message_id: str):
    try:
        logger.info(f"Summarizing story {story_id} up to message {message_id}")
        
        dialogue_service = await get_dialogue_summary_service(story_id)
        await dialogue_service.summarize_chat_up_to_item(message_id)
        # TODO: return proper response model
        return {"message": "success", "story_id": story_id}
        
    except Exception as e:
        logger.error(f"Error summarizing story: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/stories")
async def create_story(request: CreateStoryRequest):
    try:
        logger.info("Creating a new story via API")
        
        stories_service = StoriesService()
        new_story_id = await stories_service.create_story(request)
        
        # TODO: return proper response model
        return {"message": "success", "story_id": new_story_id}
        
    except Exception as e:
        logger.error(f"Error creating story: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/stories", response_model=StoriesResponse)
async def get_stories_summary():
    try:
        logger.info("Fetching stories summary via API")

        stories_service = StoriesService()

        return await stories_service.get_stories_summary()
        
    except Exception as e:
        logger.error(f"Error fetching stories summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
