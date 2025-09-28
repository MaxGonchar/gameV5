import pytest
from unittest.mock import patch
from app.objects.character import Character


class TestCharacter:
    """Test suite for Character class."""
    
    @pytest.fixture
    def minimal_character_data(self):
        """Minimal character data for basic functionality tests."""
        return {
            "name": "TestChar",
            "variables": {"name": "TestChar"},
            "assistant": [
                {"title": "main goal", "type": "system", "value": "Be helpful"}
            ],
            "character": [
                {"title": "name", "value": "TestChar"},
                {"title": "personality", "value": "friendly"}
            ]
        }
    
    @pytest.fixture
    def character_data_with_dynamics(self):
        """Character data with dynamic configurations for advanced tests."""
        return {
            "name": "DynamicChar",
            "variables": {"name": "DynamicChar"},
            "assistant": [
                {"title": "main goal", "type": "system", "value": "Adapt behavior"}
            ],
            "character": [
                {"title": "name", "value": "DynamicChar"},
                {"title": "mood", "value": "neutral"}
            ],
            "parameters": {"happiness": 0.5},
            "dynamic_configs": [
                {
                    "parameter": "happiness",
                    "default": 0.0,
                    "decay_level": 0.9,
                    "dynamic_directives": {
                        "positive": {
                            "axis": [0.1, 0.2, 0.3]  # Simplified 3D vector
                        },
                        "negative": {
                            "axis": [-0.1, -0.2, -0.3]  # Simplified 3D vector
                        }
                    },
                    "levels": [
                        {
                            "range": [0.0, 1.0],
                            "character_impacts": [
                                {"title": "mood", "value": "happy"}
                            ]
                        },
                        {
                            "range": [-1.0, 0.0],
                            "character_impacts": [
                                {"title": "mood", "value": "sad"}
                            ]
                        }
                    ]
                }
            ]
        }
    
    @pytest.fixture
    def character_data_with_memory(self):
        """Character data with memory for memory-related tests."""
        return {
            "name": "MemoryChar",
            "variables": {"name": "MemoryChar"},
            "assistant": [
                {"title": "main goal", "type": "system", "value": "Remember things"}
            ],
            "character": [
                {"title": "name", "value": "MemoryChar"},
                {"title": "memory", "value": ["Initial memory"]}
            ]
        }


