from typing import Any


class Location:
    def __init__(self, location_data: dict[str, Any]):
        self.description = location_data["description"]
