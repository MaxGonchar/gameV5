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


class Memory:
    """
memory_items:
  first_level:
    - episode_id: "1"
        behavioral_mode: "cautious_hope" <during the episode>
        start_message_id: "1"
        end_message_id: "15"
        mental_state_progression:
            stress:
                from: "tense"
                to: "wary"
            trust:
                from: "guarded"
                to: "fragile"
            fear:
                from: "alert"
                to: "watchful"
        
        episode_title: "First Careful Steps Toward Trust"

        emotional_arc_summary: |
        My stress began high as the two-legs first approached, every muscle tight and ready to bolt. 
        Through their careful movements and soft voice, the sharp edge of fear gradually dulled. 
        When they offered food without demands, something shifted - not trust, but the smallest 
        crack in my walls. By the time they sat still and let me approach on my terms, I found 
        myself wanting to believe this could be different.
        
        
        narrative_summary: |
        The two-legs named Alex approached my den with cautious respect, maintaining distance 
        and using soft tones. They brought food regularly without forcing interaction. Through 
        consistent, non-threatening behavior, they demonstrated they understood boundaries. 
        I began testing - moving closer, accepting food, observing their patterns. Each 
        interaction where they proved predictable and safe chipped away at my walls.
        
        character_reflection: |
        The two-legs... Alex... they do not move like hunters. Three suns now, food appears 
        but no trap follows. They sit far, make small noises, wait. This is strange-safe. 
        My belly less tight. My ears forward more. The wild-spirit says "watch-watch-watch" 
        but also whispers "maybe-maybe-maybe." I took meat from close-close yesterday. 
        Alex did not grab. Did not shout. Just... watched with soft eyes. Wolves know: 
        patterns that repeat are patterns that matter. Alex's pattern is... careful. 
        Not pack yet. But not danger-danger either.
        
        key_exchanges: <- Transform to full in character voice (he said/did -> I reacted -> reflection)
        - user: "I brought you some food. I'll just leave it here and sit over there."
            character: "*sniffs air cautiously* Grr... *watches from den entrance, tail low*"
            why_important: "First food offering - established non-threatening pattern"
        
        - user: "You don't have to be afraid. I won't hurt you."
            character: "*ears twitch forward slightly* Two-legs makes... promise-sounds? *tests closer, three steps, stops*"
            why_important: "First verbal reassurance - character began associating voice with safety"
        
        - user: "Take your time. I'm not going anywhere."
            character: "*slowly approaches food, eyes locked on Alex* *takes meat quickly, retreats* Grr... but... thank-you-maybe?"
            why_important: "First successful close interaction - breakthrough moment for trust building"
        
        transition_trigger: |
        Alex reached out hand slowly to touch my head. Sudden movement toward vulnerable 
        spot triggered deep instinct-fear, spiking stress sharply. Combined with growing 
        trust creating confusion about how to react. Transitioned from hopeful openness 
        to protective wariness.
"""
    def __init__(self, data: dict[str, Any]):
        self.data = deepcopy(data)

    def marshal(self) -> dict[str, Any]:
        return deepcopy(self.data)

    def get_last_first_level_memory_message_id(self) -> str | None:
        first_level_memories = self.data.get("first_level", [])
        if not first_level_memories:
            return None
        last_memory = first_level_memories[-1]
        return last_memory.get("end_message_id", None)

    def get_first_level_memory_items(self) -> list[dict[str, Any]]:
        return self.data.get("first_level", [])
    
    def add_first_level_memory_item(self, item: dict[str, Any]) -> None:
        if "first_level" not in self.data:
            self.data["first_level"] = []

        item["id"] = self._get_last_first_level_memory_id() + 1
        self.data["first_level"].append(item)
    
    def _get_last_first_level_memory_id(self) -> int:
        first_level_memories = self.data.get("first_level", [])
        if not first_level_memories:
            return 0
        last_memory = first_level_memories[-1]
        return int(last_memory.get("id", 0))


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

    def get_current_mental_states(self) -> dict[str, str]:
        return {
            state["type"]: state["current"] for state in self.data
        }

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


