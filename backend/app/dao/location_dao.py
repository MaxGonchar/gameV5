from pathlib import Path
from typing import Any, Optional
from app.objects.location import Location

from .yaml_file_handler import YamlFileHandler


class LocationDAO:
    def __init__(
        self,
        locations_dir: str = "data",
        yaml_handler: Optional[YamlFileHandler] = None,
    ):
        self.locations_dir = Path(locations_dir)
        self.yaml_handler = yaml_handler or YamlFileHandler()

    async def get_location(self) -> Location:
        path = self.locations_dir / "location.yaml"
        data = await self._read_yaml(path)
        return Location(data)
    
    async def _read_yaml(self, file_path: Path) -> dict[str, Any]:
        data = await self.yaml_handler.read_yaml_file(file_path)
        if not data or not isinstance(data, dict):
            raise ValueError(f"Invalid location data in {file_path}")
        return data
