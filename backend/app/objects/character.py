from copy import deepcopy
from typing import Any, TypedDict
import numpy as np

from app.core.config import get_logger

logger = get_logger(__name__)


class MemoryItemType(TypedDict):
    event_description: str
    in_character_reflection: str


class Character:
    def __init__(self, character_data: dict[str, Any]):
        self.data = deepcopy(character_data)
    
    def to_dict(self) -> dict[str, Any]:
        return deepcopy(self.data)
    
    @property
    def current_goal(self) -> dict[str, Any]:
        return self.data.get("goal", {})
    
    @property
    def traits(self) -> list[str]:
        return self._get_from_goal_first("traits", list)
    
    @property
    def speech_patterns(self) -> list[str]:
        return self._get_from_goal_first("speech_patterns", list)
    
    @property
    def physical_tells(self) -> list[str]:
        return self._get_from_goal_first("physical_tells", list)

    def _get_from_goal_first(self, key: str, none_type: type) -> Any:
        value = (
            self.current_goal.get(f"goal_{key}", none_type())
            if self.current_goal
            else self.data["base_personality"].get(key, none_type())
        )

        if not value:
            logger.warning(f"Character '{self.name}' has no '{key}' defined.")

        return value
    
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
    
    def add_items_to_memory(self, items: list[MemoryItemType]) -> None:
        if "memories" not in self.data:
            self.data["memories"] = []

        for item in items:
            self.data["memories"].append(
                {
                    "event_description": item["event_description"],
                    "in_character_reflection": item["in_character_reflection"]
                }
            )

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
