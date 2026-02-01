"""
Path management utilities for data access operations.
Centralized path construction logic for all DAO operations.
"""

# # Relative imports
from ..core.config import settings
from ..core.constants import (
    CHARACTER_FILE_NAME,
    CHARACTERS_DIR_NAME,
    CHAT_HISTORY_DIR_NAME,
    CHAT_HISTORY_FILE_NAME,
    HISTORY_FILE_NAME,
    LOCATIONS_DIR_NAME,
    META_FILE_NAME,
    STORIES_DIR_NAME,
)


# TODO: refactor to use Path
# TODO: check methods, looks like some of them are doing the same and not needed
class PathManager:
    """Centralized path management for all DAO operations."""

    # @staticmethod
    # def get_base_data_dir() -> str:
    #     """Get the base data directory."""
    #     return settings.DATA_BASE_DIR

    @staticmethod
    def get_characters_base_dir() -> str:
        """Get the base directory for character data."""
        return f"{settings.DATA_BASE_DIR}/{CHARACTERS_DIR_NAME}"

    # @staticmethod
    # def get_locations_base_dir() -> str:
    #     """Get the base directory for location data."""
    #     return f"{settings.DATA_BASE_DIR}/{LOCATIONS_DIR_NAME}"

    @staticmethod
    def get_stories_base_dir() -> str:
        """Get the base directory for story data."""
        return f"{settings.DATA_BASE_DIR}/{STORIES_DIR_NAME}"

    @staticmethod
    def get_story_dir(story_id: str) -> str:
        """Get the directory for a specific story."""
        return f"{PathManager.get_stories_base_dir()}/{story_id}"

    @staticmethod
    def get_story_characters_dir(story_id: str) -> str:
        """Get the characters directory for a specific story."""
        return f"{PathManager.get_story_dir(story_id)}/{CHARACTERS_DIR_NAME}"

    @staticmethod
    def get_story_history_file(story_id: str) -> str:
        """Get the history file path for a specific story."""
        return f"{PathManager.get_story_dir(story_id)}/{HISTORY_FILE_NAME}"

    @staticmethod
    def get_story_meta_file(story_id: str) -> str:
        """Get the meta file path for a specific story."""
        return f"{PathManager.get_story_dir(story_id)}/{META_FILE_NAME}"

    @staticmethod
    def get_character_file(character_id: str, characters_dir: str | None = None) -> str:
        """Get the character file path for a specific character."""
        if characters_dir:
            return f"{characters_dir}/{character_id}/{CHARACTER_FILE_NAME}"
        return f"{PathManager.get_characters_base_dir()}/{character_id}/{CHARACTER_FILE_NAME}"

    @staticmethod
    def get_character_dir(character_id: str, characters_dir: str | None = None) -> str:
        """Get the directory for a specific character."""
        if characters_dir:
            return f"{characters_dir}/{character_id}"
        return f"{PathManager.get_characters_base_dir()}/{character_id}"

    # @staticmethod
    # def get_location_dir(location_id: str) -> str:
    #     """Get the directory for a specific location."""
    #     return f"{PathManager.get_locations_base_dir()}/{location_id}"

    # @staticmethod
    # def get_meta_file(file_dir: str) -> str:
    #     """Get the global meta file path."""
    #     return f"{file_dir}/{META_FILE_NAME}"

    # @staticmethod
    # def get_chat_history_file(story_id: str | None = None) -> str:
    #     """Get chat history file path (global or story-specific)."""
    #     if story_id:
    #         return f"{PathManager.get_story_dir(story_id)}/{CHAT_HISTORY_FILE_NAME}"
    #     return f"{settings.DATA_BASE_DIR}/{CHAT_HISTORY_DIR_NAME}/{CHAT_HISTORY_FILE_NAME}"


# Create a singleton instance for easy access
path_manager = PathManager()
