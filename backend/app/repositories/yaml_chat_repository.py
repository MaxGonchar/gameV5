"""
YAML file-based implementation of the chat repository.
"""

import yaml
import os
from typing import List
from .chat_repository_interface import ChatRepositoryInterface
from ..chat_types import ChatItem
from ..core.constants import CHAT_HISTORY_FILE_NAME

class YamlChatRepository(ChatRepositoryInterface):
    """YAML file-based chat repository implementation."""
    
    def __init__(self, file_path: str = CHAT_HISTORY_FILE_NAME):
        """
        Initialize the YAML chat repository.
        
        Args:
            file_path (str): Path to the YAML file (default: from constants)
        """
        self.file_path = file_path
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Ensure the YAML file exists, create if it doesn't."""
        if not os.path.exists(self.file_path):
            self._create_empty_file()
    
    def _create_empty_file(self):
        """Create an empty YAML file with empty list."""
        with open(self.file_path, 'w', encoding='utf-8') as file:
            yaml.dump([], file, default_flow_style=False, allow_unicode=True)
    
    def _load_messages(self) -> List[ChatItem]:
        """Load messages from YAML file."""
        with open(self.file_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    
    def _save_messages(self, messages: List[ChatItem]) -> None:
        """Save messages to YAML file."""
        with open(self.file_path, 'w', encoding='utf-8') as file:
            yaml.dump(messages, file, default_flow_style=False, allow_unicode=True)
    
    def get_all_messages(self) -> List[ChatItem]:
        """
        Retrieve all chat messages from YAML storage.
        
        Returns:
            List[ChatItem]: List of chat messages
        """
        return self._load_messages()
    
    def add_message(self, message: ChatItem) -> None:
        """
        Add a new message to YAML storage.
        
        Args:
            message (ChatItem): Message to add
        """
        messages = self._load_messages()
        messages.append(message)
        self._save_messages(messages)
