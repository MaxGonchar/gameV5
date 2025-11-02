"""
Character service module containing business logic for character operations.
"""

import logging

from app.dao.character_dao import CharacterDAO
from app.models.responses import CharacterSummary, CharactersResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CharacterService:
    """Service class handling character business logic."""

    def __init__(self):
        """Initialize the character service."""
        self.character_dao = CharacterDAO()

    async def get_characters_list(self) -> CharactersResponse:
        """
        Get a list of all characters with their basic information.
        
        Returns:
            CharactersResponse: Response containing list of character summaries
        """
        try:
            logger.info("Fetching characters list")
            
            # Get all characters from DAO
            characters = await self.character_dao.get_characters()
            
            # Transform characters to response format
            character_summaries = [
                CharacterSummary(
                    id=character.id,
                    name=character.name
                )
                for character in characters
            ]
            
            logger.info(f"Successfully fetched {len(character_summaries)} characters")
            
            return CharactersResponse(characters=character_summaries)
            
        except Exception as e:
            logger.error(f"Error fetching characters list: {e}")
            raise