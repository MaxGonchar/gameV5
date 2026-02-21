# # Standard library imports
from copy import deepcopy
from typing import Any, TypedDict

# # Third-party imports
import numpy as np

# # Local application imports
from app.core.config import get_logger

logger = get_logger(__name__)


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

    def marshal(self) -> list[dict[str, Any]]:
        return deepcopy(self.data)

    def update_state(self, state_name: str, change: str, reasoning: str) -> None:
        for state in self.data:
            if state["type"].lower() == state_name.lower():
                logger.debug(
                    f"Updating mental state '{state_name}' to level '{change}'"
                )
                state["current_level"] = change
                state["current_level_reasoning"] = reasoning

    def get_current_mental_states(self) -> dict[str, str]:
        return {
            state["type"]: state["current_level"] for state in self.data
        }


class BehavioralMode:
    def __init__(self, mode_data: dict[str, Any]):
        self.data = deepcopy(mode_data)
    
    def marshal(self) -> dict[str, Any]:
        return deepcopy(self.data)

    def get_instructions(self) -> dict[str, Any]:
        return {
            "traits": self.data["traits"],
            "speech_patterns": self.data["speech_patterns"],
            "physical_tells": self.data["physical_tells"],
        }


# TODO: get rid of dict like key calls, move to abstractions
class Character:
    def __init__(self, character_data: dict[str, Any]):
        self.data = deepcopy(character_data)
        # TODO: Remove mental_states data from character to not copy it twice
        self._mental_states: MentalStates = MentalStates(
            self.data.get("mental_states", [])
        )
        self._behavioral_mode: BehavioralMode = BehavioralMode(
            self.data.get("behavioral_mode", {})
        )
        self._memory_items: Memory = Memory(
            self.data.get("memory_items", {})
        )

    def to_dict(self) -> dict[str, Any]:
        data = deepcopy(self.data)
        data["mental_states"] = self._mental_states.marshal()
        data["behavioral_mode"] = self._behavioral_mode.marshal()
        data["memory_items"] = self._memory_items.marshal()
        return data

    @property
    def current_goal(self) -> dict[str, Any]:
        return self.data.get("goal", {})

    @property
    def traits(self) -> list[str]:
        return self._behavioral_mode.get_instructions()["traits"]

    @property
    def speech_patterns(self) -> list[str]:
        return self._behavioral_mode.get_instructions()["speech_patterns"]

    @property
    def physical_tells(self) -> list[str]:
        return self._behavioral_mode.get_instructions()["physical_tells"]

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
    def memories(self) -> dict[str, Any]:
        return self.data.get("memory_items", {})

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
    def current_behavioral_mode(self) -> dict[str, Any]:
        return self._behavioral_mode.marshal()

    def update_mental_state(self, impact: dict[str, Any]) -> None:

        for state, data in impact.items():
            logger.debug(f"Updating mental state: {state} to level '{data}'")
            self._mental_states.update_state(state, data["level"], data["reasoning"])
    
    def update_behavioral_mode(self, mode_data: dict[str, Any]) -> None:
        mode_data["mental_states_combination"] = {
            state["type"]: state["current_level"] for state in self._mental_states.data
        }
        self._behavioral_mode = BehavioralMode(mode_data)

    def get_last_remembered_message_id(self) -> str | None:
        return self._memory_items.get_last_first_level_memory_message_id()

    def get_first_level_memory_items(self) -> list[dict[str, Any]]:
        return self._memory_items.get_first_level_memory_items()

    def add_first_level_memory_item(self, item: dict[str, Any]) -> None:
        self._memory_items.add_first_level_memory_item(item)
