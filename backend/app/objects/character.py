# # Standard library imports
from copy import deepcopy
from typing import Any, TypedDict

# # Third-party imports
import numpy as np

# # Local application imports
from app.core.config import get_logger

logger = get_logger(__name__)


class MemoryItemType(TypedDict):
    event_description: str
    in_character_reflection: str


class RangeDict:
    """A dict-like class that maps integer values to levels based on ranges."""

    def __init__(self, levels):
        """
        Initialize with a list of level definitions.

        Args:
            levels: List of dicts with 'level' (str) and 'range' ([min, max]) keys
        """
        self.levels = levels

    def __getitem__(self, key):
        """
        Get the level name for a given integer value.

        Args:
            key: Integer value to look up

        Returns:
            The level name (str) if found

        Raises:
            KeyError: If the value doesn't fall within any range
        """
        if not isinstance(key, int):
            raise TypeError(f"Key must be an integer, got {type(key).__name__}")

        for level_def in self.levels:
            min_val, max_val = level_def["range"]
            if min_val <= key <= max_val:
                return level_def["level"]

        raise KeyError(f"No level found for value {key}")

    def get(self, key, default=None):
        """Get the level for a key, returning default if not found."""
        try:
            return self[key]
        except KeyError:
            return default

    def __contains__(self, key):
        """Check if a value falls within any range."""
        try:
            self[key]
            return True
        except KeyError:
            return False

    def __repr__(self):
        return f"RangeDict({self.levels})"


class MentalStates:
    def __init__(self, data: list[dict[str, Any]]):
        self.data = deepcopy(data)
        self.direction_sign = {
            "increase": 1,
            "decrease": -1,
        }

    def marshal(self) -> list[dict[str, Any]]:
        return deepcopy(self.data)

    def update_state(self, state_name: str, change: str) -> None:
        for state in self.data:
            if state["type"].lower() == state_name.lower():
                logger.debug(
                    f"Updating mental state '{state_name}' with change '{change}'"
                )
                level, direction = change.split("_")

                # handle case "no_change"
                if level == "no" and direction == "change":
                    logger.debug(f"No change for mental state '{state_name}'")
                    continue

                impact = state["impact_rate"][level] * self.direction_sign[direction]

                new_numeric_level = self._calculate_numeric_level(state, impact)
                state["current_numeric"] = new_numeric_level
                self._set_current_level(state)

    def _calculate_numeric_level(self, state: dict[str, Any], impact: int) -> int:
        current = state["current_numeric"]
        return min(
            max(
                state["change_mechanics"]["min"],
                current + impact,
            ),
            state["change_mechanics"]["max"],
        )

    def _set_current_level(self, state: dict[str, Any]) -> None:
        range_dict = RangeDict(state["scale"])
        state["current"] = range_dict.get(state["current_numeric"], "Unknown")


class Character:
    def __init__(self, character_data: dict[str, Any]):
        self.data = deepcopy(character_data)
        # TODO: Remove mental_states data from character to not copy it twice
        self._mental_states: MentalStates = MentalStates(
            self.data.get("mental_states", [])
        )

    def to_dict(self) -> dict[str, Any]:
        data = deepcopy(self.data)
        data["mental_states"] = self._mental_states.marshal()
        return data

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
                    "in_character_reflection": item["in_character_reflection"],
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

    @property
    def mental_states(self) -> list[dict[str, Any]]:
        return self._mental_states.marshal()

    def update_mental_state(self, impact: dict[str, Any]) -> None:

        for state, impact in impact.items():
            logger.debug(f"Updating mental state: {state}")
            logger.debug(f"Impact: {impact['change']}")
            logger.debug(f"Impact: {impact['reasoning']}")
            self._mental_states.update_state(state, impact["change"])
