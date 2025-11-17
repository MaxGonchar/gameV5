"""
Stories service module containing business logic for story operations.
"""

from app.core.config import settings
from app.dao.story_dao import StoryDAO
from app.dao.character_dao import CharacterDAO

from app.objects.meta import MetaData
from app.objects.story_state import StoryState
from app.models.responses import StorySummary, StoriesResponse
from app.models.requests import CreateStoryRequest
from app.services.llm_communicator import LLMCommunicator
from app.llm.venice_ai import VeniceAIChatModel
from app.models.session_context import SessionContextResponse, build_session_context_prompt
from pathlib import Path
from app.core.config import get_logger

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
        
        # Initialize Venice model for story context generation
        venice_api_key = settings.VENICE_API_KEY
        try:
            self.venice_model = VeniceAIChatModel(
                api_key=venice_api_key,
                model="mistral-31-24b",
                temperature=0.7
            )
            logger.info("✅ VeniceAI integration enabled for story context generation")
        except Exception as e:
            raise ValueError(f"Failed to initialize VeniceAI model: {e}")
        
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
            ValueError: If character not found or LLM generation fails
            Exception: For other story creation errors
        """
        try:
            logger.info(f"Creating new story '{request.story_title}' for character '{request.character_id}'")

            # Get character for context generation
            character = await self.character_dao.get_character(request.character_id)
            
            # Generate session context using LLM
            input_data = {
                "character": character,
                "request": request
            }
            
            system_prompt, user_prompt = build_session_context_prompt(input_data)
            
            session_context = await self.llm_communicator.generate_structured_response(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_model=SessionContextResponse
            )
            
            # Create story metadata
            story_meta = MetaData(data={
                "title": request.story_title,
                "description": f"Story created for character {character.name}",
                "session_context": session_context.dict()
            })
            
            # Use character's data path to create story
            character_path = Path(settings.DATA_PATH) / "characters" / f"{character.id}.yaml"
            story_id = await self.story_dao.create_story(
                character_path=character_path,
                story_meta=story_meta
            )

            # Create StoryState entity and fill the character related data
            story_state = await StoryState.create(story_id=story_id)
            story_state.add_story_context_character_data(
                {
                    "companion": session_context.companion,
                    "forbidden_concepts": session_context.forbidden_concepts,
                    "current_reality": session_context.current_reality,
                    "goal": session_context.goal,
                    "memories": [
                        {
                            "event_description": item.event_description,
                            "in_character_reflection": item.in_character_reflection
                        } for item in session_context.memories
                    ],
                    "confused_phrase": session_context.confused_phrase
                }
            )
            await story_state.save_state()

            logger.info(f"Successfully created story with ID: {story_id}")
            return story_id
            
        except Exception as e:
            logger.exception(f"Error creating story '{request.story_title}': {e}")
            raise
    
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
