from typing import Optional
import asyncio
from pathlib import Path

from .yaml_file_handler import YamlFileHandler
from app.objects import Character


class CharacterDAO:
    """
    Data Access Object for character configurations.
    
    Handles loading and storing characters from/to YAML files using UUID-based directories.
    """
    
    def __init__(
        self, 
        characters_dir: str = "data/characters",
        yaml_handler: Optional[YamlFileHandler] = None
    ) -> None:
        """
        Initialize the character DAO.
        
        Args:
            characters_dir: Directory containing character YAML files
            yaml_handler: YAML file handler dependency
        """
        self.characters_dir = Path(characters_dir)
        self.yaml_handler = yaml_handler or YamlFileHandler()

    async def get_characters(self) -> list[Character]:
        """
        Load all characters from the characters directory.
        
        Returns:
            List of Character objects
            
        Raises:
            FileNotFoundError: If characters directory doesn't exist
            yaml.YAMLError: If YAML parsing fails for any character
        """
        if not self.characters_dir.exists():
            return []
        
        # Collect all character file paths
        character_files = []
        for character_dir in self.characters_dir.iterdir():
            if character_dir.is_dir():
                character_file = character_dir / "character.yaml"
                if character_file.exists():
                    character_files.append(character_file)
        
        if not character_files:
            return []
        
        # Load all character files concurrently
        async def load_character(character_file: Path) -> Character | None:
            """Load a single character file, returning None if it fails."""
            try:
                character_data = await self.yaml_handler.read_yaml_file(character_file)
                if isinstance(character_data, dict):
                    return Character(character_data)
                else:
                    print(f"Warning: Invalid character data format in {character_file}, expected dict but got {type(character_data)}")
                    return None
            except Exception as e:
                # Log the error but continue with other characters
                print(f"Warning: Failed to load character from {character_file}: {e}")
                return None
        
        # Load all characters concurrently
        character_results = await asyncio.gather(
            *[load_character(file) for file in character_files],
            return_exceptions=False
        )
        
        # Filter out None results (failed loads)
        characters = [char for char in character_results if char is not None]
        
        return characters

    async def get_character(self, id: str) -> Character:
        """
        Load a specific character by ID.
        
        Args:
            id: UUID of the character
            
        Returns:
            Character object
            
        Raises:
            FileNotFoundError: If character file doesn't exist
            yaml.YAMLError: If YAML parsing fails
        """
        character_file = self.characters_dir / id / "character.yaml"
        
        if not character_file.exists():
            raise FileNotFoundError(f"Character with id {id} not found at {character_file}")
        
        character_data = await self.yaml_handler.read_yaml_file(character_file)
        
        if not isinstance(character_data, dict):
            raise ValueError(f"Invalid character data format in {character_file}, expected dict but got {type(character_data)}")
        
        return Character(character_data)

    async def store_character(self, id: str, character: Character) -> None:
        """
        Store a character to a YAML file.
        
        Args:
            id: UUID for the character directory
            character: Character object to store
            
        Raises:
            yaml.YAMLError: If YAML serialization fails
            OSError: If file writing fails
        """
        character_dir = self.characters_dir / id
        character_file = character_dir / "character.yaml"
        
        # Ensure the directory exists
        character_dir.mkdir(parents=True, exist_ok=True)
        
        # Store the character using the yaml handler
        await self.yaml_handler.write_yaml_file(character_file, character.to_dict())


