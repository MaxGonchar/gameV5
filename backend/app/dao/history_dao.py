"""
Data Access Object for history management.

This module provides a HistoryDAO class that handles loading and saving
history data from/to a single YAML file.
"""

from typing import List, cast
from pathlib import Path
from .path_manager import PathManager

from .yaml_file_handler import YamlFileHandler
from app.chat_types import ChatItem
from app.objects import ChatHistory
from app.exceptions import DataValidationException
from app.core.config import get_logger

logger = get_logger(__name__)


# TODO: refactor:
# make methods smaller, focused on single tasks
# consider reusing "FileSystemOperations" where applicable
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
        story_id: str,
        yaml_handler: YamlFileHandler | None = None,
        path_manager: PathManager | None = None
    ):
        """
        Initialize the history DAO.

        Args:
            history_file: Path to the history YAML file (default: from settings)
            yaml_handler: YAML file handler dependency
        """
        self.yaml_handler = yaml_handler or YamlFileHandler()
        self.path_manager = path_manager or PathManager()
        self.history_file = Path(self.path_manager.get_story_history_file(story_id))
        # TODO: make creation logic to "create_story" responsibility
        self.history_file.parent.mkdir(parents=True, exist_ok=True)

    async def load_history(self) -> ChatHistory:
        """
        Load history from the YAML file.

        Returns:
            ChatHistory object containing all history messages

        Raises:
            YamlException, FileOperationException: From yaml_handler (bubbled up)
            DataValidationException: If history data format is invalid
        """
        return ChatHistory(await self._read_yaml())
    
    async def _read_yaml(self) -> list[ChatItem]:
        """
        Read history from the YAML file and return as a list of ChatItem.

        Returns:
            List of ChatItem objects

        Raises:
            YamlException, FileOperationException: From yaml_handler (bubbled up)
            DataValidationException: If history data format is invalid
        """
        if not self.history_file.exists():
            logger.debug(f"History file does not exist, returning empty history: {self.history_file}")
            return []
        
        data = await self.yaml_handler.read_yaml_file(self.history_file)
        
        if not data:
            logger.debug(f"History file is empty, returning empty history: {self.history_file}")
            return []
        
        # History must be a list of chat items
        if not isinstance(data, list):
            raise DataValidationException(
                f"Invalid history data format in {self.history_file}",
                details={
                    "file_path": str(self.history_file),
                    "expected_type": "list",
                    "actual_type": type(data).__name__
                }
            )
        
        try:
            # Process list of chat items - all must be valid
            chat_items = []
            for i, item in enumerate(data):
                if not isinstance(item, dict):
                    raise DataValidationException(
                        f"Invalid chat item at index {i} in {self.history_file}",
                        details={
                            "file_path": str(self.history_file),
                            "item_index": i,
                            "expected_type": "dict",
                            "actual_type": type(item).__name__
                        }
                    )
                chat_items.append(ChatItem(**item))
            
            logger.debug(f"Successfully loaded {len(chat_items)} chat items from {self.history_file}")
            return chat_items
        except TypeError as e:
            # ChatItem construction failed
            raise DataValidationException(
                f"Invalid chat item data structure in {self.history_file}",
                details={
                    "file_path": str(self.history_file),
                    "original_error": str(e)
                }
            )

    async def save(self, history: ChatHistory) -> None:
        """
        Save history to the YAML file.

        Args:
            history: ChatHistory object containing messages to save

        Raises:
            YamlException, FileOperationException: From yaml_handler (bubbled up)
        """
        # ChatItem is a TypedDict, so it's compatible with Dict[str, Any]
        data = cast(List[dict], history.get_data())
        logger.debug(f"Saving {len(data)} chat items to {self.history_file}")
        await self.yaml_handler.write_yaml_file(self.history_file, data)
        logger.info(f"Successfully saved chat history to {self.history_file}")


# Backward compatibility alias
ChatHistoryDAO = HistoryDAO