"""
Chat API endpoints.
"""

from fastapi import APIRouter, HTTPException
import logging


from app.models.requests import SendMessageRequest
from app.models.responses import (
    ChatHistoryResponse, 
    ChatMessage,
    BotResponse
)
from app.services.chat_service import ChatService
from app.services.dialogue_summary_service import DialogueSummaryService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

chat_service = ChatService()
dialogue_summary_service = DialogueSummaryService()

@router.post("/chat/message", response_model=BotResponse)
async def process_user_message(request: SendMessageRequest):
    try:
        logger.info(f"Processing message: {request.message[:50]}...")
        
        await chat_service.process_user_message(request.message)
        
        chat_history = await chat_service.get_chat_history()

        last_message = chat_history[-1]
        return BotResponse(
            id=last_message["id"],
            content=last_message["content"],
            author_name=last_message["author_name"]
            )
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/chat/history", response_model=ChatHistoryResponse)
async def get_chat_history():
    logger.info("Fetching chat history")
    try:
        chat_history = await chat_service.get_chat_history()
        
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
        
        return ChatHistoryResponse(messages=messages)
        
    except Exception as e:
        logger.error(f"Error getting chat history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/chat/summarize/{message_id}")
async def summarize_chat(message_id: str):
    try:
        logger.info(f"Summarizing chat up to message {message_id}")
        
        await dialogue_summary_service.summarize_chat_up_to_item(message_id)
        return {"message": "success"}
        
    except Exception as e:
        logger.error(f"Error summarizing chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")