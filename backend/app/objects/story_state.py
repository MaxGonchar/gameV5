import asyncio
from typing import Any
from enum import Enum

from app.objects.character import Character
from app.objects.location import Location
from app.objects.chat_history import ChatHistory
from app.objects.meta import MetaData
from app.dao.character_dao import CharacterDAO
from app.dao.location_dao import LocationDAO
from app.dao.history_dao import HistoryDAO
from app.dao.meta_dao import MetaDAO
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
    """
    
    # TODO: Using async __new__ is an anti-pattern and can cause issues with object initialization.
    # Consider using a factory method or async context manager instead.
    async def __new__(cls, *a, **kw):
        instance = super().__new__(cls)
        await instance.__init__(*a, **kw)
        return instance

    async def __init__(self, story_id: str, character_id: str | None = None, user_id: str = "user", user_name: str = "User"):
        """
        Initialize the story state.
        
        Args:
            story_id: UUID of the story
            character_id: UUID of the character (will be determined from story data if None)
            user_id: ID of the user (default: "user")
            user_name: Name of the user (default: "User")
        """
        self.story_id = story_id
        self.character_id = character_id
        self.user_id = user_id
        self.user_name = user_name

        # Initialize DAOs with story-specific paths
        self.character_dao = CharacterDAO(characters_dir=f"data/stories/{story_id}/characters")
        self.location_dao = LocationDAO(locations_dir=f"data/stories/{story_id}/locations")
        self.chat_history_dao = HistoryDAO(history_file=f"data/stories/{story_id}/history.yaml")
        self.meta_dao = MetaDAO(meta_dir=f"data/stories/{story_id}")

        self.character: Character
        self.location: Location
        self.chat_history: ChatHistory
        self.meta: MetaData

        await self._get_init_state()

    async def _get_init_state(self):
        """Load initial state from story data files."""
        # Load meta and history first
        meta, chat_history = await asyncio.gather(
            self.meta_dao.get_meta(),
            self.chat_history_dao.load_history()
        )

        # Determine character_id if not provided
        if not self.character_id:
            # Get the first available character from the story
            characters = await self.character_dao.get_characters()
            if not characters:
                raise ValueError(f"No characters found in story {self.story_id}")
            self.character_id = characters[0].id

        # Determine location_id from the first available location
        locations = await self.location_dao.get_locations()
        if not locations:
            raise ValueError(f"No locations found in story {self.story_id}")
        location_id = locations[0].id

        # Load character and location
        character, location = await asyncio.gather(
            self.character_dao.get_character(self.character_id),
            self.location_dao.get_location(location_id)
        )

        if not character or not location or not meta:
            raise ValueError(f"Failed to initialize story state for story {self.story_id}: missing data")

        self.character = character
        self.chat_history = chat_history
        self.location = location
        self.meta = meta

    def add_user_message(self, message: str, scene_description: str) -> None:
        """Add a user message to the chat history."""
        self.chat_history.add_message(
            author_id=self.user_id,
            author_type=AuthorType.USER.value,
            author_name=self.user_name,
            content=message,
            scene_description=scene_description
        )

    def add_character_message(self, message: str, scene_description: str) -> None:
        """Add a character message to the chat history."""
        self.chat_history.add_message(
            author_id=self.character.id,
            author_type=AuthorType.BOT.value,
            author_name=self.character.name,
            content=message,
            scene_description=scene_description
        )
    
    def update_character_configs(self, user_message_embeddings: list[float]) -> None:
        """Update character configurations based on user message embeddings."""
        self.character.update_dynamic_configs_according_to_message_embeddings(user_message_embeddings)

    def get_character_prompt_configs(self) -> list[dict[str, Any]]:
        """Get character prompt configurations."""
        return self.character.to_prompt_dict()["character"]
    
    def get_character_assistant_configs(self) -> list[dict[str, Any]]:
        """Get character assistant configurations."""
        return self.character.to_prompt_dict()["assistant"]

    def get_location_description(self) -> dict[str, Any]:
        """Get location description."""
        return self.location.description
    
    def get_chat_history(self) -> list[ChatItem]:
        """Get chat history data."""
        return self.chat_history.get_data()

    def get_last_scene_description(self) -> str:
        """Get the last scene description from history or meta initial scene."""
        if description := self.chat_history.get_last_scene_description():
            return description
        return self.meta.initial_scene_description

    async def save_state(self) -> None:
        """Save the current state to files."""
        await asyncio.gather(
            self.chat_history_dao.save(self.chat_history),
            self.character_dao.store_character(self.character.id, self.character),
        )


# Backward compatibility alias
GlobalState = StoryState