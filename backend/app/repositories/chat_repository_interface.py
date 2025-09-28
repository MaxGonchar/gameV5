"""
Chat repository interface for persistent storage operations.
"""

from abc import ABC, abstractmethod
from typing import List
from ..chat_types import ChatItem

class ChatRepositoryInterface(ABC):
    """Abstract interface for chat repository operations."""
    
    @abstractmethod
    def get_all_messages(self) -> List[ChatItem]:
        """
        Retrieve all chat messages from storage.
        
        Returns:
            List[ChatItem]: List of chat messages
        """
        pass
    
    @abstractmethod
    def add_message(self, message: ChatItem) -> None:
        """
        Add a new message to storage.
        
        Args:
            message (ChatItem): Message to add
        """
        pass
