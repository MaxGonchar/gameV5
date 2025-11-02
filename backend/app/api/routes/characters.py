"""
Characters API endpoints.
"""

from fastapi import APIRouter, HTTPException
import logging

from app.models.responses import CharactersResponse
from app.services.character_service import CharacterService

# TODO: move logger configuration to main.py
# check other files for similar logger setups
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Character service will be initialized lazily on first use
character_service = None

async def get_character_service():
    """Get or create the character service instance."""
    global character_service
    if character_service is None:
        character_service = CharacterService()
    return character_service

@router.get("/characters", response_model=CharactersResponse)
async def get_characters():
    """
    Get list of all available characters.
    
    Returns:
        CharactersResponse: List of characters with their basic information
    """
    try:
        logger.info("Processing get characters request")
        
        service = await get_character_service()
        characters_response = await service.get_characters_list()
        
        logger.info(f"Successfully returned {len(characters_response.characters)} characters")
        return characters_response
        
    except Exception as e:
        logger.error(f"Error getting characters: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )