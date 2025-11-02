"""
Location service module containing business logic for location operations.
"""

import logging

from app.dao.location_dao import LocationDAO
from app.models.responses import LocationSummary, LocationsResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LocationService:
    """Service class handling location business logic."""

    def __init__(self):
        """Initialize the location service."""
        self.location_dao = LocationDAO()

    async def get_locations_list(self) -> LocationsResponse:
        """
        Get a list of all locations with their basic information.
        
        Returns:
            LocationsResponse: Response containing list of location summaries
        """
        try:
            logger.info("Fetching locations list")
            
            # Get all locations from DAO
            locations = await self.location_dao.get_locations()
            
            # Transform locations to response format
            location_summaries = [
                LocationSummary(
                    id=location.id,
                    name=location.name
                )
                for location in locations
            ]
            
            logger.info(f"Successfully fetched {len(location_summaries)} locations")
            
            return LocationsResponse(locations=location_summaries)
            
        except Exception as e:
            logger.error(f"Error fetching locations list: {e}")
            raise