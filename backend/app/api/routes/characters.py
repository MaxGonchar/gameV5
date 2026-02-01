"""
Characters API endpoints.
"""

# # Standard library imports
import logging
from http import HTTPStatus

# # Third-party imports
from fastapi import APIRouter, HTTPException

# # Local application imports
from app.core.config import get_logger
from app.dependencies import CharacterServiceDep
from app.exceptions import (
    DataValidationException,
    EntityNotFoundException,
    ServiceException,
)
from app.models.responses import CharactersResponse

logger = get_logger(__name__)

router = APIRouter()


@router.get("/characters", response_model=CharactersResponse)
async def get_characters(character_service: CharacterServiceDep):
    """
    Get list of all available characters.

    Returns:
        CharactersResponse: List of characters with their basic information
    """
    try:
        logger.info("Processing get characters request")

        characters_response = await character_service.get_characters_list()

        logger.info(
            f"Successfully returned {len(characters_response.characters)} characters"
        )
        return characters_response

    except EntityNotFoundException as e:
        logger.warning(f"Characters data not found: {e.message}")
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="No characters found"
        )

    except DataValidationException as e:
        logger.error(f"Character data validation error: {e.message}")
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Character data validation failed. Please contact support.",
        )

    except ServiceException as e:
        logger.error(f"Service error getting characters: {e.message}")
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Internal service error. Please try again.",
        )

    except Exception as e:
        logger.exception(f"Unexpected error getting characters: {str(e)}")
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again.",
        )
