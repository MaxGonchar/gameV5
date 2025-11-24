"""
Story service module containing business logic and prompt processing for interactive story generation.
"""

import os
from typing import Any
import logging
import asyncio

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage

from app.core.config import settings, get_logger
from app.chat_types import ChatItem
from app.llm.venice_ai import VeniceAIChatModel
from app.llm.venice_client import VeniceClient
from app.models.assistant_response import AssistantResponse
from app.builders import CharacterMoveSystemPromptBuilder
from app.builders.character_move_prompt_builder import build_character_messages_chain
from app.objects.story_state import StoryState
from app.services.llm_communicator import LLMCommunicator
from app.models.scene_description import MoveSceneDescriptionResponse, build_scene_description_prompt
from app.exceptions import (
    InitializationException,
    EntityNotFoundException,
    DataValidationException,
    ExternalServiceException,
    ServiceException
)

logger = get_logger(__name__)


class StoryService:
    """Main façade and orchestrator for interactive story sessions.
    
    Serves as the primary interface for API routes and coordinates business logic
    between specialized components for story generation.
    
    Responsibilities:
    - Story interaction orchestration (process_user_message)
    - API façade methods (get_chat_history, get_initial_scene_description)
    - Async initialization via factory method (create)
    
    Uses specialized components:
    - build_character_messages_chain() for message formatting
    - build_scene_description_prompt() for scene prompts
    - LLMCommunicator for all LLM interactions
    - StoryState for data persistence
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
        
        # Initialize Venice API components
        venice_api_key = settings.VENICE_API_KEY
        self.llm_client = VeniceClient(venice_api_key)
        
        # Initialize VeniceAI model
        try:
            self.venice_model = VeniceAIChatModel(
                api_key=venice_api_key,
                model="venice-uncensored",
                temperature=0.7
            )
            logger.info("✅ VeniceAI integration enabled")
        except Exception as e:
            logger.error(f"Failed to initialize VeniceAI model: {e}")
            raise InitializationException(
                "Failed to initialize VeniceAI model for story service",
                details={
                    "model": "venice-uncensored",
                    "api_key_present": bool(venice_api_key),
                    "original_error": str(e)
                }
            )
        
        # Initialize LLM communicator (single instance for reuse)
        self.llm_communicator = LLMCommunicator(llm_model=self.venice_model)

    @classmethod
    async def create(cls, story_id: str) -> 'StoryService':
        """
        Factory method for creating a fully initialized StoryService.
        
        Args:
            story_id: UUID of the story to load
            
        Returns:
            Fully initialized StoryService instance
            
        Raises:
            InitializationException: If service initialization fails
            EntityNotFoundException: If story data not found
            DataValidationException: If story data is invalid
        """
        try:
            story_state = await StoryState.create(story_id)
            return cls(story_id, story_state=story_state)
            
        except ValueError as e:
            # StoryState.create() data validation errors
            logger.error(f"Story state creation failed for story {story_id}: {e}")
            raise EntityNotFoundException(
                f"Failed to load story data",
                details={
                    "story_id": story_id,
                    "original_error": str(e)
                }
            )
            
        except (DataValidationException, EntityNotFoundException):
            # Re-raise custom exceptions with story context
            logger.error(f"Data validation failed for story {story_id}")
            raise
            
        except Exception as e:
            logger.error(f"Unexpected error creating StoryService for story {story_id}: {e}", exc_info=True)
            raise InitializationException(
                "Failed to initialize story service due to unexpected error",
                details={
                    "story_id": story_id,
                    "original_error": str(e)
                }
            )

    def _generate_story_messages(self) -> list[BaseMessage]:
        """Generate LangChain messages using the dedicated function."""
        return build_character_messages_chain(
            character=self.story_state.character,
            chat_history=self.story_state.get_chat_history(),
            current_reality=self.story_state.get_last_scene_description()["environmental_context"]
        )


    async def _generate_bot_response(self) -> str:
        """Generate bot response using LLM communicator."""
        logger.info("Generating bot response...")

        messages = self._generate_story_messages()
        return await self.llm_communicator.generate_chat_response(messages)

    async def _get_user_message_embeddings(self, user_message: str) -> list[float]:
        """Get embeddings for user message (currently unused)."""
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
        # Use function to build prompts
        system_prompt, user_prompt = build_scene_description_prompt({
            "story_state": self.story_state,
            "actor": actor,
            "message": message
        })

        scene_description = await self.llm_communicator.generate_structured_response(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=MoveSceneDescriptionResponse
        )

        print("*" * 100)
        print("Goal:", scene_description.goal_status)
        print("*" * 100)
        
        return {
            "companion_side": scene_description.companion_side,
            "character_side": scene_description.character_side,
            "environmental_context": scene_description.environmental_context
        }

    async def process_user_message(self, message: str) -> None:
        """Process user message and generate bot response.
        
        Main orchestration method that coordinates the story interaction flow.
        
        Raises:
            ExternalServiceException: If LLM communication fails
            DataValidationException: If response parsing fails
            ServiceException: For other processing errors
        """
        try:
            logger.info(f"Processing user message: {message}")

            # Add user message with scene description
            await self._update_chat_history(message, author_user=True)

            # Generate and add bot response
            bot_response = await self._generate_bot_response()
            await self._update_chat_history(bot_response, author_user=False)

            # Persist changes
            logger.info("Saving story state...")
            await self.story_state.save_state()
            
        except (ExternalServiceException, DataValidationException):
            # LLM communication or response parsing failed - re-raise with context
            logger.error(f"LLM operation failed during message processing for story {self.story_id}")
            raise
            
        except Exception as e:
            logger.error(f"Unexpected error processing user message in story {self.story_id}: {e}", exc_info=True)
            raise ServiceException(
                "Failed to process user message due to unexpected error",
                details={
                    "story_id": self.story_id,
                    "message_preview": message[:50] + "..." if len(message) > 50 else message,
                    "original_error": str(e)
                }
            )

    # Façade methods for API routes
    def get_chat_history(self) -> list[ChatItem]:
        """Get chat history for API consumers."""
        return self.story_state.get_chat_history()

    def get_initial_scene_description(self) -> str:
        """Get initial scene description for API consumers."""
        return self.story_state.get_last_scene_description()["companion_side"]
