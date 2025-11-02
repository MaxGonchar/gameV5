"""
Character service module containing business logic for character operations.
"""

import logging

from app.dao.story_dao import StoryDAO
from app.dao.character_dao import CharacterDAO
from app.dao.location_dao import LocationDAO
from app.objects.meta import MetaData
from app.models.responses import StorySummary, StoriesResponse
from app.models.requests import CreateStoryRequest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StoriesService:
    """Service class handling story business logic."""

    def __init__(self):
        """Initialize the story service."""
        self.story_dao = StoryDAO()
        self.character_dao = CharacterDAO()
        self.location_dao = LocationDAO()

    async def create_story(self, request: CreateStoryRequest) -> str:
        """
        Create a new story based on the provided request data.
        
        Args:
            request (CreateStoryRequest): Data required to create a new story.
        
        Returns:
            str: The ID of the newly created story.
        """
        try:
            logger.info("Creating a new story")
            
            story_id = await self.story_dao.create_story(
                character_path=self.character_dao.get_character_folder(request.character_id),
                location_path=self.location_dao.get_location_path(request.location_id),
                story_meta=MetaData({"initial_scene_description": request.init_scene_description})
            )
            logger.info(f"Successfully created story with ID: {story_id}")
            return story_id
        except Exception as e:
            logger.error(f"Error creating story: {e}")
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
                location=story["location_name"],
                character=story["character_name"]
            )
            for story in await self.story_dao.get_stories_summary()
        ]
        return StoriesResponse(stories=summaries)
