from typing import Any


class MetaData:
    def __init__(self, data: dict[str, Any]):
        self._data = data
    
    def to_dict(self) -> dict[str, Any]:
        return self._data
