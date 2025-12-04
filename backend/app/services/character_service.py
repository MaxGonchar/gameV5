"""
Character service module containing business logic for character operations.
"""

# # Local application imports
from app.core.config import get_logger
from app.dao.character_dao import CharacterDAO
from app.exceptions import (
    DataValidationException,
    EntityNotFoundException,
    ServiceException,
)
from app.models.responses import CharactersResponse, CharacterSummary

logger = get_logger(__name__)


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
                CharacterSummary(id=character.id, name=character.name)
                for character in characters
            ]

            logger.info(f"Successfully fetched {len(character_summaries)} characters")

            return CharactersResponse(characters=character_summaries)

        except (EntityNotFoundException, DataValidationException) as e:
            # DAO-level exceptions - add service context but let them bubble up
            logger.warning(f"Character data issue while fetching list: {e.message}")
            raise  # Let DAO exceptions bubble up with original context

        except Exception as e:
            logger.error(
                f"Unexpected error fetching characters list: {e}", exc_info=True
            )
            raise ServiceException(
                "Failed to fetch characters list due to unexpected error",
                details={"original_error": str(e)},
            )
