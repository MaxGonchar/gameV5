from copy import deepcopy
from typing import Any
import numpy as np


class Character:
    """
    Represents a character in the game.
    Is initialized from a dictionary.

    Required keys are:
    assistant: instructions for the llm assistant
    character: character's configuration
    """

    def __init__(self, character_data: dict[str, Any]):
        try:
            self.assistant = character_data["assistant"]
            self.character = character_data["character"]
            self.variables = character_data["variables"]
            self.name = self.variables["name"]
            self.id = self.variables["id"]
        except KeyError as e:
            raise ValueError(f"Invalid character_data, missing key: {e}")


        self.parameters, self.dynamic_directives = self._init_dynamic_configs(
            character_data
        )

        self.dynamic_configs = character_data.get("dynamic_configs", [])

    def _init_dynamic_configs(
        self, data: dict[str, Any]
    ) -> tuple[dict[str, Any], dict[str, Any]] | tuple[None, None]:
        """
        Initializes optional dynamic configurations from the provided data.
        """
        if not data.get("dynamic_configs"):
            return None, None

        parameters = data.get("parameters", {})
        dynamic_configs = {}

        for config in data["dynamic_configs"]:

            if parameters.get(config["parameter"]) is None:
                parameters[config["parameter"]] = config["default"]

            dynamic_configs[config["parameter"]] = config

        return parameters, dynamic_configs

    def to_prompt_dict(self) -> dict[str, Any]:
        return {"assistant": self.assistant, "character": self.character}

    def to_dict(self) -> dict[str, Any]:
        data = {
            "variables": self.variables,
            "assistant": self.assistant,
            "character": self.character,
        }

        if self.parameters:
            data["parameters"] = self.parameters
        if self.dynamic_configs:
            data["dynamic_configs"] = self.dynamic_configs

        return data
    
    def update_dynamic_configs_according_to_message_embeddings(self, embeddings: list[float]) -> None:
        for config in self.dynamic_configs:
            self._update_config(config, embeddings)

    def _update_config(self, config: dict, embeddings: list[float]) -> None:
        positive_axis = config["dynamic_directives"]["positive"]["axis"]
        negative_axis = config["dynamic_directives"]["negative"]["axis"]

        impact = self._calculate_impact(positive_axis, negative_axis, embeddings)
        impact = self.map_to_sigmoid(impact)

        parameter = self.parameters[config["parameter"]]
        print(f"Current parameter '{config['parameter']}': {parameter}")

        if decay_level := float(config.get("decay_level")):
            parameter *= decay_level
            print(f"Decay applied: {decay_level} on {config['parameter']} -> {parameter}")

        updated_parameter = float(parameter + impact) # numpy float64 to float
        self.parameters[config["parameter"]] = max(min(updated_parameter, 1.0), -1.0)

        print(f"impact: {impact}")
        print(f"Updated parameter '{config['parameter']}': {self.parameters[config['parameter']]}")

        self._update_character_according_to_config(config)
    
    def _update_character_according_to_config(self, config: dict) -> None:
        param_value = self.parameters[config["parameter"]]

        for level in config["levels"]:
            level_min, level_max = level["range"]
            if level_min <= param_value <= level_max:
                property_ = deepcopy(level["character_impacts"][0])
                prop_name = property_["title"]
                self._correct_property(prop_name, property_)
                break
    
    def _correct_property(self, prop_name: str, property_: dict) -> None:
        for current_property in self.character:
            print(f"Checking property: {current_property['title']} to match {prop_name}")
            if current_property["title"].lower() == prop_name.lower():
                print(f"Found property: {property_['title']}")
                self.character.remove(current_property)
                self.character.append(property_)
                break

    # TODO: extract cover with tests
    def _calculate_impact(self, positive_axis: list[float], negative_axis: list[float], message_vector: list[float]) -> float:
        """calculate cosine similarities and return the difference"""
        pos_sim = np.dot(message_vector, positive_axis) / (np.linalg.norm(message_vector) * np.linalg.norm(positive_axis))
        neg_sim = np.dot(message_vector, negative_axis) / (np.linalg.norm(message_vector) * np.linalg.norm(negative_axis))
        return pos_sim - neg_sim

    def map_to_sigmoid(self, impact: float, scale_factor=1) -> float:
        """Squash the impact to a range of -1 to 1."""
        sigmoid = 1 / (1 + np.exp(-impact * scale_factor))
        # map to -1 ... 1 range
        return 2 * sigmoid - 1
    
    def get_memory(self) -> list[str]:
        """
        Get the character's memory summaries.
        
        Returns:
            List of memory summary strings
        """
        for item in self.character:
            if item.get("title", "").lower() == "memory":
                memory_value = item.get("value", [])
                if isinstance(memory_value, list):
                    return memory_value
                elif isinstance(memory_value, str):
                    return [memory_value]
                else:
                    return []
        return []
    
    def add_item_to_memory(self, summary: str) -> None:
        """
        Add a new memory summary to the character.
        
        Args:
            summary: New summary to add to memory
        """
        # Find existing memory item
        memory_item = None
        for item in self.character:
            if item.get("title", "").lower() == "memory":
                memory_item = item
                break
        
        # If no memory item exists, create one
        if memory_item is None:
            memory_item = {
                "title": "Memory",
                "value": []
            }
            self.character.append(memory_item)
        
        # Ensure value is a list
        if not isinstance(memory_item["value"], list):
            memory_item["value"] = [memory_item["value"]] if memory_item["value"] else []
        
        # Add the new summary
        memory_item["value"].append(summary)
