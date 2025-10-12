"""
Chat service module containing business logic and prompt processing.
"""

from typing import List
import os
from dotenv import load_dotenv
import logging
import asyncio

from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain.prompts import PromptTemplate

from app.chat_types import ChatItem
from app.llm.venice_ai import VeniceAIChatModel
from app.llm.venice_client import VeniceClient
from app.models.assistant_response import AssistantResponse
from app.builders import CharacterMoveSystemPromptBuilder
from app.objects.global_state import GlobalState
from app.services.prompt_templates import SCENE_DESCRIPTION


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatService:
    """Service class handling chat business logic with LangChain-based prompt processing."""

    # TODO: Using async __new__ is an anti-pattern and can cause issues with object initialization.
    # Consider using a factory method or async context manager instead.
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
            .with_current_scene_description(self.global_state.get_last_scene_description())\
            .build()

        messages.append(SystemMessage(content=system_prompt))

        for item in self.global_state.get_chat_history():
            if item["author_type"] == "user":
                messages.append(HumanMessage(content=item["content"]))
            elif item["author_type"] == "bot":
                messages.append(AIMessage(content=item["content"]))

        return messages


    async def _generate_bot_response(self) -> str:
        logger.info("Generating bot response...")

        messages = self._generate_chat_messages()
        response = await self.venice_model.ainvoke(messages)
        return str(response.content)

    async def _update_character(self, user_message: str) -> None:
        logger.info(f"Updating character configs based on user message: {user_message}")

        embeddings = await self._get_user_message_embeddings(user_message)
        self.global_state.update_character_configs(embeddings)
    
    async def _get_user_message_embeddings(self, user_message: str) -> list[float]:
        embeddings = await self.llm_client.embed([user_message])
        return embeddings[0]

    async def _update_chat_history(self, message: str, author_user: bool) -> None:
        logger.info(f"Updating chat history with message: {message}, author_user: {author_user}")

        last_description = self.global_state.get_last_scene_description()
        new_description = await self._change_scene_description(last_description, message)
        if author_user:
            self.global_state.add_user_message(message, new_description)
        else:
            self.global_state.add_character_message(message, new_description)
    
    async def _change_scene_description(self, previous_description: str, message: str) -> str:
        template = SCENE_DESCRIPTION
        prompt = PromptTemplate(
            input_variables=["previous_description", "message"],
            template=template
        )
        chain = prompt | self.venice_model | StrOutputParser()
        response = await chain.ainvoke(
            {
                "previous_description": previous_description,
                "message": message
            }
        )
        return response

    async def process_user_message(self, message: str) -> None:
        logger.info(f"Processing user message: {message}")

        await asyncio.gather(
            self._update_chat_history(message, author_user=True),
            self._update_character(message)
        )

        bot_response = await self._generate_bot_response()

        await self._update_chat_history(bot_response, author_user=False)

        logger.info("Update global state...")
        await self.global_state.save_state()
    
    async def get_chat_history(self) -> List[ChatItem]:
        return self.global_state.get_chat_history()