class TestCharacterInitialization(TestCharacter):
    """Tests for Character initialization."""
    
    def test_init_with_minimal_data(self, minimal_character_data):
        """Test initialization with minimal required data."""
        character = Character(minimal_character_data)
        
        assert character.name == "TestChar"
        assert character.variables == {"name": "TestChar"}
        
        # Check actual assistant content, not just length
        assert character.assistant == [
            {"title": "main goal", "type": "system", "value": "Be helpful"}
        ]
        
        # Check actual character content, not just length
        assert character.character == [
            {"title": "name", "value": "TestChar"},
            {"title": "personality", "value": "friendly"}
        ]
        
        # Verify dynamic configs are properly uninitialized
        assert character.parameters is None
        assert character.dynamic_directives is None
        assert character.dynamic_configs == []
    
    def test_init_with_dynamic_configs(self, character_data_with_dynamics):
        """Test initialization with dynamic configurations."""
        character = Character(character_data_with_dynamics)
        
        assert character.name == "DynamicChar"
        assert character.variables == {"name": "DynamicChar"}
        
        # Check actual assistant content
        assert character.assistant == [
            {"title": "main goal", "type": "system", "value": "Adapt behavior"}
        ]
        
        # Check actual character content
        assert character.character == [
            {"title": "name", "value": "DynamicChar"},
            {"title": "mood", "value": "neutral"}
        ]
        
        # Check specific parameter values
        assert character.parameters == {"happiness": 0.5}
        
        # Check that dynamic directives were properly initialized
        expected_dynamic_directives = {
            "happiness": {
                "parameter": "happiness",
                "default": 0.0,
                "decay_level": 0.9,
                "dynamic_directives": {
                    "positive": {
                        "axis": [0.1, 0.2, 0.3]
                    },
                    "negative": {
                        "axis": [-0.1, -0.2, -0.3]
                    }
                },
                "levels": [
                    {
                        "range": [0.0, 1.0],
                        "character_impacts": [
                            {"title": "mood", "value": "happy"}
                        ]
                    },
                    {
                        "range": [-1.0, 0.0],
                        "character_impacts": [
                            {"title": "mood", "value": "sad"}
                        ]
                    }
                ]
            }
        }
        assert character.dynamic_directives == expected_dynamic_directives
        
        # Check the actual dynamic config structure
        assert character.dynamic_configs == character_data_with_dynamics["dynamic_configs"]
    
    def test_init_missing_required_fields(self):
        """Test initialization fails with missing required fields."""
        incomplete_data = {"name": "TestChar"}
        
        with pytest.raises(ValueError, match="Invalid character_data, missing key"):
            Character(incomplete_data)
    
    def test_init_dynamic_configs_sets_default_parameters(self):
        """Test that dynamic configs set default parameters when not provided."""
        data = {
            "name": "TestChar",
            "variables": {"name": "TestChar"},
            "assistant": [{"title": "goal", "value": "test"}],
            "character": [{"title": "name", "value": "TestChar"}],
            "dynamic_configs": [
                {
                    "parameter": "mood",
                    "default": 0.8,
                    "dynamic_directives": {
                        "positive": {"axis": [1, 0, 0]},
                        "negative": {"axis": [-1, 0, 0]}
                    }
                }
            ]
        }
        
        character = Character(data)
        assert character.parameters is not None
        assert character.parameters["mood"] == 0.8


class TestCharacterConversionMethods(TestCharacter):
    """Tests for Character conversion methods."""
    
    def test_to_prompt_dict(self, minimal_character_data):
        """Test conversion to prompt dictionary."""
        character = Character(minimal_character_data)
        prompt_dict = character.to_prompt_dict()
        
        # Check actual prompt dictionary content
        expected_prompt_dict = {
            "assistant": [
                {"title": "main goal", "type": "system", "value": "Be helpful"}
            ],
            "character": [
                {"title": "name", "value": "TestChar"},
                {"title": "personality", "value": "friendly"}
            ]
        }
        assert prompt_dict == expected_prompt_dict
    
    def test_to_dict_minimal(self, minimal_character_data):
        """Test conversion to dictionary with minimal data."""
        character = Character(minimal_character_data)
        char_dict = character.to_dict()
        
        # Check actual dictionary content, not just keys
        expected_dict = {
            "name": "TestChar",
            "variables": {"name": "TestChar"},
            "assistant": [
                {"title": "main goal", "type": "system", "value": "Be helpful"}
            ],
            "character": [
                {"title": "name", "value": "TestChar"},
                {"title": "personality", "value": "friendly"}
            ]
        }
        assert char_dict == expected_dict
    
    def test_to_dict_with_dynamics(self, character_data_with_dynamics):
        """Test conversion to dictionary with dynamic configurations."""
        character = Character(character_data_with_dynamics)
        char_dict = character.to_dict()
        
        # Check actual dictionary content with dynamics
        expected_dict = {
            "name": "DynamicChar",
            "variables": {"name": "DynamicChar"},
            "assistant": [
                {"title": "main goal", "type": "system", "value": "Adapt behavior"}
            ],
            "character": [
                {"title": "name", "value": "DynamicChar"},
                {"title": "mood", "value": "neutral"}
            ],
            "parameters": {"happiness": 0.5},
            "dynamic_configs": character_data_with_dynamics["dynamic_configs"]
        }
        assert char_dict == expected_dict


