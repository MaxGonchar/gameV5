# Story Creation Enhancement Implementation Plan

## Overview
This plan outlines the implementation of LLM-driven character configuration generation during story creation, based on the SESSION CONTEXT GENERATION ASSISTANT from the character creation framework Phase 2B.

## Current State Analysis

### Current Story Creation Process (`stories_service.py`)
- User provides: `character_id`, `location_id`, `init_scene_description`
- System creates story folder with metadata
- Copies character and location data to story folder
- No LLM-generated session-specific character configs

### Current Character Structure
- Characters have general configs in `character.yaml`
- Structure includes: variables, general instructions, character description, decision drivers, communication style
- Missing: session-specific variables like `{{companion}}`, `{{forbidden_concepts}}`, etc.

### Required Changes Based on Character Creation Framework
According to Phase 2B, we need to generate session-specific variables with the following modifications:
1. `{{companion}}` - Term character uses for user
2. `{{forbidden_concepts}}` - Concepts outside character's world  
3. `{{current_reality}}` - Location with sensory details (based on meeting location)
4. `{{goal}}` - Immediate character goal
5. **Modified Memory Structure:**
   - `{{general meeting event description}}` - What happened during the meeting
   - `{{how it reflects in character memory}}` - Character's internal reflection/interpretation
6. `{{confused_phrase}}` - Character's deflection phrase for forbidden concepts

## Implementation Steps

### Step 1: Extend CreateStoryRequest Model ✅
**File:** `backend/app/models/requests.py`
**Status:** COMPLETED
**Changes:**
- ✅ Added required fields for SESSION CONTEXT GENERATION ASSISTANT:
  - `name: str` - User's name/preferred address
  - `description: str` - User character description/background
  - `context: str` - Background context/world information
  - `meeting_location_description: str` - Where the meeting takes place
  - `meeting_description: str` - How the meeting happens/scenario
- ✅ Maintained backward compatibility with optional `init_scene_description` field
- ✅ Added proper validation with min_length constraints
- ✅ All validation tests passed
- ✅ Existing imports and services work correctly

**Components reused:** Existing validation patterns from current request models

### Step 2: Create General LLM Tool and Session Context Generation ✅
**Files Created:** 
- ✅ `backend/app/services/llm_generation_service.py` - COMPLETED
- ✅ `backend/app/models/session_context.py` - COMPLETED

**Status:** COMPLETED - Ready for Session Context Service implementation

**Implementation:**

#### General LLM Generation Tool ✅
- ✅ **Simplified following YAGNI principle** - Only implemented what we need
- ✅ Generic service accepting: system prompt, user prompt, response model
- ✅ **Uses LangChain chain syntax**: `prompt | llm | parser`
- ✅ Uses existing `VeniceAIChatModel` for LLM integration  
- ✅ Returns structured response based on provided Pydantic model
- ✅ Includes retry logic for reliability (max_retries parameter)
- ✅ Auto-generates format instructions for Pydantic models
- ✅ Comprehensive error handling and logging
- ✅ All tests passed successfully

**Key Features Implemented:**
- `generate_structured_response()` - Only method needed, uses chains
- Configurable retry logic with detailed error logging
- Type-safe generic implementation with TypeVar
- **Clean chain syntax**: `ChatPromptTemplate | VeniceAI | PydanticOutputParser`

**Removed (YAGNI):**
- ❌ `generate_simple_response()` - Not needed for our use case
- ❌ `create_enhanced_system_prompt()` - Format instructions auto-generated

#### Session Context Models and Prompt ✅
- ✅ **Separated concerns** - Prompts and models in dedicated file
- ✅ **SessionContextResponse** - Complete Pydantic model for LLM output
- ✅ **SessionMemory** - Nested model for memory entries
- ✅ **SESSION_CONTEXT_GENERATION_PROMPT** - Comprehensive system prompt
- ✅ **Modified memory structure** implemented:
  - `event_description` - What happened during the meeting
  - `in_character_reflection` - Character's internal reflection/interpretation
- ✅ **Validation rules** - 2-3 memories required, proper field constraints
- ✅ **All 6 session variables** defined according to framework:
  1. `companion` - Term character uses for user
  2. `forbidden_concepts` - Concepts outside character's world
  3. `current_reality` - Location with sensory details format
  4. `goal` - Immediate character goal
  5. `memories` - Modified memory structure (2-3 entries)
  6. `confused_phrase` - Character's deflection phrase
- ✅ All model tests passed successfully

#### Modified Memory Structure
Instead of `{{Event/Fear/Secret}} → behavioral effects`, use:
- `{{general meeting event description}}` - What happened during the meeting
- `{{how it reflects in character memory}}` - Character's internal reflection/interpretation

#### Pydantic Response Model
Define structured output model for LLM response validation

### Step 3: Update StoryDAO for Enhanced Metadata
**File:** `backend/app/dao/story_dao.py`  
**Changes:**
- Modify `create_story` method to accept additional user context data
- Store user context in `meta.yaml` (remove `initial_scene_description`, use `meeting_description` instead)
- Add session-specific character configs to story character copy

**Components to reuse:** 
- Existing YAML handling via `YamlFileHandler`
- Current file copying logic for character/location data

### Step 4: Create Character Enhancement Logic
**File:** `backend/app/services/character_enhancement_service.py` (NEW)
**Purpose:** Merge base character with session-specific configs
**Implementation:**
- Read base character configuration
- Integrate generated session variables into character structure
- Write enhanced character config to story folder
- Maintain backward compatibility with existing character structure

**Components to reuse:**
- `CharacterDAO` for reading base character configs
- `YamlFileHandler` for file operations
- Existing character data structure patterns

