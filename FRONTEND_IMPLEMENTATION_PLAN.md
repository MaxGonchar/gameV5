# Frontend Multi-Story Implementation Plan

## Overview
Converting the single-story React frontend to support multiple stories with character and location selection.

## Current State
- Single-page React app with hardcoded story interaction
- Backend already supports multi-story operations with new API endpoints
- Need to implement story selection, creation, and navigation

## Target User Experience
1. **Dashboard** - View all stories, continue existing or create new
2. **Story Creation** - Select character + location, create new story
3. **Story Chat** - Existing chat interface but story-aware

## Implementation Phases

### ✅ Phase 0: Planning
- [x] Analyze backend API endpoints
- [x] Design UX flow and page structure  
- [x] Create implementation plan
- [x] Set up tracking document

### ✅ Phase 1: Foundation
#### Item 1: Restructure API Service Layer
**Status:** ✅ COMPLETED  
**Files:** `frontend/src/services/api.js`, `frontend/src/services/storyService.js`, `frontend/src/services/catalogService.js`, `frontend/src/services/healthService.js`  
**Goal:** Create modular API service structure for multi-story operations

**New Service Structure:**
```
services/
├── api.js              # Common axios config & instance
├── storyService.js     # All story operations  
├── catalogService.js   # Characters + locations
└── healthService.js    # Health checks
```

**Tasks:**
- [x] Create `api.js` with shared axios configuration
- [x] Create `storyService.js` with story functions:
  - `getStories()`, `createStory()`, `sendMessage(storyId, message)`
  - `getStoryHistory(storyId)`, `summarizeStory(storyId, messageId)`
- [x] Create `catalogService.js` with catalog functions:
  - `getCharacters()`, `getLocations()`
- [x] Create `healthService.js` with `checkHealth()`
- [x] Create `testServices.js` for API validation
- [x] Update existing components to use new service structure (completed in Item 5)
- [x] Remove old `storyApi.js` file (completed - legacy files cleaned up)
- [x] Test all new service functions

**API Mappings:**
- `GET /stories` → `storyService.getStories()`
- `POST /stories` → `storyService.createStory()`
- `POST /stories/{story_id}/message` → `storyService.sendMessage(storyId, message)`
- `GET /stories/{story_id}/history` → `storyService.getStoryHistory(storyId)`
- `GET /characters` → `catalogService.getCharacters()` 
- `GET /locations` → `catalogService.getLocations()`

**Service Structure Benefits:**
- **Modular**: Easy to maintain and extend each service independently
- **Future-ready**: Character/location management features can be added to `catalogService.js`
- **Clean imports**: `import { getStories } from '../services/storyService'`
- **Shared config**: Common axios setup in `api.js` used by all services

#### Item 2: Implement Routing System
**Status:** ✅ COMPLETED  
**Files:** `frontend/package.json`, `frontend/src/index.js`, `frontend/src/App.js`  
**Goal:** Add React Router for multi-page navigation

**Tasks:**
- [x] Install React Router: `npm install react-router-dom`
- [x] Set up BrowserRouter in `src/index.js`
- [x] Create route structure in `src/App.js`:
  - `/` - Dashboard (story list)
  - `/create` - Story creation page
  - `/story/:storyId` - Active story chat
- [x] Create placeholder components (Dashboard, CreateStory, StoryChatPage)
- [x] Backup original App.js as App.js.backup
- [x] Test basic routing navigation

### ✅ Phase 2: New Pages

#### Item 3: Create Story Dashboard Page
**Status:** ✅ COMPLETED  
**Files:** `frontend/src/components/Dashboard.js`, `frontend/src/components/StoryCard.js`  
**Goal:** Main landing page with story list and create option

**Tasks:**
- [x] Create `Dashboard.js` component with API integration
- [x] Create `StoryCard.js` component for both story types  
- [x] Create interactive "New Story" card (fully clickable) → `/create`
- [x] Implement story loading with `storyService.getStories()` API
- [x] Add "Continue Story" navigation to `/story/:storyId`
- [x] Position "New Story" card first in the layout
- [x] Style dashboard with CSS (consistent layout, different interactions)
- [x] Add loading and error states
- [x] Test story list display and navigation

