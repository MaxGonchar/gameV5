# # Standard library imports
from typing import Any


class Location:
    def __init__(self, location_data: dict[str, Any]):
        try:
            self.description = location_data["description"]
            self.name = location_data["name"]
            self.id = location_data["id"]
        except KeyError as e:
            raise ValueError(f"Invalid location_data, missing key: {e}")
