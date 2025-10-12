import pytest
from unittest.mock import patch
from app.builders.character_move_system_prompt_builder import CharacterMoveSystemPromptBuilder


class TestCharacterMoveSystemPromptBuilder:
    """Test suite for CharacterMoveSystemPromptBuilder class."""
    
    @pytest.fixture
    def builder(self):
        """Create a fresh builder instance for each test."""
        return CharacterMoveSystemPromptBuilder()
    
    @pytest.fixture
    def custom_template_builder(self):
        """Create a builder with custom template."""
        custom_template = "Custom system prompt template.\n"
        return CharacterMoveSystemPromptBuilder(template=custom_template)
    
    @pytest.fixture
    def sample_assistant_configs(self):
        """Sample assistant configurations for testing."""
        return [
            {"title": "main goal", "value": "Be a helpful assistant"},
            {"title": "style", "value": "Professional and concise"},
            {"title": "constraints", "value": ["No harmful content", "Stay in character"]}
        ]
    
    @pytest.fixture
    def sample_character_config(self):
        """Sample character configuration for testing."""
        return {
            "title": "character",
            "value": [
                {"title": "name", "value": "Aria"},
                {"title": "personality", "value": "Curious and analytical"},
                {"title": "background", "value": ["Former scientist", "Lives in a magical world"]},
                {"title": "abilities", "value": ["Spell casting", "Potion brewing", "Research"]}
            ]
        }
    
    @pytest.fixture
    def sample_location_config(self):
        """Sample location configuration for testing."""
        return {
            "title": "location",
            "value": [
                {"title": "name", "value": "Ancient Library"},
                {"title": "description", "value": "A vast library filled with mystical tomes"},
                {"title": "atmosphere", "value": "Quiet and mysterious"},
                {"title": "notable_features", "value": ["Floating books", "Glowing crystals", "Ancient artifacts"]}
            ]
        }

    def test_init_default_template(self):
        """Test builder initialization with default template."""
        builder = CharacterMoveSystemPromptBuilder()
        
        expected_template = (
            "Assistant is a character in the role play game.\n"
            "Assistant strictly has to follow the character description and general instructions.\n"
        )
        
        assert builder.template == expected_template
        assert builder.template == CharacterMoveSystemPromptBuilder.TEMPLATE
        assert builder.configs == []

    def test_init_custom_template(self):
        """Test builder initialization with custom template."""
        custom_template = "This is a custom template.\n"
        builder = CharacterMoveSystemPromptBuilder(template=custom_template)
        
        assert builder.template == custom_template
        assert builder.configs == []

    def test_init_none_template_uses_default(self):
        """Test that None template falls back to default."""
        builder = CharacterMoveSystemPromptBuilder(template=None)
        
        assert builder.template == CharacterMoveSystemPromptBuilder.TEMPLATE

    def test_with_assistant_configs_returns_self(self, builder, sample_assistant_configs):
        """Test that with_assistant_configs returns self for method chaining."""
        result = builder.with_assistant_configs(sample_assistant_configs)
        
        assert result is builder

    def test_with_assistant_configs_adds_config(self, builder, sample_assistant_configs):
        """Test that assistant configs are properly added."""
        builder.with_assistant_configs(sample_assistant_configs)
        
        expected_config = {
            "template": "\n<General assistant instructions>\n{}\n</General assistant instructions>\n",
            "configs": sample_assistant_configs,
        }
        
        assert len(builder.configs) == 1
        assert builder.configs[0] == expected_config

    def test_with_character_config_returns_self(self, builder, sample_character_config):
        """Test that with_character_config returns self for method chaining."""
        result = builder.with_character_config(sample_character_config)
        
        assert result is builder

    def test_with_character_config_adds_config(self, builder, sample_character_config):
        """Test that character config is properly added."""
        builder.with_character_config(sample_character_config)
        
        expected_config = {
            "template": "\n<Character description>\n{}\n</Character description>\n",
            "configs": [sample_character_config],
        }
        
        assert len(builder.configs) == 1
        assert builder.configs[0] == expected_config

    def test_with_location_config_returns_self(self, builder, sample_location_config):
        """Test that with_location_config returns self for method chaining."""
        result = builder.with_location_config(sample_location_config)
        
        assert result is builder

    def test_with_location_config_adds_config(self, builder, sample_location_config):
        """Test that location config is properly added."""
        builder.with_location_config(sample_location_config)
        
        expected_config = {
            "template": "\n<Location description>\n{}\n</Location description>\n",
            "configs": [sample_location_config],
        }
        
        assert len(builder.configs) == 1
        assert builder.configs[0] == expected_config

    def test_with_current_scene_description_returns_self(self, builder):
        """Test that with_current_scene_description returns self for method chaining."""
        scene_description = "A bustling marketplace filled with merchants and travelers."
        result = builder.with_current_scene_description(scene_description)
        
        assert result is builder

    def test_with_current_scene_description_adds_config(self, builder):
        """Test that scene description is properly added."""
        scene_description = "A bustling marketplace filled with merchants and travelers."
        builder.with_current_scene_description(scene_description)
        
        expected_config = {
            "template": "\n<Current scene description>\n{}\n</Current scene description>\n",
            "configs": [scene_description],
        }
        
        assert len(builder.configs) == 1
        assert builder.configs[0] == expected_config

    def test_method_chaining(self, builder, sample_assistant_configs, sample_character_config, sample_location_config):
        """Test that all methods can be chained together."""
        scene_description = "A bustling marketplace filled with merchants and travelers."
        result = (builder
                 .with_assistant_configs(sample_assistant_configs)
                 .with_character_config(sample_character_config)
                 .with_location_config(sample_location_config)
                 .with_current_scene_description(scene_description))
        
        expected_configs = [
            {
                "template": "\n<General assistant instructions>\n{}\n</General assistant instructions>\n",
                "configs": sample_assistant_configs,
            },
            {
                "template": "\n<Character description>\n{}\n</Character description>\n",
                "configs": [sample_character_config],
            },
            {
                "template": "\n<Location description>\n{}\n</Location description>\n",
                "configs": [sample_location_config],
            },
            {
                "template": "\n<Current scene description>\n{}\n</Current scene description>\n",
                "configs": [scene_description],
            }
        ]
        
        assert result is builder
        assert len(builder.configs) == 4
        assert builder.configs == expected_configs

    def test_build_default_template_only(self, builder):
        """Test building with only the default template."""
        result = builder.build()
        
        assert result == CharacterMoveSystemPromptBuilder.TEMPLATE

    def test_build_custom_template_only(self, custom_template_builder):
        """Test building with only a custom template."""
        result = custom_template_builder.build()
        
        assert result == "Custom system prompt template.\n"

    def test_build_with_scene_description_only(self, builder):
        """Test building with only scene description."""
        scene_description = "A mysterious forest clearing illuminated by moonlight."
        result = builder.with_current_scene_description(scene_description).build()
        
        expected_result = (
            "Assistant is a character in the role play game.\n"
            "Assistant strictly has to follow the character description and general instructions.\n"
            "\n<Current scene description>\n"
            "A mysterious forest clearing illuminated by moonlight.\n"
            "</Current scene description>\n"
        )
        
        assert result == expected_result

    def test_build_with_all_configs(self, builder, sample_assistant_configs, sample_character_config, sample_location_config):
        """Test building a complete prompt with all config types."""
        scene_description = "A bustling marketplace filled with merchants and travelers."
        result = (builder
                 .with_assistant_configs(sample_assistant_configs)
                 .with_character_config(sample_character_config)
                 .with_location_config(sample_location_config)
                 .with_current_scene_description(scene_description)
                 .build())
        
        expected_result = (
            "Assistant is a character in the role play game.\n"
            "Assistant strictly has to follow the character description and general instructions.\n"
            "\n<General assistant instructions>\n"
            "### **Main goal**\n"
            "Be a helpful assistant\n\n"
            "### **Style**\n"
            "Professional and concise\n\n"
            "### **Constraints**\n"
            "No harmful content\n"
            "Stay in character\n"
            "</General assistant instructions>\n"
            "\n<Character description>\n"
            "### **Character**\n"
            "**Name**: Aria\n"
            "**Personality**: Curious and analytical\n"
            "**Background**: Former scientist\n"
            "Lives in a magical world\n"
            "**Abilities**: Spell casting\n"
            "Potion brewing\n"
            "Research\n"
            "</Character description>\n"
            "\n<Location description>\n"
            "### **Location**\n"
            "**Name**: Ancient library\n"
            "**Description**: A vast library filled with mystical tomes\n"
            "**Atmosphere**: Quiet and mysterious\n"
            "**Notable_features**: Floating books\n"
            "Glowing crystals\n"
            "Ancient artifacts\n"
            "</Location description>\n"
            "\n<Current scene description>\n"
            "A bustling marketplace filled with merchants and travelers.\n"
            "</Current scene description>\n"
        )
        
        assert result == expected_result

    @pytest.mark.parametrize("data_type,expected_type", [
        ({"key": "value"}, "dict"),
        ("string", "str"),
        (["list", "items"], "list"),
        (123, "unknown"),
        (None, "unknown"),
    ])
    def test_get_item_data_type(self, builder, data_type, expected_type):
        """Test that _get_item_data_type correctly identifies data types."""
        result = builder._get_item_data_type(data_type)
        assert result == expected_type

    def test_get_title_value_valid_dict(self, builder):
        """Test _get_title_value with valid dictionary."""
        item = {"title": "test_title", "value": "test_value"}
        title, value = builder._get_title_value(item)
        
        assert title == "test_title"
        assert value == "test_value"

    def test_get_title_value_missing_title(self, builder):
        """Test _get_title_value with missing title."""
        item = {"value": "test_value"}
        
        with patch('app.builders.character_move_system_prompt_builder.logger') as mock_logger:
            title, value = builder._get_title_value(item)
            
            assert title == ""
            assert value == ""
            mock_logger.warning.assert_called_once()

    def test_get_title_value_missing_value(self, builder):
        """Test _get_title_value with missing value."""
        item = {"title": "test_title"}
        
        with patch('app.builders.character_move_system_prompt_builder.logger') as mock_logger:
            title, value = builder._get_title_value(item)
            
            assert title == ""
            assert value == ""
            mock_logger.warning.assert_called_once()

    def test_str_renderer(self, builder):
        """Test string rendering."""
        result = builder._str_renderer("hello world")
        assert result == "Hello world"

    def test_str_renderer_in_list(self, builder):
        """Test string rendering when in a list context."""
        result = builder._str_renderer("hello world", in_list=True)
        assert result == "Hello world"

    def test_dict_renderer_not_in_list(self, builder):
        """Test dictionary rendering when not in a list."""
        item = {"title": "name", "value": "John"}
        result = builder._dict_renderer(item, in_list=False)
        
        expected_result = "### **Name**\nJohn"
        assert result == expected_result

    def test_dict_renderer_in_list(self, builder):
        """Test dictionary rendering when in a list."""
        item = {"title": "name", "value": "John"}
        result = builder._dict_renderer(item, in_list=True)
        
        expected_result = "**Name**: John"
        assert result == expected_result

    def test_list_renderer_simple_strings(self, builder):
        """Test list rendering with simple strings."""
        items = ["item1", "item2", "item3"]
        result = builder._list_renderer(items)
        
        expected_result = "Item1\nItem2\nItem3"
        assert result == expected_result

    def test_list_renderer_with_description_string(self, builder):
        """Test list rendering with description string format."""
        items = ["This is a description:", {"title": "item1", "value": "value1"}, {"title": "item2", "value": "value2"}]
        result = builder._list_renderer(items)
        
        expected_result = "This is a description:\n- **Item1**: Value1\n- **Item2**: Value2"
        assert result == expected_result

    def test_list_renderer_in_list_context(self, builder):
        """Test list rendering when in list context."""
        items = ["item1", "item2"]
        result = builder._list_renderer(items, in_list=True)
        
        expected_result = "Item1\nItem2"
        assert result == expected_result

    @pytest.mark.parametrize("items,expected", [
        (["Description", {"title": "item1", "value": "value1"}, {"title": "item2", "value": "value2"}], True),
        (["item1", "item2", "item3"], False),
        (["Description"], False),  # Only one item
        ([1, 2, 3], False),  # No strings
        ([], False),  # Empty list
    ])
    def test_is_list_with_description_string(self, builder, items, expected):
        """Test detection of lists with description string format."""
        result = builder._is_list_with_description_string(items)
        assert result == expected

    def test_build_configs_with_valid_list(self, builder):
        """Test _build_configs with a valid list of configs."""
        configs = [
            {"title": "name", "value": "Test"},
            {"title": "type", "value": "Character"}
        ]
        result = builder._build_configs(configs)
        
        expected_result = "### **Name**\nTest\n\n### **Type**\nCharacter"
        
        assert result == expected_result

    def test_build_configs_with_non_list(self, builder):
        """Test _build_configs with non-list input."""
        with patch('app.builders.character_move_system_prompt_builder.logger') as mock_logger:
            result = builder._build_configs("not a list")
            
            assert result == "not a list"
            mock_logger.warning.assert_called_once()

    def test_get_renderer_unknown_type(self, builder):
        """Test _get_renderer with unknown type logs warning and returns default."""
        with patch('app.builders.character_move_system_prompt_builder.logger') as mock_logger:
            renderer = builder._get_renderer("unknown_type")
            result = renderer("test input")
            
            assert result == "test input"
            mock_logger.warning.assert_called_once()

    def test_get_character_name_valid_config(self, builder):
        """Test _get_character_name with valid character config."""
        character_config = {
            "variables": {"name": "TestCharacter"}
        }
        result = builder._get_character_name(character_config)
        
        assert result == "TestCharacter"

    def test_get_character_name_missing_variables(self, builder):
        """Test _get_character_name with missing variables."""
        character_config = {}
        result = builder._get_character_name(character_config)
        
        assert result == ""

    def test_get_character_name_missing_name(self, builder):
        """Test _get_character_name with missing name in variables."""
        character_config = {"variables": {}}
        result = builder._get_character_name(character_config)
        
        assert result == ""

    def test_complex_nested_structure(self, builder):
        """Test rendering of complex nested data structures."""
        complex_config = {
            "title": "character",
            "value": [
                {"title": "name", "value": "Wizard"},
                {"title": "attributes", "value": ["Intelligence: High", "Wisdom: Medium"]},
                {"title": "spells", "value": ["Fireball", "Heal", "Teleport"]}
            ]
        }
        
        builder.with_character_config(complex_config)
        result = builder.build()
        
        expected_result = (
            "Assistant is a character in the role play game.\n"
            "Assistant strictly has to follow the character description and general instructions.\n"
            "\n<Character description>\n"
            "### **Character**\n"
            "**Name**: Wizard\n"
            "**Attributes**: Intelligence: high\n"
            "Wisdom: medium\n"
            "**Spells**: Fireball\n"
            "Heal\n"
            "Teleport\n"
            "</Character description>\n"
        )
        
        assert result == expected_result

    def test_empty_configs_list(self, builder):
        """Test behavior with empty configs list."""
        result = builder._build_configs([])
        assert result == ""

    def test_multiple_assistant_configs_calls(self, builder):
        """Test calling with_assistant_configs multiple times."""
        config1 = [{"title": "goal1", "value": "First goal"}]
        config2 = [{"title": "goal2", "value": "Second goal"}]
        
        builder.with_assistant_configs(config1).with_assistant_configs(config2)
        result = builder.build()
        
        expected_result = (
            "Assistant is a character in the role play game.\n"
            "Assistant strictly has to follow the character description and general instructions.\n"
            "\n<General assistant instructions>\n"
            "### **Goal1**\n"
            "First goal\n"
            "</General assistant instructions>\n"
            "\n<General assistant instructions>\n"
            "### **Goal2**\n"
            "Second goal\n"
            "</General assistant instructions>\n"
        )
        
        assert result == expected_result