**Dashboard Features:**
- Display all user stories (character + location + story ID)
- Continue existing story button → `/story/:storyId`
- Create new story button → `/create`
- Loading states and error handling

**Dashboard Design:**
- **"New Story" card** appears first, is fully interactive (entire card clickable) → `/create`
- **Regular story cards** are non-interactive displays with action buttons
- **Consistent visual layout** but different interaction patterns
- **Future-ready** design for adding story management features (edit, delete, etc.)
- **Card order**: New Story → User Stories (most recent first)

**Interaction Patterns:**
```
┌─────────────┐ ← INTERACTIVE: Entire card = clickable button
│✨ New Story │   Hover effects, cursor pointer
│             │   Click anywhere → /create  
│Create your  │
│next         │
│adventure... │
└─────────────┘

┌─────────────┐ ← NON-INTERACTIVE: Only button clickable
│📖 Story 1  │   Card = display only
│Nira         │   Button = interactive element
│Forest       │   Future: add edit/delete buttons
│             │
│[Continue ▶] │ ← Only this button clickable
└─────────────┘
```

**Implementation Notes:**
- `StoryCard.js` handles both types based on props: `type="new-story"` vs `type="existing-story"`
- Different CSS classes for interaction states
- New story card: `cursor: pointer`, hover effects, onClick handler
- Regular story cards: static display with button interactions only

#### Item 4: Create Story Creation Page  
**Status:** ✅ COMPLETED  
**Files:** `frontend/src/components/CreateStory.js`, `frontend/src/components/CharacterSelector.js`, `frontend/src/components/LocationSelector.js`  
**Goal:** Story creation flow with character and location selection

**Tasks:**
- [x] Create `CreateStory.js` main component with side-by-side layout
- [x] Create `CharacterSelector.js` dropdown component
- [x] Create `LocationSelector.js` dropdown component  
- [x] Load characters with `catalogService.getCharacters()` API
- [x] Load locations with `catalogService.getLocations()` API
- [x] Add initial scene description text area (required field)
- [x] Implement form validation (all fields required)
- [x] Implement story creation with `storyService.createStory()` API
- [x] Add navigation back to dashboard
- [x] Navigate to new story after creation → `/story/:newStoryId`
- [x] Style creation page with CSS (responsive two-column dropdown layout)
- [x] Test full story creation flow

**Creation Flow:**
1. Display character and location dropdowns side-by-side  
2. User selects character + location from dropdown lists
3. User enters initial scene description in text area
4. Call `storyService.createStory()` API
5. Redirect to new story chat page → `/story/:newStoryId`

**Page Layout:**
```
┌─────────────────────────────────────────────┐
│  ✨ Create New Story                       │
│  [← Back to Stories]                        │
│                                             │
│  ┌─────────────────────┐ ┌─────────────────┐│
│  │ Select Character... ▼│ │ Select Location ▼││ ← Side by side
│  └─────────────────────┘ └─────────────────┘│
│                                             │
│  Initial Scene Description:                 │
│  ┌─────────────────────────────────────────┐│
│  │[User enters initial scene text here...] ││ ← Required field
│  │                                         ││
│  └─────────────────────────────────────────┘│
│                                             │
│  [Cancel] [Create Story & Begin Adventure] │ ← Disabled until
└─────────────────────────────────────────────┘   all fields set
```

**Design Benefits:**
- **Compact layout**: Efficient use of horizontal space
- **Desktop-optimized**: No mobile constraints  
- **Future tooltip support**: Left dropdown → right-side tooltip, right dropdown → left-side tooltip
- **Scalable**: Handles any number of characters/locations
- **Form validation**: Clear required field states

### 🔄 Phase 3: Integration

#### Item 5: Adapt Existing Story Page
**Status:** ✅ COMPLETED  
**Files:** `frontend/src/components/StoryChatPage.js` (renamed from `App.js`)  
**Goal:** Make existing chat interface work with specific story IDs

