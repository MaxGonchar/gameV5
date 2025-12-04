"""
Dependency injection providers for FastAPI routes.

This module contains all the dependency providers that create and configure
service instances for use in API endpoints through FastAPI's dependency injection system.
"""

# # Standard library imports
from typing import Annotated

# # Third-party imports
from fastapi import Depends, Path

# # Local application imports
from app.services.character_service import CharacterService
from app.services.dialogue_summary_service import DialogueSummaryService
from app.services.stories_service import StoriesService

# Import all service classes that will be used as dependencies
from app.services.story_service import StoryService


# Story-related dependency providers
async def get_story_service(story_id: str = Path(...)) -> StoryService:
    """Create StoryService instance for the given story."""
    return await StoryService.create(story_id)


def get_dialogue_summary_service(story_id: str = Path(...)) -> DialogueSummaryService:
    """Create DialogueSummaryService instance for the given story."""
    return DialogueSummaryService(story_id)


# Character and Stories service dependency providers
def get_character_service() -> CharacterService:
    """Create CharacterService instance."""
    return CharacterService()


def get_stories_service() -> StoriesService:
    """Create StoriesService instance."""
    return StoriesService()


# Type aliases for cleaner dependency injection in route functions
StoryServiceDep = Annotated[StoryService, Depends(get_story_service)]
DialogueServiceDep = Annotated[
    DialogueSummaryService, Depends(get_dialogue_summary_service)
]
CharacterServiceDep = Annotated[CharacterService, Depends(get_character_service)]
StoriesServiceDep = Annotated[StoriesService, Depends(get_stories_service)]