class TestCharacterMemoryMethods(TestCharacter):
    """Tests for Character memory functionality."""
    
    def test_get_memory_with_existing_memory_list(self, character_data_with_memory):
        """Test getting memory when memory exists as a list."""
        character = Character(character_data_with_memory)
        memory = character.get_memory()
        
        assert memory == ["Initial memory"]
    
    def test_get_memory_with_string_memory(self):
        """Test getting memory when memory exists as a string."""
        data = {
            "name": "TestChar",
            "variables": {"name": "TestChar"},
            "assistant": [{"title": "goal", "value": "test"}],
            "character": [
                {"title": "name", "value": "TestChar"},
                {"title": "memory", "value": "Single memory string"}
            ]
        }
        character = Character(data)
        memory = character.get_memory()
        
        assert memory == ["Single memory string"]
    
    def test_get_memory_no_memory_field(self, minimal_character_data):
        """Test getting memory when no memory field exists."""
        character = Character(minimal_character_data)
        memory = character.get_memory()
        
        assert memory == []
    
    def test_get_memory_empty_memory(self):
        """Test getting memory when memory field is empty."""
        data = {
            "name": "TestChar",
            "variables": {"name": "TestChar"},
            "assistant": [{"title": "goal", "value": "test"}],
            "character": [
                {"title": "name", "value": "TestChar"},
                {"title": "memory", "value": []}
            ]
        }
        character = Character(data)
        memory = character.get_memory()
        
        assert memory == []
    
    def test_add_item_to_memory_existing_memory(self, character_data_with_memory):
        """Test adding memory item when memory already exists."""
        character = Character(character_data_with_memory)
        character.add_item_to_memory("New memory")
        
        memory = character.get_memory()
        assert memory == ["Initial memory", "New memory"]
    
    def test_add_item_to_memory_no_existing_memory(self, minimal_character_data):
        """Test adding memory item when no memory exists."""
        character = Character(minimal_character_data)
        character.add_item_to_memory("First memory")
        
        memory = character.get_memory()
        assert memory == ["First memory"]
    
    def test_add_item_to_memory_string_memory(self):
        """Test adding memory item when existing memory is a string."""
        data = {
            "name": "TestChar",
            "variables": {"name": "TestChar"},
            "assistant": [{"title": "goal", "value": "test"}],
            "character": [
                {"title": "name", "value": "TestChar"},
                {"title": "memory", "value": "Old memory"}
            ]
        }
        character = Character(data)
        character.add_item_to_memory("New memory")
        
        memory = character.get_memory()
        assert memory == ["Old memory", "New memory"]
    
    def test_add_item_to_memory_none_value(self):
        """Test adding memory item when memory value is None."""
        data = {
            "name": "TestChar",
            "variables": {"name": "TestChar"},
            "assistant": [{"title": "goal", "value": "test"}],
            "character": [
                {"title": "name", "value": "TestChar"},
                {"title": "memory", "value": None}
            ]
        }
        character = Character(data)
        character.add_item_to_memory("New memory")
        
        memory = character.get_memory()
        assert memory == ["New memory"]


