"""
Chat service module containing business logic and prompt processing.
"""

from enum import Enum
from typing import List
import os
from dotenv import load_dotenv
import logging

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage

from app.chat_types import ChatItem
from app.llm.venice_ai import VeniceAIChatModel
from app.llm.venice_client import VeniceClient
from app.models.assistant_response import AssistantResponse
from app.builders import CharacterMoveSystemPromptBuilder
from app.objects.global_state import GlobalState


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatService:
    """Service class handling chat business logic with LangChain-based prompt processing."""

    # TODO: extract to aobject to use like "class ChatService(aobject)"
    async def __new__(cls, *a, **kw):
        instance = super().__new__(cls)
        await instance.__init__(*a, **kw)
        return instance
    
    async def __init__(
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

        self.global_state: GlobalState = await GlobalState(character_name)
        
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

    def _generate_chat_messages(self) -> list[BaseMessage]:
        messages = []

        system_prompt = self.system_prompt_builder\
            .with_assistant_configs(self.global_state.get_character_assistant_configs())\
            .with_character_config(self.global_state.get_character_prompt_configs())\
            .with_location_config(self.global_state.get_location_description())\
            .build()

        messages.append(SystemMessage(content=system_prompt))

        for item in self.global_state.get_chat_history():
            if item["author_type"] == "user":
                messages.append(HumanMessage(content=item["content"]))
            elif item["author_type"] == "bot":
                messages.append(AIMessage(content=item["content"]))

        return messages


    async def _generate_bot_response(self) -> str:
        messages = self._generate_chat_messages()
        response = await self.venice_model.ainvoke(messages)

        return str(response.content)

    async def _update_character(self, user_message: str) -> None:
        embeddings = await self._get_user_message_embeddings(user_message)
        self.global_state.update_character_configs(embeddings)
    
    async def _get_user_message_embeddings(self, user_message: str) -> list[float]:
        embeddings = await self.llm_client.embed([user_message])
        return embeddings[0]
    
    async def process_user_message(self, message: str) -> None:
        self.global_state.add_user_message(message)

        await self._update_character(message)
        bot_response = await self._generate_bot_response()

        self.global_state.add_character_message(bot_response)

        await self.global_state.save_state()
    
    async def get_chat_history(self) -> List[ChatItem]:
        return self.global_state.get_chat_history()
