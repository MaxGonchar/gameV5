import pytest
import asyncio
import yaml
import tempfile
import aiofiles
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path

from app.dao.character_dao import CharacterDAO
from app.dao.yaml_file_handler import YamlFileHandler
from app.objects.character import Character


class TestCharacterDAO:
    """Test suite for CharacterDAO class."""

    @pytest.fixture
    def temp_characters_dir(self):
        """Create a temporary directory for test character files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def mock_yaml_handler(self):
        """Mock YamlFileHandler for testing."""
        return Mock(spec=YamlFileHandler)

    @pytest.fixture
    def sample_character_data(self):
        """Sample character data for testing."""
        return {
            "name": "TestCharacter",
            "variables": {"name": "TestCharacter", "mood": "happy"},
            "assistant": [
                {"title": "main goal", "type": "system", "value": "Be helpful"},
                {"title": "personality", "type": "system", "value": "friendly"}
            ],
            "character": [
                {"title": "name", "value": "TestCharacter"},
                {"title": "personality", "value": "cheerful"},
                {"title": "appearance", "value": "tall and friendly"}
            ],
            "parameters": {"happiness": 0.8, "energy": 0.6},
            "dynamic_configs": [
                {
                    "parameter": "happiness",
                    "default": 0.5,
                    "decay_level": 0.9,
                    "dynamic_directives": {
                        "positive": {"axis": [0.1, 0.2, 0.3]},
                        "negative": {"axis": [-0.1, -0.2, -0.3]}
                    }
                }
            ]
        }

    @pytest.fixture
    def templated_character_yaml(self):
        """Sample YAML string with Jinja2 template variables."""
        return """
name: {{ name }}
variables:
  name: "{{ name }}"
  mood: "{{ mood }}"
assistant:
  - title: main goal
    type: system
    value: "Be a helpful {{ name }}"
character:
  - title: name
    value: "{{ name }}"
  - title: mood
    value: "{{ mood }}"