### Step 5: Update StoriesService Integration
**File:** `backend/app/services/stories_service.py`
**Changes:**
- Modify `create_story` method to:
  1. Validate extended request data
  2. Call `SessionContextService` to generate session configs
  3. Call `CharacterEnhancementService` to merge configs
  4. Pass enhanced data to `StoryDAO`

**Components to reuse:**
- Existing service initialization patterns
- Error handling and logging from current implementation
- Async operation patterns

### Step 6: Update Story Metadata Structure
**File:** Story `meta.yaml` structure enhancement
**New fields to add:**
```yaml
name: "..."
description: "..."
context: "..."
meeting_location_description: "..."
meeting_description: "..."
session_generated_at: "2024-11-02T10:30:00Z"
```

### Step 7: Enhanced Character Structure  
**File:** Story character `character.yaml` enhancement
**Structure based on provided template:**
```yaml
base_personality:
  name: "..."
  in-universe_self_description: "..."
  sensory_origin_memory: "..."
  character_native_deflection: "..."
  in-character_behavior: "..."
  traits:
    - "..."
  speech_patterns: "..."
  physical_tells: "..."
  goal: "..."
  core_principles:
    - "..."

current_reality:
  scene: "..."
  sensory_details:
    - "..."
    - "..."

memories:
  - event_description: "..."
    in_character_reflection: "..."
  - event_description: "..."
    in_character_reflection: "..."

session:
  companion: "..."
  forbidden_concepts: "..."
  confused_phrase: "..."

general:
  home_world: "..."
  background: "..."
  appearance: "..."
```

### Step 8: Frontend Updates
**Files:** Frontend components requiring user input changes
**Changes:**
- Update story creation form to collect new required fields:
  - `name` - User's name/preferred address
  - `description` - User character description/background  
  - `context` - Background context/world information
  - `meeting_location_description` - Where the meeting takes place
  - `meeting_description` - How the meeting happens/scenario
- Remove `init_scene_description` field
- Update form validation and submission logic

## Implementation Order

### Phase 1: Core Infrastructure (Days 1-2)
1. Update `CreateStoryRequest` model with new user input fields
2. Create `LLMGenerationService` - reusable LLM client
3. Create `SessionContextService` with modified SESSION CONTEXT GENERATION ASSISTANT
4. Define Pydantic models for structured LLM responses
5. Test LLM prompt generation in isolation

### Phase 2: Data Integration (Days 3-4)  
6. Create `CharacterEnhancementService` with new character structure
7. Update `StoryDAO` to handle enhanced metadata (remove `initial_scene_description`)
8. Test character config merging logic with new memory structure

### Phase 3: Service Integration (Day 6)
9. Update `StoriesService` to orchestrate new flow
10. End-to-end testing of story creation
11. Error handling and validation

### Phase 4: Frontend Integration (Day 7)
12. Update frontend story creation form
13. Implement new user input fields collection
14. Test complete user journey

## Testing Strategy

### Unit Tests
- `LLMGenerationService` generic functionality
- `SessionContextService` prompt generation with new memory structure
- `CharacterEnhancementService` config merging with new template structure
- Request model validation with new fields

### Integration Tests  
- Complete story creation flow with new user inputs
- Character config enhancement with proper template structure
- Metadata persistence without `initial_scene_description`

### Manual Testing
- Create story with new enhanced flow and user input fields
- Verify generated session configs follow new memory structure
- Test story gameplay with enhanced character template

## Risk Mitigation

### Backward Compatibility
- Maintain existing story creation API structure
- Add new fields as optional initially
- Ensure old stories continue to work

### LLM Reliability
- Add retry logic for LLM calls
- Validate LLM output format
- Provide fallback default values for session configs

### Performance
- Cache character base configs
- Optimize LLM prompt size
- Add timeout handling for LLM calls

## Acceptance Criteria

### Story Creation Enhancement
- [ ] User can provide extended context for story creation
- [ ] System generates session-specific character variables via LLM
- [ ] Enhanced character configs are properly stored in story folder
- [ ] Original story creation functionality remains intact

### Character Configuration  
- [ ] Generated session variables follow framework specification
- [ ] Character configs include both base + session-specific data
- [ ] Session configs are contextually appropriate for given scenario

### System Integration
- [ ] All existing story/character functionality continues working
- [ ] New LLM service integrates cleanly with existing architecture
- [ ] Proper error handling for LLM failures
- [ ] Performance meets existing standards

## File Dependencies

### Files to Modify
- `backend/app/models/requests.py` - Update with new user input fields
- `backend/app/services/stories_service.py` - Integrate new LLM generation flow
- `backend/app/dao/story_dao.py` - Remove `initial_scene_description`, add new metadata fields
- Frontend story creation components - Add new user input fields

### Files to Create
- `backend/app/services/llm_generation_service.py` - Reusable LLM client
- `backend/app/services/session_context_service.py` - Session-specific generation
- `backend/app/services/character_enhancement_service.py` - Character template merging
- `backend/app/models/session_context.py` - Pydantic models for LLM responses

### Files to Reference
- `docs/Character/character_creation_framework.md` (for prompt templates)
- `backend/app/llm/venice_ai.py` (for LLM integration patterns)
- `backend/app/services/dialogue_summary_service.py` (for service patterns)

## Future Enhancements

### Post-Implementation Improvements
- Cache generated session configs for similar scenarios
- Allow user to regenerate session configs
- Add session config editing interface
- Implement character config versioning

### Framework Extensions  
- Implement other character creation assistants from framework
- Add location enhancement during story creation
- Integrate with character prompt builder for gameplay