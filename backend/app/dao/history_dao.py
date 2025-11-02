"""
Data Access Object for history management.

This module provides a HistoryDAO class that handles loading and saving
history data from/to a single YAML file.
"""

from typing import List, cast
from pathlib import Path

from .yaml_file_handler import YamlFileHandler
from app.chat_types import ChatItem
from app.objects import ChatHistory


class HistoryDAO:
    """
    Data Access Object for history management.

    Handles:
    - Loading history from a single YAML file
    - Saving history to a single YAML file
    - Managing history messages in chronological order

    This abstraction allows for easy replacement with database or other storage
    systems in the future while maintaining the same interface.
    """

    def __init__(
        self,
        history_file: str = "data/chat_history/chat_history.yaml",
        yaml_handler: YamlFileHandler | None = None,
    ):
        """
        Initialize the history DAO.

        Args:
            history_file: Path to the history YAML file (default: "data/chat_history/chat_history.yaml")
            yaml_handler: YAML file handler dependency
        """
        self.history_file = Path(history_file)
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self.yaml_handler = yaml_handler or YamlFileHandler()

    async def load_history(self) -> ChatHistory:
        """
        Load history from the YAML file.

        Returns:
            ChatHistory object containing all history messages

        Raises:
            yaml.YAMLError: If YAML parsing fails
        """
        return ChatHistory(await self._read_yaml())
    
    async def _read_yaml(self) -> list[ChatItem]:
        """
        Read history from the YAML file and return as a list of ChatItem.

        Returns:
            List of ChatItem objects

        Raises:
            yaml.YAMLError: If YAML parsing fails
        """
        if not self.history_file.exists():
            # Return empty history for new files
            return []
        data = await self.yaml_handler.read_yaml_file(self.history_file)
        if not data:
            return []
        elif isinstance(data, list):
            return [ChatItem(**item) if isinstance(item, dict) else item for item in data]
        else:
            return [ChatItem(**data) if isinstance(data, dict) else data]

    async def save(self, history: ChatHistory) -> None:
        """
        Save history to the YAML file.

        Args:
            history: ChatHistory object containing messages to save

        Raises:
            yaml.YAMLError: If YAML serialization fails
            OSError: If file writing fails
        """
        # ChatItem is a TypedDict, so it's compatible with Dict[str, Any]
        data = cast(List[dict], history.get_data())
        await self.yaml_handler.write_yaml_file(self.history_file, data)


# Backward compatibility alias
ChatHistoryDAO = HistoryDAO