class TestCharacterDynamicBehavior(TestCharacter):
    """Tests for Character dynamic behavior functionality."""
    
    def test_calculate_impact_positive_similarity(self):
        """Test impact calculation with positive similarity."""
        character = Character({
            "name": "TestChar",
            "variables": {"name": "TestChar"},
            "assistant": [{"title": "goal", "value": "test"}],
            "character": [{"title": "name", "value": "TestChar"}]
        })
        
        positive_axis = [1.0, 0.0, 0.0]
        negative_axis = [0.0, 1.0, 0.0]
        message_vector = [1.0, 0.0, 0.0]  # Aligned with positive
        
        impact = character._calculate_impact(positive_axis, negative_axis, message_vector)
        # Expected: pos_sim = 1.0 (perfect alignment), neg_sim = 0.0 (orthogonal)
        # So impact = 1.0 - 0.0 = 1.0
        assert abs(impact - 1.0) < 1e-10  # Use small epsilon for floating-point comparison
    
    def test_calculate_impact_negative_similarity(self):
        """Test impact calculation with negative similarity."""
        character = Character({
            "name": "TestChar",
            "variables": {"name": "TestChar"},
            "assistant": [{"title": "goal", "value": "test"}],
            "character": [{"title": "name", "value": "TestChar"}]
        })
        
        positive_axis = [1.0, 0.0, 0.0]
        negative_axis = [0.0, 1.0, 0.0]
        message_vector = [0.0, 1.0, 0.0]  # Aligned with negative
        
        impact = character._calculate_impact(positive_axis, negative_axis, message_vector)
        # Expected: pos_sim = 0.0 (orthogonal), neg_sim = 1.0 (perfect alignment)
        # So impact = 0.0 - 1.0 = -1.0
        assert abs(impact - (-1.0)) < 1e-10  # Use small epsilon for floating-point comparison
    
    def test_calculate_impact_diagonal_vectors(self):
        """Test impact calculation with diagonal vectors for precision validation."""
        character = Character({
            "name": "TestChar",
            "variables": {"name": "TestChar"},
            "assistant": [{"title": "goal", "value": "test"}],
            "character": [{"title": "name", "value": "TestChar"}]
        })
        
        positive_axis = [3.0, 4.0, 0.0]  # Length = 5
        negative_axis = [1.0, 0.0, 0.0]  # Length = 1
        message_vector = [6.0, 8.0, 0.0]  # Length = 10, same direction as positive
        
        impact = character._calculate_impact(positive_axis, negative_axis, message_vector)
        # Expected: pos_sim = (18+32+0)/(10*5) = 50/50 = 1.0
        # Expected: neg_sim = (6+0+0)/(10*1) = 6/10 = 0.6
        # So impact = 1.0 - 0.6 = 0.4
        assert abs(impact - 0.4) < 1e-10
    
    def test_map_to_sigmoid_range(self):
        """Test sigmoid mapping keeps values in expected range."""
        character = Character({
            "name": "TestChar",
            "variables": {"name": "TestChar"},
            "assistant": [{"title": "goal", "value": "test"}],
            "character": [{"title": "name", "value": "TestChar"}]
        })
        
        # Test various inputs
        test_values = [-10, -1, 0, 1, 10]
        for value in test_values:
            result = character.map_to_sigmoid(value)
            assert -1 <= result <= 1
    
    def test_update_config_with_decay(self, character_data_with_dynamics):
        """Test parameter update with decay applied."""
        character = Character(character_data_with_dynamics)
        assert character.parameters is not None
        # Initial happiness = 0.5 (from fixture)
        
        config = character.dynamic_configs[0]
        embeddings = [0.5, 0.5, 0.5]  # Test embeddings
        
        with patch.object(character, '_update_character_according_to_config'):
            character._update_config(config, embeddings)
        
        # Calculate expected result step by step:
        # 1. Initial happiness = 0.5
        # 2. Apply decay: 0.5 * 0.9 = 0.45
        # 3. Calculate impact:
        #    - pos_sim = 0.926 (positive embeddings align with positive axis)
        #    - neg_sim = -0.926 (positive embeddings oppose negative axis)
        #    - impact_raw = 0.926 - (-0.926) = 1.852
        # 4. Apply sigmoid: 2*sigmoid(1.852) - 1 = 0.729
        # 5. Add to decayed: 0.45 + 0.729 = 1.179
        # 6. Clamp to [-1, 1]: max(min(1.179, 1.0), -1.0) = 1.0
        
        expected_happiness = 1.0  # Should be clamped to maximum
        assert abs(character.parameters["happiness"] - expected_happiness) < 1e-10
    
    def test_correct_property_updates_character(self):
        """Test that _correct_property updates character correctly."""
        data = {
            "name": "TestChar",
            "variables": {"name": "TestChar"},
            "assistant": [{"title": "goal", "value": "test"}],
            "character": [
                {"title": "name", "value": "TestChar"},
                {"title": "mood", "value": "neutral"}
            ]
        }
        character = Character(data)
        
        new_property = {"title": "mood", "value": "happy"}
        character._correct_property("mood", new_property)
        
        # Should have replaced the mood property
        mood_properties = [p for p in character.character if p["title"].lower() == "mood"]
        assert len(mood_properties) == 1
        assert mood_properties[0]["value"] == "happy"
    
    def test_update_character_according_to_config(self, character_data_with_dynamics):
        """Test character update based on config levels."""
        character = Character(character_data_with_dynamics)
        assert character.parameters is not None
        character.parameters["happiness"] = 0.7  # Positive range
        
        config = character.dynamic_configs[0]
        
        with patch.object(character, '_correct_property') as mock_correct:
            character._update_character_according_to_config(config)
            mock_correct.assert_called_once()
    
    def test_update_dynamic_configs_according_to_message_embeddings(self, character_data_with_dynamics):
        """Test full dynamic config update pipeline."""
        character = Character(character_data_with_dynamics)
        embeddings = [0.8, 0.6, 0.4]  # Some test embeddings
        
        with patch.object(character, '_update_config') as mock_update:
            character.update_dynamic_configs_according_to_message_embeddings(embeddings)
            mock_update.assert_called_once_with(character.dynamic_configs[0], embeddings)


