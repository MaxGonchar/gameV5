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
