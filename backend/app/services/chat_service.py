"""
Chat service module containing business logic and prompt processing.
"""

import asyncio
from enum import Enum
from typing import Any, List
import os
from dotenv import load_dotenv
import logging

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage

from app.chat_types import ChatItem, ProcessUserMessageResponse
from app.llm.venice_ai import VeniceAIChatModel
from app.llm.venice_client import VeniceClient
from app.models.assistant_response import AssistantResponse
from app.dao.character_dao import CharacterDAO
from app.dao.chat_history_dao import ChatHistoryDAO
from app.builders import CharacterMoveSystemPromptBuilder
from app.objects import Character, ChatHistory


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# temporary constants:
CHARACTER_NAME = "Nira"
CHARACTER_ID = "nira"
USER_NAME = "Max"
USER_ID = "max"


class AuthorType(Enum):
    USER = "user"
    BOT = "bot"


class ChatService:
    """Service class handling chat business logic with LangChain-based prompt processing."""
    
    def __init__(
        self, 
        character_name: str = "nira"
    ):
        """
        Initialize the chat service with VeniceAI integration and dynamic prompt building.
        
        Args:
            character_name: Name of the character to load configuration for.
            
        Raises:
            ValueError: If VENICE_API_KEY environment variable is not set or character not found.
        """
        load_dotenv()  # Load environment variables
        
        self.character_name = character_name
        
        # Initialize DAOs
        self.character_dao = CharacterDAO()
        self.chat_history_dao = ChatHistoryDAO()
        
        # Initialize character prompt builder with default template
        self.system_prompt_builder = CharacterMoveSystemPromptBuilder()

        # Setup output parser
        self.output_parser = PydanticOutputParser(pydantic_object=AssistantResponse)
        
        # Get VeniceAI API key - required for this app
        venice_api_key = os.getenv("VENICE_API_KEY")
        if not venice_api_key:
            raise ValueError(
                "VENICE_API_KEY environment variable is required. "
                "Please set it in your .env file or environment."
            )
        self.llm_client = VeniceClient(venice_api_key)
        # Initialize VeniceAI model
        try:
            self.venice_model = VeniceAIChatModel(
                api_key=venice_api_key,
                model="mistral-31-24b",
                temperature=0.7
            )
            print("✅ VeniceAI integration enabled")
        except Exception as e:
            raise ValueError(f"Failed to initialize VeniceAI model: {e}")

    def _generate_chat_messages(self, chat_history: ChatHistory, character_config: dict[str, Any]) -> list[BaseMessage]:
        messages = []
        system_prompt = self.system_prompt_builder.build(character_config=character_config)
        messages.append(SystemMessage(content=system_prompt))

        for item in chat_history:
            if item["author_type"] == "user":
                messages.append(HumanMessage(content=item["content"]))
            elif item["author_type"] == "bot":
                messages.append(AIMessage(content=item["content"]))

        return messages


    async def _generate_bot_response(self, chat_history: ChatHistory, character_config: dict[str, Any]) -> str:
        messages = self._generate_chat_messages(chat_history, character_config)
        response = await self.venice_model.ainvoke(messages)

        return str(response.content)

    async def _get_data(self) -> tuple[Character, ChatHistory]:
        character, chat_history = await asyncio.gather(
            self.character_dao.get_character(self.character_name),
            self.chat_history_dao.load_chat_history()
        )
        return character, chat_history

    async def _store_data(self, character: Character, chat_history: ChatHistory) -> None:
        await asyncio.gather(
            self.chat_history_dao.save(chat_history),
            self.character_dao.store_character(character)
        )

    async def _update_character(self, character: Character, user_message: str) -> Character:
        embeddings = await self._get_user_message_embeddings(user_message)
        character.update_dynamic_configs_according_to_message_embeddings(embeddings)
        return character
    
    async def _get_user_message_embeddings(self, user_message: str) -> list[float]:
        embeddings = await self.llm_client.embed([user_message])
        return embeddings[0]
    
    async def process_user_message(self, message: str) -> None:
        character, chat_history = await self._get_data()
        chat_history.add_message(
            author_id=USER_ID,
            author_type=AuthorType.USER.value,
            author_name=USER_NAME,
            content=message
        )

        character = await self._update_character(character, message)
        bot_response = await self._generate_bot_response(chat_history, character.to_prompt_dict())

        chat_history.add_message(
            author_id=CHARACTER_ID,
            author_type=AuthorType.BOT.value,
            author_name=CHARACTER_NAME,
            content=bot_response
        )

        await self._store_data(character, chat_history)
    
    async def get_chat_history(self) -> List[ChatItem]:
        chat_history = await self.chat_history_dao.load_chat_history()
        return chat_history.get_data()