class TestCharacterEdgeCases(TestCharacter):
    """Tests for edge cases and error handling."""
    
    def test_memory_case_insensitive_matching(self):
        """Test that memory matching is case insensitive."""
        data = {
            "name": "TestChar",
            "variables": {"name": "TestChar"},
            "assistant": [{"title": "goal", "value": "test"}],
            "character": [
                {"title": "name", "value": "TestChar"},
                {"title": "MEMORY", "value": ["test memory"]}  # Uppercase
            ]
        }
        character = Character(data)
        memory = character.get_memory()
        
        assert memory == ["test memory"]
    
    def test_correct_property_case_insensitive_matching(self):
        """Test that property correction is case insensitive."""
        data = {
            "name": "TestChar",
            "variables": {"name": "TestChar"},
            "assistant": [{"title": "goal", "value": "test"}],
            "character": [
                {"title": "name", "value": "TestChar"},
                {"title": "MOOD", "value": "neutral"}  # Uppercase
            ]
        }
        character = Character(data)
        
        new_property = {"title": "mood", "value": "happy"}  # lowercase
        character._correct_property("mood", new_property)
        
        # Should have found and replaced the MOOD property
        mood_properties = [p for p in character.character if p["title"].lower() == "mood"]
        assert len(mood_properties) == 1
        assert mood_properties[0]["value"] == "happy"
    
    def test_parameters_clamping(self, character_data_with_dynamics):
        """Test that parameters are clamped to [-1, 1] range."""
        character = Character(character_data_with_dynamics)
        assert character.parameters is not None
        
        # Test upper bound clamping
        character.parameters["happiness"] = 2.0
        config = character.dynamic_configs[0]
        embeddings = [1.0, 1.0, 1.0]  # High positive impact
        
        with patch.object(character, '_update_character_according_to_config'):
            character._update_config(config, embeddings)
        
        assert character.parameters["happiness"] <= 1.0
        
        # Test lower bound clamping
        character.parameters["happiness"] = -2.0
        embeddings = [-1.0, -1.0, -1.0]  # High negative impact
        
        with patch.object(character, '_update_character_according_to_config'):
            character._update_config(config, embeddings)
        
        assert character.parameters["happiness"] >= -1.0
    
    def test_no_dynamic_configs_returns_none(self):
        """Test initialization with no dynamic configs returns None for parameters."""
        data = {
            "name": "TestChar",
            "variables": {"name": "TestChar"},
            "assistant": [{"title": "goal", "value": "test"}],
            "character": [{"title": "name", "value": "TestChar"}]
        }
        character = Character(data)
        
        assert character.parameters is None
        assert character.dynamic_directives is None