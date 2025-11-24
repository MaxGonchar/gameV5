import asyncio
from typing import Any
from enum import Enum

from app.objects.character import Character
from app.objects.location import Location
from app.objects.chat_history import ChatHistory
from app.objects.meta import MetaData
from app.dao.character_dao import CharacterDAO
# from app.dao.location_dao import LocationDAO
from app.dao.history_dao import HistoryDAO
from app.dao.meta_dao import MetaDAO
from app.dao.path_manager import path_manager
from app.chat_types import ChatItem


class AuthorType(Enum):
    USER = "user"
    BOT = "bot"


class StoryState:
    """
    Manages the state for a specific story.
    
    Handles loading and saving of story-specific data including:
    - Characters
    - Locations  
    - History
    - Meta data
    
    Use StoryState.create() factory method for async initialization.
    """
    
    # Class constants for user identification
    USER_ID = "user"
    USER_NAME = "User"
    
    def __init__(
        self, 
        story_id: str,
        *,  # Force keyword-only parameters
        character: Character | None = None,
        chat_history: ChatHistory | None = None,
        meta: MetaData | None = None
    ):
        """
        Initialize the story state with required data.
        
        Args:
            story_id: UUID of the story
            character: Character instance (required)
            chat_history: ChatHistory instance (required)
            meta: MetaData instance (required)
            
        Raises:
            ValueError: If any required parameter is None
            
        Note: Use StoryState.create(story_id) for proper initialization.
        Direct instantiation requires all parameters.
        """
        if character is None or chat_history is None or meta is None:
            raise ValueError(
                "StoryState requires character, chat_history, and meta parameters. "
                "Use StoryState.create(story_id) for proper async initialization."
            )
        
        self.story_id = story_id
        self.character = character
        self.chat_history = chat_history
        self.meta = meta
        self.character_id = character.id

        # Initialize DAOs with story-specific paths (for saving operations)
        self.character_dao = CharacterDAO(characters_dir=path_manager.get_story_characters_dir(story_id))
        self.chat_history_dao = HistoryDAO(history_file=path_manager.get_story_history_file(story_id))
        self.meta_dao = MetaDAO(meta_dir=path_manager.get_story_dir(story_id))

    @classmethod
    async def create(cls, story_id: str) -> 'StoryState':
        """
        Factory method for creating a fully initialized StoryState.
        
        Args:
            story_id: UUID of the story
            
        Returns:
            Fully initialized StoryState instance
            
        Raises:
            ValueError: If story data is missing or invalid
        """
        character, chat_history, meta = await cls._load_async_data(story_id)
        return cls(
            story_id,
            character=character,
            chat_history=chat_history,
            meta=meta
        )

    @classmethod
    async def _load_async_data(cls, story_id: str) -> tuple[Character, ChatHistory, MetaData]:
        """Load async data from story files. Called by factory method.
        
        Args:
            story_id: UUID of the story
            
        Returns:
            Tuple of (character, chat_history, meta)
            
        Raises:
            ValueError: If story data is missing or invalid
        """
        # Initialize DAOs for loading
        character_dao = CharacterDAO(characters_dir=path_manager.get_story_characters_dir(story_id))
        chat_history_dao = HistoryDAO(history_file=path_manager.get_story_history_file(story_id))
        meta_dao = MetaDAO(meta_dir=path_manager.get_story_dir(story_id))
        
        # Load all data concurrently
        meta, chat_history, characters = await asyncio.gather(
            meta_dao.get_meta(),
            chat_history_dao.load_history(),
            character_dao.get_characters()
        )

        # Validate all loaded data at once
        if not characters:
            raise ValueError(f"No characters found in story {story_id}")
        if not meta:
            raise ValueError(f"No meta data found in story {story_id}")
        
        # Load the first character
        character = await character_dao.get_character(characters[0].id)
        if not character:
            raise ValueError(f"Failed to load character {characters[0].id} in story {story_id}")

        return character, chat_history, meta

    def add_user_message(self, message: str, scene_description: dict[str, str]) -> None:
        """Add a user message to the chat history."""
        self.chat_history.add_message(
            author_id=self.USER_ID,
            author_type=AuthorType.USER.value,
            author_name=self.USER_NAME,
            content=message,
            scene_description=scene_description
        )

    def add_character_message(self, message: str, scene_description: dict[str, str]) -> None:
        """Add a character message to the chat history."""
        self.chat_history.add_message(
            author_id=self.character.id,
            author_type=AuthorType.BOT.value,
            author_name=self.character.name,
            content=message,
            scene_description=scene_description
        )

    def get_chat_history(self) -> list[ChatItem]:
        """Get chat history data."""
        return self.chat_history.get_data()

    def get_last_scene_description(self) -> dict[str, str]:
        """Get the last scene description from history or meta initial scene."""
        if description := self.chat_history.get_last_scene_description():
            return description
        return self.meta.to_dict().get("initial_scene_description", {"companion_side": "", "character_side": "", "environmental_context": ""})

    async def save_state(self) -> None:
        """Save the current state to files."""
        await asyncio.gather(
            self.chat_history_dao.save(self.chat_history),
            self.character_dao.store_character(self.character.id, self.character),
        )

    def add_story_context_character_data(self, data: dict[str, Any]) -> None:
        """Add story context data to character."""
        self.character.add_story_context_data(data)
