"""
Location service module containing business logic for location operations.
"""

from app.core.config import get_logger
from app.dao.location_dao import LocationDAO
from app.objects.location import Location
from app.models.responses import LocationSummary, LocationsResponse
from app.exceptions import (
    EntityNotFoundException,
    DataValidationException,
    ServiceException
)

logger = get_logger(__name__)


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
            
        Raises:
            EntityNotFoundException: If locations data not found
            DataValidationException: If location data is invalid
            ServiceException: For other processing errors
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
            
        except (EntityNotFoundException, DataValidationException):
            # DAO-level exceptions - add service context but let them bubble up
            logger.warning("Location data issue while fetching list")
            raise  # Let DAO exceptions bubble up with original context
            
        except Exception as e:
            logger.error(f"Unexpected error fetching locations list: {e}", exc_info=True)
            raise ServiceException(
                "Failed to fetch locations due to unexpected error",
                details={
                    "original_error": str(e)
                }
            )