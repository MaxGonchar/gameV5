"""
Stories service module containing business logic for story operations.
"""

# # Standard library imports
from pathlib import Path

# # Local application imports
from app.core.config import get_logger, settings
from app.dao.character_dao import CharacterDAO
from app.dao.story_dao import StoryDAO
from app.exceptions import (
    BusinessLogicException,
    DataValidationException,
    EntityNotFoundException,
    ExternalServiceException,
    InitializationException,
    ServiceException,
)
from app.llm.venice_ai import VeniceAIChatModel
from app.models.requests import CreateStoryRequest
from app.models.responses import StoriesResponse, StorySummary
from app.models.session_context import (
    SessionContextResponse,
    build_session_context_prompt,
)
from app.objects.meta import MetaData
from app.objects.story_state import StoryState
from app.services.llm_communicator import LLMCommunicator

logger = get_logger(__name__)


class StoriesService:
    """Service class handling story creation and management business logic.

    Responsibilities:
    - Story creation orchestration with session context generation
    - Story listing and summary operations
    - LLM-based session context generation using Venice AI

    Uses specialized components:
    - build_session_context_prompt() for prompt building
    - LLMCommunicator for all LLM interactions
    - StoryDAO, CharacterDAO for data persistence
    """

    def __init__(self):
        """Initialize the story service."""
        self.story_dao = StoryDAO()
        self.character_dao = CharacterDAO()

        # TODO: anti-pattern: Initialize Venice model for story context generation
        venice_api_key = settings.VENICE_API_KEY
        try:
            self.venice_model = VeniceAIChatModel(
                api_key=venice_api_key,
                model=settings.DEFAULT_STORY_CONTEXT_MODEL,
                temperature=settings.DEFAULT_STORY_CONTEXT_TEMPERATURE,
            )
            logger.info(
                f"✅ VeniceAI integration enabled for story context generation - Model: {settings.DEFAULT_STORY_CONTEXT_MODEL}, Temperature: {settings.DEFAULT_STORY_CONTEXT_TEMPERATURE}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize VeniceAI model: {e}")
            raise InitializationException(
                "Failed to initialize VeniceAI model for story service",
                details={
                    "model": settings.DEFAULT_STORY_CONTEXT_MODEL,
                    "temperature": settings.DEFAULT_STORY_CONTEXT_TEMPERATURE,
                    "original_error": str(e),
                },
            )

        # Initialize LLM communicator (single instance for reuse)
        self.llm_communicator = LLMCommunicator(llm_model=self.venice_model)

    async def create_story(self, request: CreateStoryRequest) -> str:
        """
        Create a new story based on the provided request data.

        Main orchestration method that coordinates story creation flow.

        Args:
            request (CreateStoryRequest): Data required to create a new story.

        Returns:
            str: The ID of the newly created story.

        Raises:
            BusinessLogicException: If character not found or business rules violated
            ExternalServiceException: If LLM communication fails
            ServiceException: For other story creation errors
        """
        try:
            logger.info(
                f"Creating new story '{request.story_title}' for character '{request.character_id}'"
            )

            # Get character for context generation
            character = await self.character_dao.get_character(request.character_id)

            # Generate session context using LLM
            input_data = {"character": character, "request": request}

            system_prompt, user_prompt = build_session_context_prompt(input_data)

            session_context = await self.llm_communicator.generate_structured_response(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_model=SessionContextResponse,
            )

            # Create story metadata
            story_meta = MetaData(
                data={
                    "title": request.story_title,
                    "initial_scene_description": session_context.meeting_scene_description.dict(),
                }
            )

            # Use character's data path to create story
            # TODO: move path creation logic to DAO
            character_path = (
                Path(settings.DATA_BASE_DIR) / "characters" / f"{character.id}"
            )
            story_id = await self.story_dao.create_story(
                character_path=character_path, story_meta=story_meta
            )

            # Create StoryState entity and fill the character related data
            story_state = await StoryState.create(story_id=story_id)
            story_state.add_story_context_character_data(
                {
                    "companion": session_context.companion,
                    "forbidden_concepts": session_context.forbidden_concepts,
                    "current_reality": session_context.current_reality,
                    "goal": session_context.goal,
                    "confused_phrase": session_context.confused_phrase,
                }
            )
            await story_state.save_state()

            logger.info(f"Successfully created story with ID: {story_id}")
            return story_id

        except EntityNotFoundException as e:
            # Character not found - could be from initial lookup or StoryState.create()
            logger.warning(f"Character not found during story creation: {e.message}")
            raise BusinessLogicException(
                "Cannot create story: Character not found",
                details={
                    "character_id": request.character_id,
                    "story_title": request.story_title,
                    "original_error": e.message,
                },
            )

        except ValueError as e:
            # StoryState.create() data validation errors
            logger.error(f"Story state creation failed due to data issues: {e}")
            # story_id is defined by this point since StoryDAO.create_story() succeeded
            current_story_id = locals().get("story_id", "unknown")
            raise InitializationException(
                "Failed to initialize story state due to data validation error",
                details={
                    "story_id": current_story_id,
                    "story_title": request.story_title,
                    "original_error": str(e),
                },
            )

        except DataValidationException as e:
            # Could be from LLM response parsing or DAO operations
            logger.error(
                f"Data validation failed during story creation for '{request.story_title}': {e.message}"
            )
            raise ServiceException(
                "Story creation failed due to data validation error",
                details={
                    "story_title": request.story_title,
                    "character_id": request.character_id,
                    "validation_error": e.message,
                },
            )

        except ExternalServiceException as e:
            # LLM communication failed - add story context and re-raise
            logger.error(
                f"LLM service failed during story creation for '{request.story_title}': {e.message}"
            )
            # Let the original exception bubble up - it already has good technical context
            raise

        except Exception as e:
            logger.error(
                f"Unexpected error creating story '{request.story_title}': {e}",
                exc_info=True,
            )
            raise ServiceException(
                "Failed to create story due to unexpected error",
                details={
                    "story_title": request.story_title,
                    "character_id": request.character_id,
                    "original_error": str(e),
                },
            )

    async def get_stories_summary(self) -> StorySummary:
        """
        Retrieve a summary of all stories.

        Returns:
            StorySummary: A summary of all stories.
        """
        summaries = [
            StorySummary(
                id=story["id"],
                title=story["title"],
            )
            for story in await self.story_dao.get_stories_summary()
        ]
        return StoriesResponse(stories=summaries)
