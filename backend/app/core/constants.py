"""
Application-wide constants for file names, extensions, and other static values.
Single source of truth for all hard-coded string constants.
"""

# File Extensions
YAML_EXTENSION = ".yaml"
JSON_EXTENSION = ".json"
TXT_EXTENSION = ".txt"

# File Names
CHARACTER_FILE_NAME = "character.yaml"
META_FILE_NAME = "meta.yaml"
HISTORY_FILE_NAME = "history.yaml"
CHAT_HISTORY_FILE_NAME = "chat_history.yaml"

# Directory Names
CHARACTERS_DIR_NAME = "characters"
LOCATIONS_DIR_NAME = "locations"
STORIES_DIR_NAME = "stories"
CHAT_HISTORY_DIR_NAME = "chat_history"

# Response Limits
ERROR_RESPONSE_LIMIT = 500
DEFAULT_MAX_TOKENS = None

# Server Defaults (for future use)
DEFAULT_SERVER_HOST = "0.0.0.0"
DEFAULT_SERVER_PORT = 8000
DEFAULT_RELOAD_MODE = True