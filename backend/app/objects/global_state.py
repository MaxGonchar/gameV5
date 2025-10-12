import asyncio
from typing import Any
from enum import Enum

from app.objects.character import Character
from app.objects.location import Location
from app.objects.chat_history import ChatHistory
from app.objects.meta import MetaData
from app.dao.character_dao import CharacterDAO
from app.dao.location_dao import LocationDAO
from app.dao.chat_history_dao import ChatHistoryDAO
from app.dao.meta_dao import MetaDAO
from app.chat_types import ChatItem

# temporary constants:
CHARACTER_NAME = "Nira"
CHARACTER_ID = "nira"
USER_NAME = "Max"
USER_ID = "max"


class AuthorType(Enum):
    USER = "user"
    BOT = "bot"


class GlobalState:
    # TODO: Using async __new__ is an anti-pattern and can cause issues with object initialization.
    # Consider using a factory method or async context manager instead.
    async def __new__(cls, *a, **kw):
        instance = super().__new__(cls)
        await instance.__init__(*a, **kw)
        return instance

    async def __init__(self, character_name: str = "nira"):
        self.character_name = character_name

        self.character_dao = CharacterDAO()
        self.location_dao = LocationDAO()
        self.chat_history_dao = ChatHistoryDAO()
        self.meta_dao = MetaDAO()

        self.character: Character
        self.location: Location
        self.chat_history: ChatHistory
        self.meta: MetaData

        await self._get_init_state()

    async def _get_init_state(self):
        character, chat_history, location, meta = await asyncio.gather(
            self.character_dao.get_character(self.character_name),
            self.chat_history_dao.load_chat_history(),
            self.location_dao.get_location(),
            self.meta_dao.get_meta()
        )

        if not character or not chat_history or not location or not meta:
            raise ValueError("Failed to initialize global state: missing data")

        self.character = character
        self.chat_history = chat_history
        self.location = location
        self.meta = meta

    def add_user_message(self, message: str, scene_description: str) -> None:
        self.chat_history.add_message(
            author_id=USER_ID,
            author_type=AuthorType.USER.value,
            author_name=USER_NAME,
            content=message,
            scene_description=scene_description
        )

    def add_character_message(self, message: str, scene_description: str) -> None:
        self.chat_history.add_message(
            author_id=CHARACTER_ID,
            author_type=AuthorType.BOT.value,
            author_name=CHARACTER_NAME,
            content=message,
            scene_description=scene_description
        )
    
    def update_character_configs(self, user_message_embeddings: list[float]) -> None:
        self.character.update_dynamic_configs_according_to_message_embeddings(user_message_embeddings)

    def get_character_prompt_configs(self) -> list[dict[str, Any]]:
        return self.character.to_prompt_dict()["character"]
    
    def get_character_assistant_configs(self) -> list[dict[str, Any]]:
        return self.character.to_prompt_dict()["assistant"]

    def get_location_description(self) -> dict[str, Any]:
        return self.location.description
    
    def get_chat_history(self) -> list[ChatItem]:
        return self.chat_history.get_data()

    def get_last_scene_description(self) -> str:
        if description := self.chat_history.get_last_scene_description():
            return description
        return self.meta.initial_scene_description

    async def save_state(self) -> None:
        await asyncio.gather(
            self.chat_history_dao.save(self.chat_history),
            self.character_dao.store_character(self.character),
        )
