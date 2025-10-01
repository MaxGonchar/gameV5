import yaml
import aiofiles
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path
from jinja2 import Template

from .yaml_file_handler import YamlFileHandler
from app.objects import Character


class CharacterDAO:
    """
    Data Access Object for character configurations.

    Handles:
    - Loading YAML files from filesystem
    - Jinja2 template rendering for variable substitution
    - Character data management

    This abstraction allows for easy replacement with database or other storage
    systems in the future while maintaining the same interface.
    """

    def __init__(
        self,
        characters_dir: str = "data/characters",
        yaml_handler: Optional[YamlFileHandler] = None,
    ):
        """
        Initialize the character DAO.

        Args:
            characters_dir: Directory containing character YAML files
            yaml_handler: YAML file handler dependency
        """
        self.characters_dir = Path(characters_dir)
        self.yaml_handler = yaml_handler or YamlFileHandler()

    async def get_character(self, character_name: str) -> Character:
        """
        Load and render character configuration from YAML file.

        Args:
            character_name: Name of the character

        Returns:
            Character object containing configuration with variables substituted

        Raises:
            FileNotFoundError: If character file doesn't exist
            yaml.YAMLError: If YAML parsing fails
        """
        character_file = self.characters_dir / character_name / "character.yaml"
        return Character(await self._read_and_render_yaml(character_file))

    async def _read_and_render_yaml(self, file_path: Path) -> Dict[str, Any]:
        """
        Read a YAML file, render it using Jinja2 with variables from the file
        itself, and return its contents as a dict.

        Args:
            file_path: Path to the YAML file

        Returns:
            Contents of the YAML file as a dict with variables rendered

        Raises:
            FileNotFoundError: If file doesn't exist
            yaml.YAMLError: If YAML parsing fails
            Exception: For other unexpected errors
        """
        try:
            yaml_string, yaml_dict = await asyncio.gather(
                self.yaml_handler.read_raw_string(file_path),
                self.yaml_handler.read_yaml_file(file_path),
            )

            variables = (
                yaml_dict.get("variables", {}) if isinstance(yaml_dict, dict) else {}
            )

            template = Template(yaml_string)
            rendered_yaml_string = template.render(**variables)

            data = yaml.safe_load(rendered_yaml_string)

            return data

        except yaml.YAMLError as exc:
            raise yaml.YAMLError(f"Error parsing rendered YAML: {exc}")

    async def store_character(self, character: Character) -> None:
        """
        Store character configuration to a YAML file.

        Args:
            character: Character object containing configuration to store

        Raises:
            Exception: If an error occurs while writing the file
        """
        character_dir = self.characters_dir / character.name.lower()
        character_file = character_dir / "character.yaml"

        # Ensure the directory exists
        character_dir.mkdir(parents=True, exist_ok=True)

        yaml_string = yaml.dump(character.to_dict(), default_flow_style=False)

        async with aiofiles.open(character_file, "w", encoding="utf-8") as file:
            await file.write(yaml_string)

