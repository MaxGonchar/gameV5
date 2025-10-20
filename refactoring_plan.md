# Multi-Story Data Structure Refactoring Plan

## Overview
Refactor the application to support multiple stories with the new data structure:
```
data/
├── stories/
│   └── <story_id>/
│       ├── characters/
│       │   └── <character_id>/
│       │       └── character.yaml
|       ├── locations/
|       │   └── <location_id>/
|       │       └── location.yaml
|       ├── chat_history.yaml
|       └── meta.yaml
├── characters/  # Global character templates (existing)
└── locations/   # Global location templates (existing)
```

## Phase 1: DAO Layer Refactoring
*Priority: Test and validate each DAO independently*

### ✅ Step 1: Refactor CharacterDAO - COMPLETED ✅
- **Backward Compatible**: `CharacterDAO()` still defaults to `"data/characters"`
- **Generic Design**: `CharacterDAO(characters_dir="any/path/to/characters")`
- **Usage Examples**:
  - Characters Service: `dao = CharacterDAO()` (unchanged)
  - Story Characters: `dao = CharacterDAO(characters_dir=f"data/stories/{story_id}/characters")`
  - Future Use Cases: `dao = CharacterDAO(characters_dir="any/other/feature/characters")`
- **Clean Architecture**: DAO doesn't know about specific use cases, just handles character operations
- **Test**: ✅ PASSED - All backward compatibility maintained + flexible for any future use case

### ✅ Step 2: Refactor LocationDAO - COMPLETED ✅
- **Backward Compatible**: `LocationDAO()` still defaults to `"data/locations"`
- **Generic Design**: `LocationDAO(locations_dir="any/path/to/locations")`
- **Usage Examples**:
  - Locations Service: `dao = LocationDAO()` (unchanged)
  - Story Locations: `dao = LocationDAO(locations_dir=f"data/stories/{story_id}/locations")`
  - Future Use Cases: `dao = LocationDAO(locations_dir="any/other/feature/locations")`
- **Clean Architecture**: DAO doesn't know about specific use cases, just handles location operations
- **Test**: ✅ PASSED - Successfully loads:
  - 1 global location (The Stillwood Glade)
  - 1 story location (The Stillwood Glade) 
  - Same location exists in both global and story-specific paths

### ✅ Step 3: Refactor ChatHistoryDAO
- **Current**: `ChatHistoryDAO(chat_history_file="data/chat_history/chat_history.yaml")`
- **New**: `ChatHistoryDAO(story_id: str, stories_dir="data/stories")`
- Update path to: `data/stories/{story_id}/chat_history.yaml`
- **Test**: Verify chat history loading/saving works with story-specific paths

### ✅ Step 4: Refactor MetaDAO
- **Current**: `MetaDAO(meta_dir="data")`
- **New**: `MetaDAO(story_id: str, stories_dir="data/stories")`
- Update path to: `data/stories/{story_id}/meta.yaml`
- **Test**: Verify meta loading works with story-specific paths

## Phase 2: Update GlobalState Class
*Priority: Integrate updated DAOs with GlobalState*

### ✅ Step 5: Update GlobalState Constructor
- **Current**: `GlobalState.__init__(character_name: str = "nira")`
- **New**: `GlobalState.__init__(story_id: str, character_id: str = None)`
- Modify `GlobalState` to accept and store `story_id`
- Update DAO instantiation to pass `story_id` to each DAO
- Remove hardcoded character/user constants
- **Test**: Verify GlobalState initialization works with story context

### ✅ Step 6: Update GlobalState Methods
- Update method signatures to work with story context
- Ensure all DAO operations use story-specific paths
- **Test**: Verify all GlobalState operations work with story-specific data

## Phase 3: Service Layer Updates
*Priority: Update services to use story-aware GlobalState*

### ✅ Step 7: Update StoryService
- **Current**: `StoryService.__init__(character_name: str = "nira")`
- **New**: `StoryService.__init__(story_id: str, character_id: str = None)`
- Pass `story_id` to `GlobalState` initialization
- Update all method signatures to work with story context
- **Test**: Verify StoryService works end-to-end with story context

### ✅ Step 8: Update DialogueSummaryService
- **Current**: `DialogueSummaryService.__init__(character_name: str = "nira")`
- **New**: `DialogueSummaryService.__init__(story_id: str, character_id: str = None)`
- Update DAO instantiations to use story-specific paths
- **Test**: Verify dialogue summarization works with story context

## Phase 4: API Layer Changes
*Priority: Update API contract and handlers*

### ✅ Step 9: Update Request/Response Models
- Add `story_id` parameter to request models (`SendMessageRequest`)
- Update response models to include `story_id` where relevant
- **Test**: Verify API models validate correctly

### ✅ Step 10: Update Story Endpoints
- **Current URLs**: 
  - `POST /api/v1/story/message`
  - `GET /api/v1/story/history`
  - `POST /api/v1/story/summarize/{message_id}`
- **New URLs**:
  - `POST /api/v1/stories/{story_id}/message`
  - `GET /api/v1/stories/{story_id}/history`
  - `POST /api/v1/stories/{story_id}/summarize/{message_id}`
- **Test**: Verify endpoints work with story ID parameter

### ✅ Step 11: Update Endpoint Handlers
- Modify story route handlers to extract `story_id` from path
- Update service instantiation to pass `story_id`
- Update global service instance management to be story-specific
- **Test**: Verify full API functionality works end-to-end

## Phase 5: Testing & Validation
*Priority: Comprehensive testing and cleanup*

### ✅ Step 12: Update Tests
- Modify existing tests to work with story-specific paths
- Add tests for new story-aware functionality
- Test data isolation between stories
- **Test**: All existing functionality works with new structure

### ✅ Step 13: Configuration & Cleanup
- Remove hardcoded constants where appropriate
- Add proper error handling for story not found, invalid story ID
- Add validation to ensure story IDs are valid UUIDs
- **Test**: Error scenarios are handled gracefully

## Implementation Notes

### Path Construction Pattern
All DAO classes will construct paths like:
```python
story_dir = Path(stories_dir) / story_id
specific_file = story_dir / "specific_file.yaml"
```

### Service Instance Management
Consider story-specific service instances or service factory pattern instead of global singletons.

### Error Handling
- Story not found errors
- Invalid story ID validation
- Missing story data files

### Data Migration
The existing story in `data/stories/fdf6b8ce-57e0-4962-91bd-4f915c3f61e9/` can be used for testing.

## Skipped for Now
- ❌ **Add Story Management Endpoints** - Will focus only on supporting new folder structure
- ❌ **Frontend Updates** - Frontend will be significantly refactored later
- ❌ **Data Migration Strategy** - Using existing story data for testing

## Current Story ID for Testing
Use existing story: `fdf6b8ce-57e0-4962-91bd-4f915c3f61e9`