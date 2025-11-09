from copy import deepcopy
from typing import Any
import numpy as np


class Character:
    def __init__(self, character_data: dict[str, Any]):
        self.data = deepcopy(character_data)
    
    def to_dict(self) -> dict[str, Any]:
        return deepcopy(self.data)
    
    @property
    def id(self) -> str:
        return self.data["id"]
    
    @property
    def name(self) -> str:
        return self.data["base_personality"]["name"]
    
    @property
    def base_personality(self) -> dict[str, Any]:
        return self.data["base_personality"]
    
    @property
    def general(self) -> dict[str, Any]:
        return self.data["general"]

    @property
    def memories(self) -> list[str]:
        return self.data.get("memories", [])

    @property
    def story_context(self) -> dict[str, Any]:
        return self.data.get("story_context", {})
    
    @story_context.setter
    def story_context(self, value: dict[str, Any]) -> None:
        self.data["story_context"] = value

    def add_story_context_data(self, story_context_data: dict[str, Any]) -> None:
        if memories := story_context_data.get("memories"):

            if "memories" not in self.data:
                self.data["memories"] = []
            self.data["memories"].extend(memories)
            story_context_data.pop("memories")

        self.data["story_context"] = story_context_data
