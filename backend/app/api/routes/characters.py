"""
Characters API endpoints.
"""

from fastapi import APIRouter, HTTPException
from http import HTTPStatus
import logging

from app.models.responses import CharactersResponse
from app.services.character_service import CharacterService
from app.core.config import get_logger
from app.exceptions import (
    EntityNotFoundException,
    DataValidationException,
    ServiceException
)

logger = get_logger(__name__)

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
        
    except EntityNotFoundException as e:
        logger.warning(f"Characters data not found: {e.message}")
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="No characters found"
        )
    
    except DataValidationException as e:
        logger.error(f"Character data validation error: {e.message}")
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Character data validation failed. Please contact support."
        )
    
    except ServiceException as e:
        logger.error(f"Service error getting characters: {e.message}")
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Internal service error. Please try again."
        )
    
    except Exception as e:
        logger.exception(f"Unexpected error getting characters: {str(e)}")
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again."
        )