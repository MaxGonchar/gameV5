"""
Locations API endpoints.
"""

from fastapi import APIRouter, HTTPException
import logging

from app.models.responses import LocationsResponse
from app.services.location_service import LocationService
from app.core.config import get_logger

logger = get_logger(__name__)

router = APIRouter()

# Location service will be initialized lazily on first use
location_service = None

async def get_location_service():
    """Get or create the location service instance."""
    global location_service
    if location_service is None:
        location_service = LocationService()
    return location_service

@router.get("/locations", response_model=LocationsResponse)
async def get_locations():
    """
    Get list of all available locations.
    
    Returns:
        LocationsResponse: List of locations with their basic information
    """
    try:
        logger.info("Processing get locations request")
        
        service = await get_location_service()
        locations_response = await service.get_locations_list()
        
        logger.info(f"Successfully returned {len(locations_response.locations)} locations")
        return locations_response
        
    except Exception as e:
        logger.error(f"Error getting locations: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )