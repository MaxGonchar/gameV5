from typing import Any


class MetaData:
    def __init__(self, data: dict[str, Any]):
        self.initial_scene_description: str = data["initial_scene_description"]