class BehavioralModes:
    def __init__(self, modes_data: list[dict[str, Any]]):
        self.modes_data = deepcopy(modes_data)

    def current_behavioral_mode(self, mental_states: dict[str, str]) -> str:
        for mode in self.modes_data:
            if self._check_mode_match(mode, mental_states):
                return mode["mode_name"]
        return "default_mode"

    
    def marshal(self) -> list[dict[str, Any]]:
        return deepcopy(self.modes_data)
    
    def get_behavior(self, mental_states: dict[str, str]) -> dict[str, Any] | None:
        for mode in self.modes_data:
            if self._check_mode_match(mode, mental_states):
                return {
                    "traits": mode.get("traits", []),
                    "speech_patterns": mode.get("speech_patterns", []),
                    "physical_tells": mode.get("physical_tells", []),
                }
        return None

    def _check_mode_match(self, mode: dict[str, Any], current_state_levels: dict[str, str]) -> bool:
        """
        mode: {
            "mode_name": "survival_edge",
            "trigger_conditions": {
                "stress": ["high", "overwhelming"],
                "trust": ["low", "fragile"]
            }
        }
        current_state_levels: {"stress": "high", "trust": "low", "hope": "diminishing"}
        """
        for state_name, required_levels in mode["trigger_conditions"].items():
            # Check if this mental state exists in current state
            if state_name not in current_state_levels:
                return False
            
            # Check if current level is in the list of required levels
            current_level = current_state_levels[state_name]
            if current_level not in required_levels:
                return False
        
        # All conditions satisfied
        return True


class Character:
    def __init__(self, character_data: dict[str, Any]):
        self.data = deepcopy(character_data)
        # TODO: Remove mental_states data from character to not copy it twice
        self._mental_states: MentalStates = MentalStates(
            self.data.get("mental_states", [])
        )
        self._behavioral_modes: BehavioralModes = BehavioralModes(
            self.data.get("behavioral_modes", [])
        )
        self._memory_items: Memory = Memory(
            self.data.get("memory_items", {})
        )

    def to_dict(self) -> dict[str, Any]:
        data = deepcopy(self.data)
        data["mental_states"] = self._mental_states.marshal()
        data["behavioral_modes"] = self._behavioral_modes.marshal()
        data["memory_items"] = self._memory_items.marshal()
        return data

    @property
    def current_goal(self) -> dict[str, Any]:
        return self.data.get("goal", {})

    @property
    def traits(self) -> list[str]:
        # return self._get_from_goal_first("traits", list)
        return self._get_from_behavioral_mode_first("traits")

    @property
    def speech_patterns(self) -> list[str]:
        # return self._get_from_goal_first("speech_patterns", list)
        return self._get_from_behavioral_mode_first("speech_patterns")

    @property
    def physical_tells(self) -> list[str]:
        # return self._get_from_goal_first("physical_tells", list)
        return self._get_from_behavioral_mode_first("physical_tells")
    
    def _get_from_behavioral_mode_first(self, key: str) -> Any:
        current_states = self._mental_states.get_current_mental_states()
        behavior = self._behavioral_modes.get_behavior(current_states)

        logger.debug(f"Getting '{key}' for character '{self.name}' from behavioral modes")
        logger.debug(f"Current mental states: {current_states}")
        logger.debug(f"Matched behavior: {behavior}")

        if behavior:
            return behavior[key]
        
        return self.data["base_personality"][key]


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
    
    @property
    def current_behavioral_mode(self) -> str:
        current_states = self._mental_states.get_current_mental_states()
        return self._behavioral_modes.current_behavioral_mode(current_states)

    def update_mental_state(self, impact: dict[str, Any]) -> None:

        for state, impact in impact.items():
            logger.debug(f"Updating mental state: {state}")
            logger.debug(f"Impact: {impact['change']}")
            logger.debug(f"Impact: {impact['reasoning']}")
            self._mental_states.update_state(state, impact["change"])

    def get_last_remembered_message_id(self) -> str | None:
        return self._memory_items.get_last_first_level_memory_message_id()

    def get_first_level_memory_items(self) -> list[dict[str, Any]]:
        return self._memory_items.get_first_level_memory_items()

    def add_first_level_memory_item(self, item: dict[str, Any]) -> None:
        self._memory_items.add_first_level_memory_item(item)