"""

    @pytest.fixture
    def character_dao(self, mock_yaml_handler):
        """Create CharacterDAO instance with mocked dependencies."""
        return CharacterDAO(
            characters_dir="test_characters",
            yaml_handler=mock_yaml_handler
        )

    @pytest.fixture
    def character_dao_with_real_dir(self, temp_characters_dir):
        """Create CharacterDAO instance with real temporary directory."""
        return CharacterDAO(characters_dir=str(temp_characters_dir))

    @pytest.mark.unit
    def test_init_default_parameters(self):
        """Test CharacterDAO initialization with default parameters."""
        dao = CharacterDAO()
        
        assert dao.characters_dir == Path("data/characters")
        assert isinstance(dao.yaml_handler, YamlFileHandler)

    @pytest.mark.unit
    def test_init_custom_parameters(self, mock_yaml_handler):
        """Test CharacterDAO initialization with custom parameters."""
        custom_dir = "custom/characters"
        dao = CharacterDAO(
            characters_dir=custom_dir,
            yaml_handler=mock_yaml_handler
        )
        
        assert dao.characters_dir == Path(custom_dir)
        assert dao.yaml_handler is mock_yaml_handler

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_character_success(self, character_dao, sample_character_data):
        """Test successful character retrieval."""
        character_name = "testchar"
        expected_file_path = Path("test_characters") / f"{character_name}.yaml"
        
        # Mock the _read_and_render_yaml method
        with patch.object(character_dao, '_read_and_render_yaml', new_callable=AsyncMock) as mock_read:
            mock_read.return_value = sample_character_data
            
            result = await character_dao.get_character(character_name)
            
            assert isinstance(result, Character)
            assert result.name == sample_character_data["name"]
            mock_read.assert_called_once_with(expected_file_path)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_character_file_not_found(self, character_dao):
        """Test character retrieval when file doesn't exist."""
        character_name = "nonexistent"
        
        # Mock the _read_and_render_yaml method to raise FileNotFoundError
        with patch.object(character_dao, '_read_and_render_yaml', new_callable=AsyncMock) as mock_read:
            mock_read.side_effect = FileNotFoundError("File not found")
            
            with pytest.raises(FileNotFoundError):
                await character_dao.get_character(character_name)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_read_and_render_yaml_success(self, character_dao, sample_character_data, templated_character_yaml):
        """Test successful YAML reading and rendering."""
        test_file_path = Path("test_file.yaml")
        
        # Mock yaml_handler methods
        character_dao.yaml_handler.read_raw_string = AsyncMock(return_value=templated_character_yaml)
        character_dao.yaml_handler.read_yaml_file = AsyncMock(return_value={
            "variables": {"name": "TestCharacter", "mood": "happy"}
        })
        
        result = await character_dao._read_and_render_yaml(test_file_path)
        
        assert isinstance(result, dict)
        assert result["name"] == "TestCharacter"
        assert result["variables"]["name"] == "TestCharacter"
        assert result["variables"]["mood"] == "happy"
        
        character_dao.yaml_handler.read_raw_string.assert_called_once_with(test_file_path)
        character_dao.yaml_handler.read_yaml_file.assert_called_once_with(test_file_path)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_read_and_render_yaml_no_variables(self, character_dao):
        """Test YAML reading when no variables section exists."""
        test_file_path = Path("test_file.yaml")
        simple_yaml = "name: SimpleCharacter\ntype: basic"
        
        character_dao.yaml_handler.read_raw_string = AsyncMock(return_value=simple_yaml)
        character_dao.yaml_handler.read_yaml_file = AsyncMock(return_value={
            "name": "SimpleCharacter", "type": "basic"
        })
        
        result = await character_dao._read_and_render_yaml(test_file_path)
        
        assert result["name"] == "SimpleCharacter"
        assert result["type"] == "basic"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_read_and_render_yaml_invalid_yaml_dict(self, character_dao):
        """Test YAML reading when yaml_dict is not a dictionary."""
        test_file_path = Path("test_file.yaml")
        simple_yaml = "- item1\n- item2"
        
        character_dao.yaml_handler.read_raw_string = AsyncMock(return_value=simple_yaml)
        character_dao.yaml_handler.read_yaml_file = AsyncMock(return_value=["item1", "item2"])
        
        result = await character_dao._read_and_render_yaml(test_file_path)
        
        assert result == ["item1", "item2"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_read_and_render_yaml_yaml_error(self, character_dao):
        """Test YAML reading when YAML parsing fails."""
        test_file_path = Path("test_file.yaml")
        invalid_yaml = "invalid: yaml: content: ["
        
        character_dao.yaml_handler.read_raw_string = AsyncMock(return_value=invalid_yaml)
        character_dao.yaml_handler.read_yaml_file = AsyncMock(return_value={})
        
        with pytest.raises(yaml.YAMLError, match="Error parsing rendered YAML"):
            await character_dao._read_and_render_yaml(test_file_path)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_store_character_success(self, character_dao_with_real_dir, sample_character_data, temp_characters_dir):
        """Test successful character storage."""
        character = Character(sample_character_data)
        expected_file_path = temp_characters_dir / f"{character.name.lower()}.yaml"
        
        await character_dao_with_real_dir.store_character(character)
        
        # Verify file was created
        assert expected_file_path.exists()
        
        # Verify file contents
        async with aiofiles.open(expected_file_path, "r", encoding="utf-8") as file:
            content = await file.read()
            loaded_data = yaml.safe_load(content)
            
        assert loaded_data["name"] == character.name
        assert loaded_data["assistant"] == character.assistant
        assert loaded_data["character"] == character.character

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_store_character_with_mock(self, character_dao, sample_character_data):
        """Test character storage with mocked file operations."""
        character = Character(sample_character_data)
        
        # Mock aiofiles.open
        mock_file = AsyncMock()
        mock_file.__aenter__ = AsyncMock(return_value=mock_file)
        mock_file.__aexit__ = AsyncMock(return_value=None)
        mock_file.write = AsyncMock()
        
        with patch('aiofiles.open', return_value=mock_file):
            await character_dao.store_character(character)
            
        # Verify yaml.dump was called with correct data
        expected_yaml = yaml.dump(character.to_dict(), default_flow_style=False)
        mock_file.write.assert_called_once_with(expected_yaml)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_store_character_creates_directory(self, temp_characters_dir):
        """Test that store_character creates directory if it doesn't exist."""
        # Create a subdirectory that doesn't exist yet
        new_characters_dir = temp_characters_dir / "new_subdir"
        
        dao = CharacterDAO(characters_dir=str(new_characters_dir))
        character_data = {
            "name": "TestChar",
            "variables": {"name": "TestChar"},
            "assistant": [{"title": "goal", "type": "system", "value": "help"}],
            "character": [{"title": "name", "value": "TestChar"}]
        }
        character = Character(character_data)
        
        # This should create the directory if it doesn't exist
        await dao.store_character(character)
        
        expected_file = new_characters_dir / "testchar.yaml"
        assert expected_file.exists()

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_and_store_character_roundtrip(self, temp_characters_dir, sample_character_data):
        """Integration test: store a character and then retrieve it."""
        dao = CharacterDAO(characters_dir=str(temp_characters_dir))
        
        # Create and store character
        original_character = Character(sample_character_data)
        await dao.store_character(original_character)
        
        # Retrieve character
        retrieved_character = await dao.get_character(original_character.name.lower())
        
        # Verify they match
        assert retrieved_character.name == original_character.name
        assert retrieved_character.assistant == original_character.assistant
        assert retrieved_character.character == original_character.character
        assert retrieved_character.variables == original_character.variables

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_character_case_sensitivity(self, character_dao, sample_character_data):
        """Test that character names are handled consistently."""
        character_name_mixed_case = "TestCharacter"
        expected_file_path = Path("test_characters") / f"{character_name_mixed_case}.yaml"
        
        with patch.object(character_dao, '_read_and_render_yaml', new_callable=AsyncMock) as mock_read:
            mock_read.return_value = sample_character_data
            
            await character_dao.get_character(character_name_mixed_case)
            
            mock_read.assert_called_once_with(expected_file_path)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_store_character_lowercase_filename(self, character_dao, sample_character_data):
        """Test that stored character files use lowercase names."""
        # Modify character data to have mixed case name
        sample_character_data["name"] = "MixedCaseCharacter"
        character = Character(sample_character_data)
        
        mock_file = AsyncMock()
        mock_file.__aenter__ = AsyncMock(return_value=mock_file)
        mock_file.__aexit__ = AsyncMock(return_value=None)
        mock_file.write = AsyncMock()
        
        with patch('aiofiles.open', return_value=mock_file) as mock_open:
            await character_dao.store_character(character)
            
            # Verify the file path uses lowercase
            expected_path = Path("test_characters") / "mixedcasecharacter.yaml"
            mock_open.assert_called_once_with(expected_path, "w", encoding="utf-8")

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_concurrent_character_operations(self, temp_characters_dir):
        """Test that concurrent character operations work correctly."""
        dao = CharacterDAO(characters_dir=str(temp_characters_dir))
        
        # Create multiple characters
        characters_data = []
        for i in range(3):
            char_data = {
                "name": f"Character{i}",
                "variables": {"name": f"Character{i}"},
                "assistant": [{"title": "goal", "type": "system", "value": f"help{i}"}],
                "character": [{"title": "name", "value": f"Character{i}"}]
            }
            characters_data.append(Character(char_data))
        
        # Store all characters concurrently
        store_tasks = [dao.store_character(char) for char in characters_data]
        await asyncio.gather(*store_tasks)
        
        # Retrieve all characters concurrently
        retrieve_tasks = [dao.get_character(f"character{i}") for i in range(3)]
        retrieved_characters = await asyncio.gather(*retrieve_tasks)
        
        # Verify all characters were stored and retrieved correctly
        for i, retrieved_char in enumerate(retrieved_characters):
            assert retrieved_char.name == f"Character{i}"
            assert retrieved_char.variables["name"] == f"Character{i}"