**Tasks:**
- [x] Extract chat logic from `App.js` to `StoryChatPage.js`
- [x] Add storyId parameter from URL using `useParams()`
- [x] Update all API calls to use storyId parameter
- [x] Test chat functionality with different story IDs
- [x] Add navigation back to dashboard
- [x] Handle invalid/missing story IDs with error page

**Changes:**
- `sendMessage(message)` → `sendMessage(storyId, message)`  
- `getStoryHistory()` → `getStoryHistory(storyId)`
- `summarizeStory(messageId)` → `summarizeStory(storyId, messageId)`

#### Item 6: Add Navigation and Error Handling  
**Status:** ⏳ PENDING  
**Files:** `frontend/src/components/Navigation.js`, `frontend/src/components/ErrorBoundary.js`  
**Goal:** Polish user experience with proper navigation and error handling

**Tasks:**
- [ ] Create `Navigation.js` component for consistent navigation
- [ ] Create `ErrorBoundary.js` for React error boundary
- [ ] Add loading states for all API operations  
- [ ] Add proper error messages for API failures
- [ ] Add breadcrumb navigation
- [ ] Test error scenarios (network failures, invalid IDs, etc.)
- [ ] Add success feedback for story creation
- [ ] Style all navigation elements

**Navigation Features:**
- Header with app title and navigation links
- Breadcrumbs showing current page location
- Back buttons where appropriate  
- Consistent loading spinners
- User-friendly error messages

## File Structure (Target)

```
frontend/src/
├── components/
│   ├── ChatHistory.js           # (existing)
│   ├── SceneDescription.js      # (existing) 
│   ├── InputSection.js          # (existing)
│   ├── ErrorMessage.js          # (existing)
│   ├── SuccessMessage.js        # (existing)
│   ├── Dashboard.js             # NEW - story list page
│   ├── StoryCard.js             # NEW - individual story display
│   ├── CreateStory.js           # NEW - story creation page
│   ├── CharacterSelector.js     # NEW - character selection
│   ├── LocationSelector.js      # NEW - location selection
│   ├── StoryChatPage.js         # NEW - refactored from App.js
│   ├── Navigation.js            # NEW - navigation component
│   └── ErrorBoundary.js         # NEW - error boundary
├── services/
│   ├── api.js                  # NEW - common axios config
│   ├── storyService.js         # NEW - story operations
│   ├── catalogService.js       # NEW - characters + locations  
│   ├── healthService.js        # NEW - health checks
│   └── storyApi.js             # LEGACY - to be removed
├── App.js                      # UPDATED - routing setup
└── index.js                    # UPDATED - router setup
```

## API Dependencies

**New Endpoints Used:**
- `GET /api/v1/stories` - List all stories
- `GET /api/v1/characters` - List all characters
- `GET /api/v1/locations` - List all locations
- `POST /api/v1/stories` - Create new story

**Updated Endpoints:**
- `POST /api/v1/stories/{story_id}/message` - Send message to specific story
- `GET /api/v1/stories/{story_id}/history` - Get specific story history  
- `POST /api/v1/stories/{story_id}/summarize/{message_id}` - Summarize specific story

## Testing Strategy

**Manual Testing Approach:**
1. Test each component individually as it's built
2. Test API integration with backend running locally
3. Test full user flows after each phase
4. Test error scenarios (network issues, invalid data, etc.)

**Key Test Scenarios:**
- [ ] Load dashboard with existing stories
- [ ] Create new story with different character/location combinations
- [ ] Continue existing story and send messages
- [ ] Navigate between all pages
- [ ] Handle network errors gracefully
- [ ] Handle invalid story IDs

## Dependencies to Install

```bash
cd frontend
npm install react-router-dom
```

## Progress Tracking

- ✅ Completed
- 🔄 In Progress  
- ⏳ Pending
- ❌ Blocked

**Current Status:** ✅ Phase 2 Completed - Ready for Phase 3 (Integration)

---

## Notes
- Backend API is ready and functional
- Focus on clean, simple implementation first
- Polish and advanced features can be added later
- Manual testing sufficient for MVP