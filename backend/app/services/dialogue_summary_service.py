"""
Dialogue summarization service for managing character memory and chat history compression.

This service handles the summarization of chat history to maintain character memory
while keeping chat history manageable by removing summarized portions.
"""

import asyncio
import os
import logging
from typing import List, Optional
from langchain_core.messages import SystemMessage, HumanMessage
from jinja2 import Template

from app.core.config import settings
from app.objects.character import Character
from app.dao.character_dao import CharacterDAO
from app.dao.history_dao import HistoryDAO
from app.chat_types import ChatItem
from app.llm.venice_ai import VeniceAIChatModel
from app.services.prompt_templates import (
    CHAT_HISTORY_SUMMARY_PROMPT,
    NO_EXISTING_SUMMARY_INSTRUCTION,
    WITH_EXISTING_SUMMARY_INSTRUCTION
)
from app.models.dialogue_memory_summary import DialogueMemorySummaryResponse, DIALOGUE_MEMORY_SUMMARIZATION_USER_PROMPT, DIALOGUE_MEMORY_SUMMARIZATION_SYSTEM_PROMPT
from app.services.llm_communicator import LLMCommunicator
from app.core.config import get_logger

logger = get_logger(__name__)


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
        self.story_id = story_id
        self.character_id = character_id
        
        # Initialize DAOs with story-specific paths
        self.character_dao = CharacterDAO(characters_dir=settings.get_story_characters_dir(story_id))
        self.chat_history_dao = HistoryDAO(history_file=settings.get_story_history_file(story_id))
        
        # Venice API key is validated in settings
        venice_api_key = settings.VENICE_API_KEY
        
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
        dialogue_items = self._format_chat_as_dialogue(chat_slice)

        new_summary = await self._generate_summary(dialogue_items, character)

        print("*" * 100)
        print("New Summary Generated:")
        print("*" * 100)
        for item in new_summary.memory_items:
            print(f"- {item.event_description}")
            print(f"  Reflection: {item.in_character_reflection}")
        print("*" * 100)

        character.add_items_to_memory(
            [
                {
                    "event_description": item.event_description,
                    "in_character_reflection": item.in_character_reflection
                }
                for item in new_summary.memory_items
            ]
        )

        chat_history.trim_messages_up_to_id(chat_item_id)
        
        await asyncio.gather(
            self.character_dao.store_character(self.character_id, character),
            self.chat_history_dao.save(chat_history)
        )
    
    def _format_chat_as_dialogue(self, chat_slice: List[ChatItem]) -> list[str]:
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
            dialogue_lines.append(f"*Actor:* {author_name}\n*Action/Message:* {content}")

        return dialogue_lines

    async def _generate_summary(self, dialogue_items: list[str], character: Character) -> DialogueMemorySummaryResponse:
        """
        Generate a new summary using the LLM.
        
        Args:
            dialogue_items: Current dialogue to summarize
            existing_summary: Previous summary if any
            
        Returns:
            New summary text
        """
        logger.info("Generating new summary...")

        prompt_template = Template(DIALOGUE_MEMORY_SUMMARIZATION_USER_PROMPT)
        user_prompt = prompt_template.render({
            "character_name": character.base_personality["name"],
            "in_universe_self_description": character.base_personality["in-universe_self_description"],
            "sensory_origin_memory": character.base_personality["sensory_origin_memory"],
            "character_native_deflection": character.base_personality["character_native_deflection"],
            "personality": character.general["personality"],
            "traits": character.base_personality["traits"],
            "core_principles": character.base_personality["core_principles"],
            "physical_tells": character.base_personality["physical_tells"],
            "speech_patterns": character.base_personality["speech_patterns"],
            "dialogue_segments": dialogue_items
        })

        llm_communicator = LLMCommunicator(llm_model=self.venice_model)
        memory_items = await llm_communicator.generate_structured_response(
            system_prompt=DIALOGUE_MEMORY_SUMMARIZATION_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=DialogueMemorySummaryResponse
        )

        return memory_items
