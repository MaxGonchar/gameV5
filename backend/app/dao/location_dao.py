from pathlib import Path
from typing import Optional
import asyncio
from app.objects.location import Location

from .yaml_file_handler import YamlFileHandler


class LocationDAO:
    """
    Data Access Object for location configurations.
    
    Handles loading and storing locations from/to YAML files.
    Structure: {locations_dir}/{location_id}/location.yaml
    """
    
    def __init__(
        self, 
        locations_dir: str = "data/locations",
        yaml_handler: Optional[YamlFileHandler] = None
    ) -> None:
        """
        Initialize the location DAO.
        
        Args:
            locations_dir: Directory containing location subdirectories (default: "data/locations")
            yaml_handler: YAML file handler dependency
        """
        self.locations_dir = Path(locations_dir)
        self.yaml_handler = yaml_handler or YamlFileHandler()

    async def get_location(self, id: str) -> Location:
        """
        Load a specific location by ID.
        
        Args:
            id: UUID of the location
            
        Returns:
            Location object
            
        Raises:
            FileNotFoundError: If location file doesn't exist
            yaml.YAMLError: If YAML parsing fails
        """
        location_file = self.locations_dir / id / "location.yaml"
        
        if not location_file.exists():
            raise FileNotFoundError(f"Location with id {id} not found at {location_file}")
        
        location_data = await self.yaml_handler.read_yaml_file(location_file)
        
        if not isinstance(location_data, dict):
            raise ValueError(f"Invalid location data format in {location_file}, expected dict but got {type(location_data)}")
        
        return Location(location_data)

    async def get_locations(self) -> list[Location]:
        """
        Load all locations from the locations directory.
        
        Returns:
            List of Location objects
            
        Raises:
            FileNotFoundError: If locations directory doesn't exist
            yaml.YAMLError: If YAML parsing fails for any location
        """
        if not self.locations_dir.exists():
            return []
        
        # Collect all location file paths
        location_files = []
        for location_dir in self.locations_dir.iterdir():
            if location_dir.is_dir():
                location_file = location_dir / "location.yaml"
                if location_file.exists():
                    location_files.append(location_file)
        
        if not location_files:
            return []
        
        # Load all location files concurrently
        async def load_location(location_file: Path) -> Location | None:
            """Load a single location file, returning None if it fails."""
            try:
                location_data = await self.yaml_handler.read_yaml_file(location_file)
                if isinstance(location_data, dict):
                    return Location(location_data)
                else:
                    print(f"Warning: Invalid location data format in {location_file}, expected dict but got {type(location_data)}")
                    return None
            except Exception as e:
                # Log the error but continue with other locations
                print(f"Warning: Failed to load location from {location_file}: {e}")
                return None
        
        # Load all locations concurrently
        location_results = await asyncio.gather(
            *[load_location(file) for file in location_files],
            return_exceptions=False
        )
        
        # Filter out None results (failed loads)
        locations = [loc for loc in location_results if loc is not None]
        
        return locations
