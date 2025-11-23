from typing import Optional
import asyncio
from pathlib import Path

from app.core.config import settings, get_logger
from .yaml_file_handler import YamlFileHandler
from app.objects import Character
from app.exceptions import EntityNotFoundException, DataValidationException

logger = get_logger(__name__)


# TODO: refactor:
# make methods smaller, focused on single tasks
# consider reusing "FileSystemOperations" where applicable
class CharacterDAO:
    """
    Data Access Object for character configurations.
    
    Handles loading and storing characters from/to YAML files.
    Structure: {characters_dir}/{character_id}/character.yaml
    """
    
    def __init__(
        self,
        characters_dir: str | None = None,
        yaml_handler: Optional[YamlFileHandler] = None
    ) -> None:
        """
        Initialize the character DAO.
        
        Args:
            characters_dir: Directory containing character subdirectories (default: from settings)
            yaml_handler: Optional YAML file handler (for testing)
        """
        self.characters_dir = Path(characters_dir or settings.characters_base_dir)
        self.yaml_handler = yaml_handler or YamlFileHandler()

    async def get_characters(self) -> list[Character]:
        """
        Load all characters from the characters directory.
        
        Returns:
            List of Character objects
            
        Note:
            Failed character loads are logged but don't stop the operation.
            Only successfully loaded characters are returned.
        """
        if not self.characters_dir.exists():
            logger.info(f"Characters directory does not exist: {self.characters_dir}")
            return []
        
        # Collect all character file paths
        character_files = []
        for character_dir in self.characters_dir.iterdir():
            if character_dir.is_dir():
                character_file = character_dir / "character.yaml"
                if character_file.exists():
                    character_files.append(character_file)
                else:
                    logger.warning(f"Character directory '{character_dir.name}' missing character.yaml file")
        
        if not character_files:
            logger.info(f"No character files found in {self.characters_dir}")
            return []
        
        # Load all character files concurrently
        async def load_character(character_file: Path) -> Character:
            """Load a single character file, raising exceptions on failure."""
            character_data = await self.yaml_handler.read_yaml_file(character_file)
            
            if not isinstance(character_data, dict):
                raise DataValidationException(
                    f"Invalid character data format in {character_file}",
                    details={
                        "file_path": str(character_file),
                        "expected_type": "dict",
                        "actual_type": type(character_data).__name__
                    }
                )
            
            return Character(character_data)
        
        # Load all characters concurrently, but collect exceptions
        character_results = await asyncio.gather(
            *[load_character(file) for file in character_files],
            return_exceptions=True
        )
        
        # Separate successful loads from failures
        characters = []
        for i, result in enumerate(character_results):
            if isinstance(result, Exception):
                character_file = character_files[i]
                logger.error(
                    f"Failed to load character from {character_file}: {result}", 
                    exc_info=isinstance(result, Exception)
                )
            else:
                characters.append(result)
        
        logger.info(f"Successfully loaded {len(characters)} out of {len(character_files)} characters")
        return characters

    async def get_character(self, character_id: str) -> Character:
        """
        Load a specific character by ID.
        
        Args:
            character_id: UUID of the character
            
        Returns:
            Character object
            
        Raises:
            EntityNotFoundException: If character file doesn't exist
            DataValidationException: If character data is invalid
            YamlException, FileOperationException: From yaml_handler (bubbled up)
        """
        character_file = self.characters_dir / character_id / "character.yaml"
        
        if not character_file.exists():
            raise EntityNotFoundException(
                f"Character '{character_id}' not found",
                details={
                    "character_id": character_id,
                    "file_path": str(character_file),
                    "characters_dir": str(self.characters_dir)
                }
            )
        
        character_data = await self.yaml_handler.read_yaml_file(character_file)
        
        if not isinstance(character_data, dict):
            raise DataValidationException(
                f"Invalid character data format for '{character_id}'",
                details={
                    "character_id": character_id,
                    "file_path": str(character_file),
                    "expected_type": "dict",
                    "actual_type": type(character_data).__name__
                }
            )
        
        return Character(character_data)

    async def store_character(self, character_id: str, character: Character) -> None:
        """
        Store a character to a YAML file.
        
        Args:
            character_id: UUID for the character directory
            character: Character object to store
            
        Raises:
            YamlException: If YAML serialization fails
            FileOperationException: If file writing fails
        """
        character_dir = self.characters_dir / character_id
        character_file = character_dir / "character.yaml"
        
        # Ensure the directory exists
        character_dir.mkdir(parents=True, exist_ok=True)
        
        # Store the character using the yaml handler
        await self.yaml_handler.write_yaml_file(character_file, character.to_dict())
    
    def get_character_folder(self, character_id: str) -> Path:
        """
        Get the folder path for a specific character by ID.

        Args:
            character_id: UUID of the character

        Returns:
            Path object representing the character's folder
        """
        return self.characters_dir / character_id
