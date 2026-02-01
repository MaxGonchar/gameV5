# # Standard library imports
import asyncio
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

# # Third-party imports
import pytest

# # Local application imports
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
            "variables": {"name": "TestCharacter", "id": "test-uuid-123"},
            "assistant": [
                {"title": "main goal", "value": "Be helpful"},
                {"title": "personality", "value": "friendly"},
            ],
            "character": [
                {"title": "name", "value": "TestCharacter"},
                {"title": "personality", "value": "cheerful"},
                {"title": "appearance", "value": "tall and friendly"},
            ],
        }

    @pytest.fixture
    def sample_character_id(self):
        """Sample character UUID for testing."""
        return "550e8400-e29b-41d4-a716-446655440000"

    @pytest.fixture
    def character_dao(self, mock_yaml_handler):
        """Create CharacterDAO instance with mocked dependencies."""
        return CharacterDAO(
            characters_dir="test_characters", yaml_handler=mock_yaml_handler
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
        dao = CharacterDAO(characters_dir=custom_dir, yaml_handler=mock_yaml_handler)

        assert dao.characters_dir == Path(custom_dir)
        assert dao.yaml_handler is mock_yaml_handler

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_character_success(
        self, character_dao, sample_character_data, sample_character_id
    ):
        """Test successful character retrieval by ID."""
        expected_file_path = (
            Path("test_characters") / sample_character_id / "character.yaml"
        )

        # Mock the yaml handler and file existence
        character_dao.yaml_handler.read_yaml_file = AsyncMock(
            return_value=sample_character_data
        )

        with patch.object(Path, "exists", return_value=True):
            result = await character_dao.get_character(sample_character_id)

            assert isinstance(result, Character)
            assert result.name == sample_character_data["name"]
            character_dao.yaml_handler.read_yaml_file.assert_called_once_with(
                expected_file_path
            )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_character_file_not_found(
        self, character_dao, sample_character_id
    ):
        """Test character retrieval when file doesn't exist."""
        # Mock file existence check and yaml handler
        with patch.object(Path, "exists", return_value=False):
            with pytest.raises(
                FileNotFoundError,
                match=f"Character with id {sample_character_id} not found",
            ):
                await character_dao.get_character(sample_character_id)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_character_invalid_yaml_format(
        self, character_dao, sample_character_id
    ):
        """Test character retrieval when YAML is not a dict."""
        # Mock yaml handler to return a list instead of dict
        character_dao.yaml_handler.read_yaml_file = AsyncMock(
            return_value=["not", "a", "dict"]
        )

        with patch.object(Path, "exists", return_value=True):
            with pytest.raises(ValueError, match="Invalid character data format"):
                await character_dao.get_character(sample_character_id)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_characters_empty_directory(self, character_dao):
        """Test get_characters when characters directory doesn't exist."""
        with patch.object(Path, "exists", return_value=False):
            result = await character_dao.get_characters()
            assert result == []

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_characters_success(self, character_dao, sample_character_data):
        """Test successful retrieval of multiple characters."""
        # Mock directory structure
        char_id_1 = "550e8400-e29b-41d4-a716-446655440000"
        char_id_2 = "550e8400-e29b-41d4-a716-446655440001"

        mock_dir_1 = Mock()
        mock_dir_1.is_dir.return_value = True
        mock_dir_1.name = char_id_1
        mock_dir_1.__truediv__ = lambda self, other: Path(
            f"test_characters/{char_id_1}/{other}"
        )

        mock_dir_2 = Mock()
        mock_dir_2.is_dir.return_value = True
        mock_dir_2.name = char_id_2
        mock_dir_2.__truediv__ = lambda self, other: Path(
            f"test_characters/{char_id_2}/{other}"
        )

        # Mock character data for second character
        sample_character_data_2 = sample_character_data.copy()
        sample_character_data_2["variables"] = sample_character_data["variables"].copy()
        sample_character_data_2["variables"]["name"] = "TestCharacter2"

        with patch.object(Path, "exists", return_value=True):
            with patch.object(Path, "iterdir", return_value=[mock_dir_1, mock_dir_2]):
                with patch.object(
                    Path, "exists", return_value=True
                ):  # For character.yaml files
                    character_dao.yaml_handler.read_yaml_file = AsyncMock()
                    character_dao.yaml_handler.read_yaml_file.side_effect = [
                        sample_character_data,
                        sample_character_data_2,
                    ]

                    result = await character_dao.get_characters()

                    assert len(result) == 2
                    assert all(isinstance(char, Character) for char in result)

                    # Check that both characters are present (order not guaranteed with concurrent loading)
                    character_names = {char.name for char in result}
                    assert character_names == {"TestCharacter", "TestCharacter2"}

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_characters_skips_invalid_characters(
        self, character_dao, sample_character_data
    ):
        """Test get_characters skips characters that fail to load."""
        char_id_1 = "550e8400-e29b-41d4-a716-446655440000"
        char_id_2 = "550e8400-e29b-41d4-a716-446655440001"

        mock_dir_1 = Mock()
        mock_dir_1.is_dir.return_value = True
        mock_dir_1.__truediv__ = lambda self, other: Path(
            f"test_characters/{char_id_1}/{other}"
        )

        mock_dir_2 = Mock()
        mock_dir_2.is_dir.return_value = True
        mock_dir_2.__truediv__ = lambda self, other: Path(
            f"test_characters/{char_id_2}/{other}"
        )

        with patch.object(Path, "exists", return_value=True):
            with patch.object(Path, "iterdir", return_value=[mock_dir_1, mock_dir_2]):
                with patch.object(Path, "exists", return_value=True):
                    # First character loads successfully, second fails
                    character_dao.yaml_handler.read_yaml_file = AsyncMock()
                    character_dao.yaml_handler.read_yaml_file.side_effect = [
                        sample_character_data,
                        Exception("Failed to load"),
                    ]

                    with patch("builtins.print") as mock_print:
                        result = await character_dao.get_characters()

                        assert len(result) == 1
                        assert result[0].name == "TestCharacter"
                        mock_print.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_store_character_success(
        self,
        character_dao_with_real_dir,
        sample_character_data,
        temp_characters_dir,
        sample_character_id,
    ):
        """Test successful character storage."""
        character = Character(sample_character_data)
        expected_character_dir = temp_characters_dir / sample_character_id
        expected_file_path = expected_character_dir / "character.yaml"

        await character_dao_with_real_dir.store_character(
            sample_character_id, character
        )

        # Verify directory was created
        assert expected_character_dir.exists()
        assert expected_character_dir.is_dir()

        # Verify file was created
        assert expected_file_path.exists()

        # Verify file contents by reading it back
        loaded_character = await character_dao_with_real_dir.get_character(
            sample_character_id
        )
        assert loaded_character.name == character.name
        assert loaded_character.assistant == character.assistant
        assert loaded_character.character == character.character

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_store_character_with_mock(
        self, character_dao, sample_character_data, sample_character_id
    ):
        """Test character storage with mocked file operations."""
        character = Character(sample_character_data)
        expected_file_path = (
            Path("test_characters") / sample_character_id / "character.yaml"
        )

        character_dao.yaml_handler.write_yaml_file = AsyncMock()

        with patch.object(Path, "mkdir") as mock_mkdir:
            await character_dao.store_character(sample_character_id, character)

            # Verify directory creation was called
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

            # Verify yaml handler was called with correct data
            character_dao.yaml_handler.write_yaml_file.assert_called_once_with(
                expected_file_path, character.to_dict()
            )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_store_character_creates_directory(
        self, temp_characters_dir, sample_character_data, sample_character_id
    ):
        """Test that store_character creates directory if it doesn't exist."""
        # Create a subdirectory that doesn't exist yet
        new_characters_dir = temp_characters_dir / "new_subdir"

        dao = CharacterDAO(characters_dir=str(new_characters_dir))
        character = Character(sample_character_data)

        # This should create the directory if it doesn't exist
        await dao.store_character(sample_character_id, character)

        expected_character_dir = new_characters_dir / sample_character_id
        expected_file = expected_character_dir / "character.yaml"
        assert expected_character_dir.exists()
        assert expected_character_dir.is_dir()
        assert expected_file.exists()

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_and_store_character_roundtrip(
        self, temp_characters_dir, sample_character_data, sample_character_id
    ):
        """Integration test: store a character and then retrieve it."""
        dao = CharacterDAO(characters_dir=str(temp_characters_dir))

        # Create and store character
        original_character = Character(sample_character_data)
        await dao.store_character(sample_character_id, original_character)

        # Retrieve character
        retrieved_character = await dao.get_character(sample_character_id)

        # Verify they match
        assert retrieved_character.name == original_character.name
        assert retrieved_character.assistant == original_character.assistant
        assert retrieved_character.character == original_character.character
        assert retrieved_character.variables == original_character.variables

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_characters_integration(
        self, temp_characters_dir, sample_character_data
    ):
        """Integration test: store multiple characters and retrieve all."""
        dao = CharacterDAO(characters_dir=str(temp_characters_dir))

        # Create and store multiple characters
        char_ids = [
            "550e8400-e29b-41d4-a716-446655440000",
            "550e8400-e29b-41d4-a716-446655440001",
            "550e8400-e29b-41d4-a716-446655440002",
        ]

        stored_characters = []
        for i, char_id in enumerate(char_ids):
            char_data = sample_character_data.copy()
            char_data["name"] = f"TestCharacter{i}"
            char_data["variables"]["name"] = f"TestCharacter{i}"
            char_data["variables"]["id"] = char_id

            character = Character(char_data)
            await dao.store_character(char_id, character)
            stored_characters.append(character)

        # Retrieve all characters
        all_characters = await dao.get_characters()

        # Verify all characters were retrieved
        assert len(all_characters) == 3
        retrieved_names = {char.name for char in all_characters}
        expected_names = {f"TestCharacter{i}" for i in range(3)}
        assert retrieved_names == expected_names

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_concurrent_character_operations(
        self, temp_characters_dir, sample_character_data
    ):
        """Test that concurrent character operations work correctly."""
        dao = CharacterDAO(characters_dir=str(temp_characters_dir))

        # Create multiple characters with different IDs
        char_data_list = []
        char_ids = []
        for i in range(3):
            char_id = f"550e8400-e29b-41d4-a716-44665544000{i}"
            # Deep copy to avoid shared references
            char_data = {
                "name": f"Character{i}",
                "variables": {"name": f"Character{i}", "id": char_id},
                "assistant": sample_character_data["assistant"].copy(),
                "character": sample_character_data["character"].copy(),
            }

            char_data_list.append((char_id, Character(char_data)))
            char_ids.append(char_id)

        # Store all characters concurrently
        store_tasks = [
            dao.store_character(char_id, char) for char_id, char in char_data_list
        ]
        await asyncio.gather(*store_tasks)

        # Retrieve all characters individually to verify correct storage
        for i, char_id in enumerate(char_ids):
            retrieved_char = await dao.get_character(char_id)
            assert retrieved_char.name == f"Character{i}"
            assert retrieved_char.variables["name"] == f"Character{i}"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_character_yaml_error_handling(
        self, character_dao, sample_character_id
    ):
        """Test character retrieval when YAML handler raises an error."""
        # Mock file existence and yaml handler error
        with patch.object(Path, "exists", return_value=True):
            character_dao.yaml_handler.read_yaml_file = AsyncMock(
                side_effect=Exception("YAML error")
            )

            with pytest.raises(Exception, match="YAML error"):
                await character_dao.get_character(sample_character_id)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_store_character_yaml_error_handling(
        self, character_dao, sample_character_data, sample_character_id
    ):
        """Test character storage when YAML handler raises an error."""
        character = Character(sample_character_data)

        # Mock yaml handler error
        character_dao.yaml_handler.write_yaml_file = AsyncMock(
            side_effect=Exception("Write error")
        )

        with patch.object(Path, "mkdir"):
            with pytest.raises(Exception, match="Write error"):
                await character_dao.store_character(sample_character_id, character)
