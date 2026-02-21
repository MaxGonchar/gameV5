"""
Story service module containing business logic and prompt processing for interactive story generation.
"""

# # Standard library imports
import asyncio
import logging
import os
from typing import Any

# # Third-party imports
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.output_parsers import PydanticOutputParser

# # Local application imports
from app.builders import CharacterMoveSystemPromptBuilder
from app.builders.character_move_prompt_builder import build_character_messages_chain
from app.chat_types import ChatItem
from app.core.config import get_logger, settings
from app.exceptions import (
    DataValidationException,
    EntityNotFoundException,
    ExternalServiceException,
    InitializationException,
    ServiceException,
)
from app.llm.venice_ai import VeniceAIChatModel
from app.llm.venice_client import VeniceClient
from app.models.assistant_response import AssistantResponse
from app.models.emotional_impact import (
    EmotionalImpactAnalysisResponse,
    build_emotional_impact_prompt,
)
from app.models.emotional_impact_semantic import (
    EmotionalImpactSemanticAnalysisResponse,
    build_semantic_emotional_impact_prompt,
)
from app.models.behavior_mode import (
    build_behavioral_mode_generation_prompt,
    BehavioralModeResponse,
)
from app.models.first_level_memory import build_first_level_memory_prompt, FirstLevelMemoryResponse
from app.models.scene_description import (
    MoveSceneDescriptionResponse,
    build_scene_description_prompt,
)
from app.objects.story_state import StoryState
from app.services.llm_communicator import LLMCommunicator

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
        story_state: StoryState | None = None,
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
                model=settings.DEFAULT_STORY_MODEL,
                temperature=settings.DEFAULT_STORY_TEMPERATURE,
            )
            logger.info(
                f"✅ VeniceAI integration enabled - Model: {settings.DEFAULT_STORY_MODEL}, Temperature: {settings.DEFAULT_STORY_TEMPERATURE}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize VeniceAI model: {e}")
            raise InitializationException(
                "Failed to initialize VeniceAI model for story service",
                details={
                    "model": settings.DEFAULT_STORY_MODEL,
                    "temperature": settings.DEFAULT_STORY_TEMPERATURE,
                    "api_key_present": bool(venice_api_key),
                    "original_error": str(e),
                },
            )

        # Initialize LLM communicator (single instance for reuse)
        self.llm_communicator = LLMCommunicator(llm_model=self.venice_model)

    @classmethod
    async def create(cls, story_id: str) -> "StoryService":
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
                details={"story_id": story_id, "original_error": str(e)},
            )

        except (DataValidationException, EntityNotFoundException):
            # Re-raise custom exceptions with story context
            logger.error(f"Data validation failed for story {story_id}")
            raise

        except Exception as e:
            logger.error(
                f"Unexpected error creating StoryService for story {story_id}: {e}",
                exc_info=True,
            )
            raise InitializationException(
                "Failed to initialize story service due to unexpected error",
                details={"story_id": story_id, "original_error": str(e)},
            )

    def _generate_story_messages(self) -> list[BaseMessage]:
        """Generate LangChain messages using the dedicated function."""
        # Currently character can not start conversation, it means that history will always start with user message.
        # Last remembered message can match the last message in the history.
        # In case of first level memory creation, last remembered message will be the last message in the history.
        # All following dialogue should start from last user message.
        # So if dialogue was reset to the point of first level memory creation, we should start from the last remembered message,
        # which should be the last user message triggered the memory summarization.
        chat_history = self.story_state.get_chat_history(
            after_message_id=self.story_state.character.get_last_remembered_message_id()
        )
        if not chat_history and (last_message_id := self.story_state.character.get_last_remembered_message_id()) is not None:
            last_message = self.story_state.chat_history.get_message_by_id(
                last_message_id
            )
            if last_message:
                chat_history = [last_message]

        return build_character_messages_chain(
            character=self.story_state.character,
            chat_history=chat_history,
            current_reality=self.story_state.get_last_scene_description()[
                "environmental_context"
            ],
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

    async def _update_chat_history(
        self, message: str, author_user: bool = True
    ) -> None:
        scene_description = await self._update_scene_description(
            actor="user" if author_user else self.story_state.character.name,
            message=message,
        )
        if author_user:
            self.story_state.add_user_message(message, scene_description)
        else:
            self.story_state.add_character_message(message, scene_description)

    async def _update_scene_description(
        self, actor: str, message: str
    ) -> dict[str, str]:
        """
        Update scene description based on the latest message.

        Args:
            actor: Who is speaking ("user" or character name)
            message: The message content

        Returns:
            Dict with updated 'companion_side' and 'character_side' descriptions
        """
        # Use function to build prompts
        system_prompt, user_prompt = build_scene_description_prompt(
            {"story_state": self.story_state, "actor": actor, "message": message}
        )

        scene_description = await self.llm_communicator.generate_structured_response(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=MoveSceneDescriptionResponse,
        )

        logger.debug(
            f"Goal: {self.story_state.character.current_goal.get('desired_state')}, Status: {scene_description.goal_status}"
        )

        return {
            "companion_side": scene_description.companion_side,
            "character_side": scene_description.character_side,
            "environmental_context": scene_description.environmental_context,
        }

    async def _calculate_emotional_impact(self, user_message: str) -> EmotionalImpactAnalysisResponse:
        system_Prompt, user_prompt = build_emotional_impact_prompt(
            {
                "character": self.story_state.character,
                "recent_history": self.story_state.get_chat_history(),
                "user_message": user_message,
            }
        )
        logger.debug("Calculating emotional impact...")
        # logger.debug(f"System Prompt: {system_Prompt}")
        logger.debug(f"User Prompt: {user_prompt}")

        emotional_impact = await self.llm_communicator.generate_structured_response(
            system_prompt=system_Prompt,
            user_prompt=user_prompt,
            response_model=EmotionalImpactAnalysisResponse,
        )
        return emotional_impact
    
    async def _get_emotional_state_semantic(self, user_message: str) -> EmotionalImpactSemanticAnalysisResponse:
        """Get the character's current emotional state."""
        system_prompt, user_prompt = build_semantic_emotional_impact_prompt(
            {
                "name": self.story_state.character.name,
                "core_fears": self.story_state.character.base_personality["core_fears"],
                "core_needs": self.story_state.character.base_personality["core_needs"],
                "unique_sensitivities": self.story_state.character.base_personality["unique_sensitivities"],
                "mental_states": [
                    {
                        "type": state["type"],
                        "current_level": state["current_level"],
                        "scale": [
                            {
                                "level": level["level"],
                                "semantic_meaning": level["semantic_meaning"],
                                "character_experience": level["character_experience"],
                                "requirements_to_reach": level["requirements_to_reach"],
                                "requirements_to_leave": level["requirements_to_leave"],
                            } for level in state["scale"]
                        ],
                        "transition_notes": state["transition_notes"],
                    } for state in self.story_state.character.mental_states
                ],
                "recent_history": self.story_state.get_chat_history(after_message_id=self.story_state.character.get_last_remembered_message_id()),
                "current_mental_states": [
                    {
                        "type": state["type"],
                        "current_level": state["current_level"],
                        "reasoning": state["current_level_reasoning"],
                    } for state in self.story_state.character.mental_states
                ],
                "user_message": user_message,
            }
        )

        logger.debug("Getting emotional state semantic analysis...")
        # logger.debug(f"System Prompt: {system_prompt}")
        logger.debug(f"User Prompt: {user_prompt}")

        emotional_state = await self.llm_communicator.generate_structured_response(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=EmotionalImpactSemanticAnalysisResponse,
        )
        return emotional_state

    def _get_character_mental_state_snapshot(self) -> dict[str, str]:
        """Get a snapshot of the character's current mental state."""

        mental_state_snapshot = {
            state["type"]: state["current_level"]
            for state in self.story_state.character.mental_states
        }

        return mental_state_snapshot
    
    def _get_emotional_shift(
            self,
            initial_snapshot: dict[str, Any],
            updated_snapshot: dict[str, Any],
            impact_data: dict[str, Any],
        ) -> dict[str, Any]:
        """Calculate emotional shifts based on mental state snapshots."""
        mental_states = {}
        for before, after, impact in zip(
            sorted(list(initial_snapshot.items()), key=lambda x: x[0]),
            sorted(list(updated_snapshot.items()), key=lambda x: x[0]),
            sorted(list(impact_data["mental_state_impacts"].items()), key=lambda x: x[0]),
        ):
            mental_states[before[0]] = {
                "before_level": before[1],
                "after_level": after[1],
                "reasoning": impact[1]["reasoning"],
            }

        emotional_snapshot = {
            "mental_states": mental_states,
        }
        return emotional_snapshot
    
    def _is_emotional_state_changed(self, initial_snapshot: dict[str, str], updated_snapshot: dict[str, str]) -> bool:
        for name, level in initial_snapshot.items():
            if level.lower() != updated_snapshot[name].lower():
                return True
        return False

    async def _create_first_level_memory_item(self) -> None:
        # get last not summarized chat history items
        last_memory_message_id = self.story_state.character.get_last_remembered_message_id()
        if last_memory_message_id is not None:
            history_items_to_summarize = self.story_state.chat_history.get_messages_after_id(
                last_memory_message_id)
        else:
            history_items_to_summarize = self.story_state.chat_history.get_data()

        # Build prompt for first-level memory item
        system_prompt, user_prompt = build_first_level_memory_prompt(
            {
                "character": self.story_state.character,
                "episode_messages": history_items_to_summarize,
            }
        )
        logger.debug("Creating first-level memory item...")
        # logger.debug(f"System Prompt: {system_prompt}")
        # logger.debug(f"User Prompt: {user_prompt}")

        # call LLM to generate first-level memory item
        memory_item = await self.llm_communicator.generate_structured_response(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=FirstLevelMemoryResponse,
        )

        # add memory item to character
        memory_item_dict = memory_item.model_dump()
        self.story_state.character.add_first_level_memory_item(
            {
                "start_message_id": history_items_to_summarize[0]["id"],
                "end_message_id": history_items_to_summarize[-1]["id"],
                "episode_title": memory_item_dict["episode_title"],
                "emotional_arc_summary": memory_item_dict["emotional_arc_summary"],
                "narrative_summary": memory_item_dict["narrative_summary"],
                "character_reflections": memory_item_dict["character_reflection"],
                "transition_trigger": memory_item_dict["transition_trigger"],
                "key_exchanges": memory_item_dict["key_exchanges"],
            }
        )
    
    async def _update_behavioral_mode(self) -> None:
        def _build_mental_states(self) -> dict[str, Any]:
            res = {}
            for state in self.story_state.character.mental_states:
                type_ = state["type"]
                current_level = state["current_level"]
                meaning = ""
                character_experience = ""
                for level in state["scale"]:
                    if level["level"].lower() == current_level.lower():
                        meaning = level["semantic_meaning"]
                        character_experience = level["character_experience"]
                        break

                res[type_] = {
                    "current_level": current_level,
                    "meaning": meaning,
                    "character_experience": character_experience,
                }

            return res

        def _build_previous_mode(self) -> dict[str, Any]:
            mode = self.story_state.character.current_behavioral_mode
            return {
                "name": mode["name"],
                "summary": " ".join(
                    [mode["manifestation"], mode["why_here"]]
                ),
                "traits": mode["traits"],
            }

        def _build_recent_history(self) -> list[dict[str, Any]]:
            history = self.story_state.get_chat_history(after_message_id=self.story_state.character.get_last_remembered_message_id())
            return [
                {
                    "author_name": item["author_name"],
                    "author_type": item["author_type"],
                    "content": item["content"],
                    "emotional_shift": item.get("emotional_shift", ""),
                }
             for item in history]
        
        system_prompt, user_prompt = build_behavioral_mode_generation_prompt(
            {
                "character_name": self.story_state.character.name,
                "in_universe_self_description": self.story_state.character.base_personality["in-universe_self_description"],
                "core_principles": self.story_state.character.base_personality["core_principles"],
                "core_fears": self.story_state.character.base_personality["core_fears"],
                "core_needs": self.story_state.character.base_personality["core_needs"],
                "unique_sensitivities": self.story_state.character.base_personality["unique_sensitivities"],
                "communication_patterns": [
                    {
                        "context": {
                            "emotional_state": item["emotional_state"],
                            "typical_situations": item["typical_situations"],
                        },
                        "speech_pattern": {
                            "description": item["speech_patterns"]["description"],
                            "examples": [se for se in item["speech_patterns"]["examples"]],
                            "vocal_tells": [vt for vt in item["speech_patterns"]["vocal_tells"]],
                        },
                        "body_language": {
                            "description": item["body_language"]["description"],
                            "examples": [be for be in item["body_language"]["examples"]],
                            "physical_tells": [pt for pt in item["body_language"]["physical_tells"]],
                        },
                        "reasoning": item["reasoning"],
                    } for item in self.story_state.character.data["communication_patterns"]
                ],
                "mental_states": _build_mental_states(self),
                "previous_mode": _build_previous_mode(self),
                "recent_history": _build_recent_history(self),
            }
        )

        logger.debug("Updating behavioral mode...")
        # logger.debug(f"System Prompt: {system_prompt}")
        # logger.debug(f"User Prompt: {user_prompt}")

        behavioral_mode_response = await self.llm_communicator.generate_structured_response(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=BehavioralModeResponse,
        )

        self.story_state.character.update_behavioral_mode(behavioral_mode_response.model_dump())

    async def _process_user_message(self, message: str) -> None:
        """Process user message and generate bot response.
        Main orchestration method that coordinates the story interaction flow.
        """
        try:
            logger.info(f"Processing user message: {message}")

            # Update scene description based on user message
            scene_description = await self._update_scene_description(
                actor="user", message=message
            )
            self.story_state.add_user_message(message, scene_description)
            # Detect emotional state levels
            new_emotional_state = await self._get_emotional_state_semantic(message)
            logger.debug(f"Semantic Emotional State Result: {new_emotional_state.model_dump()}")

            # update character mental state
            previous_mental_state = self._get_character_mental_state_snapshot()

            self.story_state.character.update_mental_state(
                new_emotional_state.model_dump()["mental_state_impacts"]
            )

            updated_mental_state = self._get_character_mental_state_snapshot()

            emotional_shift = self._get_emotional_shift(
                previous_mental_state,
                updated_mental_state,
                new_emotional_state.model_dump(),
            )

            # create first level memory item on emotional state change
            if self._is_emotional_state_changed(previous_mental_state, updated_mental_state):
                await self._create_first_level_memory_item()
                await self._update_behavioral_mode()

            # Generate and bot response
            bot_response = await self._generate_bot_response()

            # Update scene description based on bot response
            scene_description = await self._update_scene_description(
                actor=self.story_state.character.name, message=bot_response
            )
            self.story_state.add_character_message(bot_response, scene_description, emotional_shift)

            # Persist changes
            logger.info("Saving story state...")
            await self.story_state.save_state()

        except (ExternalServiceException, DataValidationException):
            # LLM communication or response parsing failed - re-raise with context
            logger.error(
                f"LLM operation failed during message processing for story {self.story_id}"
            )
            raise

        except Exception as e:
            logger.error(
                f"Unexpected error processing user message in story {self.story_id}: {e}",
                exc_info=True,
            )
            raise ServiceException(
                "Failed to process user message due to unexpected error",
                details={
                    "story_id": self.story_id,
                    "message_preview": (
                        message[:50] + "..." if len(message) > 50 else message
                    ),
                    "original_error": str(e),
                },
            )
    
    async def _process_user_message_v2(self, message: str) -> None:
        pass
    
    async def process_user_message(self, message: str) -> None:
        await self._process_user_message(message)

    # Façade methods for API routes
    def get_chat_history(self) -> list[ChatItem]:
        """Get chat history for API consumers."""
        return self.story_state.get_chat_history()

    def get_initial_scene_description(self) -> str:
        """Get initial scene description for API consumers."""
        return self.story_state.get_last_scene_description()["companion_side"]
