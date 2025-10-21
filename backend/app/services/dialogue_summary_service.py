"""
Dialogue summarization service for managing character memory and chat history compression.

This service handles the summarization of chat history to maintain character memory
while keeping chat history manageable by removing summarized portions.
"""

import asyncio
import os
import logging
from typing import List, Optional
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage

from app.dao.character_dao import CharacterDAO
from app.dao.history_dao import HistoryDAO
from app.chat_types import ChatItem
from app.llm.venice_ai import VeniceAIChatModel
from app.services.prompt_templates import (
    CHAT_HISTORY_SUMMARY_PROMPT,
    NO_EXISTING_SUMMARY_INSTRUCTION,
    WITH_EXISTING_SUMMARY_INSTRUCTION
)

logger = logging.getLogger(__name__)


class DialogueSummaryService:
    """
    Service responsible for summarizing dialogue history and updating character memory.
    
    This service:
    1. Takes a chat item ID and collects history up to that point
    2. Concatenates the chat slice into dialogue format
    3. Checks for existing character summaries
    4. Calls LLM to create/update the summary
    5. Updates character with new summary
    6. Removes summarized portion from chat history
    7. Saves updated character and chat history
    """
    
    def __init__(self, story_id: str, character_id: str | None = None):
        """
        Initialize the dialogue summary service.
        
        Args:
            story_id: UUID of the story to work with
            character_id: UUID of the character (will be determined from story if None)
        """
        load_dotenv()
        
        self.story_id = story_id
        self.character_id = character_id
        
        # Initialize DAOs with story-specific paths
        self.character_dao = CharacterDAO(characters_dir=f"data/stories/{story_id}/characters")
        self.chat_history_dao = HistoryDAO(history_file=f"data/stories/{story_id}/history.yaml")
        
        # Initialize LLM
        venice_api_key = os.getenv("VENICE_API_KEY")
        if not venice_api_key:
            raise ValueError(
                "VENICE_API_KEY environment variable is required. "
                "Please set it in your .env file or environment."
            )
        
        self.venice_model = VeniceAIChatModel(
            api_key=venice_api_key,
            model="mistral-31-24b",
            temperature=0.3  # Lower temperature for more consistent summaries
        )
    
    async def summarize_chat_up_to_item(self, chat_item_id: str) -> None:
        """
        Summarize chat history up to and including the specified chat item.
        
        Args:
            chat_item_id: ID of the chat item to summarize up to (inclusive)
            
        Returns:
            Dict containing success status and error information
        """
        logger.info(f"Starting summarization up to chat item ID: {chat_item_id}")

        # Determine character_id if not provided
        if not self.character_id:
            characters = await self.character_dao.get_characters()
            if not characters:
                raise ValueError(f"No characters found in story {self.story_id}")
            self.character_id = characters[0].id

        character, chat_history = await asyncio.gather(
            self.character_dao.get_character(self.character_id),
            self.chat_history_dao.load_history()
        )
        
        chat_slice = chat_history.get_messages_up_to_id(chat_item_id)
        dialogue_text = self._format_chat_as_dialogue(chat_slice)

        existing_memory = character.get_memory()
        existing_summary = "\n".join(existing_memory) if existing_memory else None
        
        new_summary = await self._generate_summary(dialogue_text, existing_summary)
        
        character.add_item_to_memory(new_summary)
        
        chat_history.trim_messages_up_to_id(chat_item_id)
        
        await asyncio.gather(
            self.character_dao.store_character(self.character_id, character),
            self.chat_history_dao.save(chat_history)
        )
    
    def _format_chat_as_dialogue(self, chat_slice: List[ChatItem]) -> str:
        """
        Convert chat items to dialogue format.
        
        Args:
            chat_slice: List of chat items to format
            
        Returns:
            Formatted dialogue string
        """
        dialogue_lines = []
        for item in chat_slice:
            author_name = item.get("author_name", "Unknown")
            content = item.get("content", "")
            dialogue_lines.append(f"{author_name}: {content}")
        
        return "\n".join(dialogue_lines)
    
    async def _generate_summary(self, dialogue_text: str, existing_summary: Optional[str]) -> str:
        """
        Generate a new summary using the LLM.
        
        Args:
            dialogue_text: Current dialogue to summarize
            existing_summary: Previous summary if any
            
        Returns:
            New summary text
        """
        logger.info("Generating new summary...")

        system_prompt = CHAT_HISTORY_SUMMARY_PROMPT

        messages = []
        messages.append(SystemMessage(content=system_prompt))
        
        if existing_summary:
            human_content = WITH_EXISTING_SUMMARY_INSTRUCTION.format(
                existing_summary=existing_summary,
                dialogue_text=dialogue_text
            )
        else:
            human_content = NO_EXISTING_SUMMARY_INSTRUCTION.format(
                dialogue_text=dialogue_text
            )
        
        messages.append(HumanMessage(content=human_content))
        
        response = await self.venice_model.ainvoke(messages)
        return str(response.content).strip()
