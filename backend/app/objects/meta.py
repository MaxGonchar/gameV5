from typing import Any


class MetaData:
    def __init__(self, data: dict[str, Any]):
        self.initial_scene_description: str = data["initial_scene_description"]
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "initial_scene_description": self.initial_scene_description
        }
