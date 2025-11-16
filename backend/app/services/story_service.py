"""
Story service module containing business logic and prompt processing for interactive story generation.
"""

import os
from typing import Any
import logging
import asyncio

from jinja2 import Template
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage

from app.core.config import settings, get_logger
from app.chat_types import ChatItem
from app.llm.venice_ai import VeniceAIChatModel
from app.llm.venice_client import VeniceClient
from app.models.assistant_response import AssistantResponse
from app.builders import CharacterMoveSystemPromptBuilder
from app.objects.story_state import StoryState
from app.services.llm_communicator import LLMCommunicator
from app.models.scene_description import MOVE_SCENE_DESCRIPTION_SYSTEM_PROMPT, MOVE_SCENE_DESCRIPTION_USER_PROMPT, MoveSceneDescriptionResponse

logger = get_logger(__name__)


class StoryService:
    """Service class handling interactive story business logic with LangChain-based prompt processing.
    
    Use StoryService.create() factory method for async initialization.
    """
    
    def __init__(
        self,
        story_id: str,
        *,  # Force keyword-only parameters
        story_state: StoryState | None = None
    ):
        """
        Initialize the story service with required data.
        
        Args:
            story_id: UUID of the story
            story_state: StoryState instance (required)
            
        Raises:
            ValueError: If story_state parameter is None
            
        Note: Use StoryService.create(story_id) for proper initialization.
        Direct instantiation requires story_state parameter.
        """
        if story_state is None:
            raise ValueError(
                "StoryService requires story_state parameter. "
                "Use StoryService.create(story_id) for proper async initialization."
            )
        
        self.story_id = story_id
        self.story_state = story_state
        
        # Initialize character prompt builder with default template
        self.system_prompt_builder = CharacterMoveSystemPromptBuilder

        # Setup output parser
        self.output_parser = PydanticOutputParser(pydantic_object=AssistantResponse)
        
        # Venice API key is validated in settings
        venice_api_key = settings.VENICE_API_KEY
        self.llm_client = VeniceClient(venice_api_key)
        # Initialize VeniceAI model
        try:
            self.venice_model = VeniceAIChatModel(
                api_key=venice_api_key,
                # model="mistral-31-24b",
                model="venice-uncensored",
                temperature=0.7
            )
            print("✅ VeniceAI integration enabled")
        except Exception as e:
            raise ValueError(f"Failed to initialize VeniceAI model: {e}")

    @classmethod
    async def create(cls, story_id: str) -> 'StoryService':
        """
        Factory method for creating a fully initialized StoryService.
        
        Args:
            story_id: UUID of the story to load
            
        Returns:
            Fully initialized StoryService instance
            
        Raises:
            ValueError: If VENICE_API_KEY environment variable is not set or story data not found.
        """
        story_state = await StoryState.create(story_id)
        return cls(story_id, story_state=story_state)

    def _generate_story_messages(self) -> list[BaseMessage]:
        messages = []

        system_prompt = self.system_prompt_builder(
            character=self.story_state.character
        ).with_current_reality(
            self.story_state.get_last_scene_description()["environmental_context"]
        ).build()

        print("*" * 100)
        print("SYSTEM PROMPT:")
        print(system_prompt)
        print("*" * 100)

        messages.append(SystemMessage(content=system_prompt))

        for item in self.story_state.get_chat_history():
            if item["author_type"] == "user":
                messages.append(HumanMessage(content=item["content"]))
            elif item["author_type"] == "bot":
                messages.append(AIMessage(content=item["content"]))

        return messages


    async def _generate_bot_response(self) -> str:
        logger.info("Generating bot response...")

        messages = self._generate_story_messages()
        response = await self.venice_model.ainvoke(messages)
        return str(response.content)

    # async def _update_character(self, user_message: str) -> None:
    #     logger.info(f"Updating character configs based on user message: {user_message}")

    #     embeddings = await self._get_user_message_embeddings(user_message)
    #     self.story_state.update_character_configs(embeddings)
    
    async def _get_user_message_embeddings(self, user_message: str) -> list[float]:
        embeddings = await self.llm_client.embed([user_message])
        return embeddings[0]

    async def _update_chat_history(self, message: str, author_user: bool = True) -> None:
        scene_description = await self._update_scene_description(
            actor="user" if author_user else self.story_state.character.name,
            message=message
        )
        if author_user:
            self.story_state.add_user_message(message, scene_description)
        else:
            self.story_state.add_character_message(message, scene_description)

    async def _update_scene_description(self, actor: str, message: str) -> dict[str, str]:
        """
        Update scene description based on the latest message.
        
        Args:
            actor: Who is speaking ("user" or character name)
            message: The message content
            
        Returns:
            Dict with updated 'companion_side' and 'character_side' descriptions
        """
        # Create user prompt with previous scene and action
        prompt_template = Template(MOVE_SCENE_DESCRIPTION_USER_PROMPT)
        last_description = self.story_state.get_last_scene_description()
        user_prompt = prompt_template.render({
            "companion_side": last_description["companion_side"],
            "character_side": last_description["character_side"],
            "actor": actor,
            "message": message,
            "character_name": self.story_state.character.base_personality["name"],
            "in_universe_self_description": self.story_state.character.base_personality["in-universe_self_description"],
            "sensory_origin_memory": self.story_state.character.base_personality["sensory_origin_memory"],
            "character_native_deflection": self.story_state.character.base_personality["character_native_deflection"],
            "traits": self.story_state.character.base_personality["traits"],
            "core_principles": self.story_state.character.base_personality["core_principles"],
            "physical_tells": self.story_state.character.base_personality["physical_tells"],
            "speech_patterns": self.story_state.character.base_personality["speech_patterns"]
        })

        llm_communicator = LLMCommunicator(llm_model=self.venice_model)
        scene_description = await llm_communicator.generate_structured_response(
            system_prompt=MOVE_SCENE_DESCRIPTION_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=MoveSceneDescriptionResponse
        )
        
        return {
            "companion_side": scene_description.companion_side,
            "character_side": scene_description.character_side,
            "environmental_context": scene_description.environmental_context
        }

    async def process_user_message(self, message: str) -> None:
        logger.info(f"Processing user message: {message}")

        await self._update_chat_history(message, author_user=True)
        # await asyncio.gather(
        #     self._update_chat_history(message, author_user=True),
        #     # self._update_character(message)
        # )

        bot_response = await self._generate_bot_response()

        await self._update_chat_history(bot_response, author_user=False)

        logger.info("Updating story state...")
        await self.story_state.save_state()

    def get_chat_history(self) -> list[ChatItem]:
        return self.story_state.get_chat_history()

    def get_initial_scene_description(self) -> str:
        return self.story_state.get_last_scene_description()["companion_side"]
