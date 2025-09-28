from app.chat_types import ChatItem


class ChatHistory:
    def __init__(self, data: list[ChatItem] | None):
        self.data = self._init_data(data)

    def add_message(self, author_id: str, author_type: str, author_name: str, content: str) -> None:
        message: ChatItem = {
            "id": str(self._last_id() + 1),
            "author_id": author_id,
            "author_type": author_type,
            "author_name": author_name,
            "content": content
        }
        self.data.append(message)

    def get_data(self) -> list[ChatItem]:
        return self.data

    def __iter__(self):
        return iter(self.data)

    def _init_data(self, data: list[ChatItem] | None) -> list[ChatItem]:
        if data is None:
            return []

        data.sort(key=lambda x: int(x["id"]))
        return data

    def _last_id(self):
        if not self.data:
            return 0
        return int(self.data[-1]["id"])
    
    def get_messages_up_to_id(self, target_id: str) -> list[ChatItem]:
        """
        Extract chat history up to and including the specified item ID.
        
        Args:
            target_id: Target chat item ID
            
        Returns:
            List of chat items up to the target (inclusive)
            
        Raises:
            ValueError: If target_id is not found in chat history
        """
        result = []
        found = False
        
        for item in self.data:
            result.append(item)
            if item["id"] == target_id:
                found = True
                break
        
        if not found:
            raise ValueError(f"Chat item with ID '{target_id}' not found in chat history")
        
        return result
    
    def trim_messages_up_to_id(self, up_to_id: str) -> int:
        """
        Remove chat items from history up to and including the specified ID.
        
        Args:
            up_to_id: Last item ID to remove (inclusive)
            
        Returns:
            Number of items removed
            
        Raises:
            ValueError: If up_to_id is not found in chat history
        """
        # Find the index of the target item
        target_index = None
        for i, item in enumerate(self.data):
            if item["id"] == up_to_id:
                target_index = i
                break
        
        if target_index is None:
            raise ValueError(f"Chat item with ID '{up_to_id}' not found in chat history")
        
        # Calculate how many items will be removed
        items_to_remove = target_index + 1
        
        # Keep only items after the target
        self.data = self.data[target_index + 1:]
        
        return items_to_remove
