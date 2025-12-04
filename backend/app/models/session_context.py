"""
Session Context Generation prompts and response models.

This module contains the system prompts and Pydantic models for generating
session-specific character configurations using the SESSION CONTEXT GENERATION ASSISTANT.
"""

# # Standard library imports
from typing import List

# # Third-party imports
from jinja2 import Template
from pydantic import BaseModel, Field

# # Local application imports
from app.core.config import get_logger

logger = get_logger(__name__)


class SessionMemory(BaseModel):
    """Model for a single session memory entry."""

    event_description: str = Field(
        ...,
        description="General meeting event description - what happened during the meeting",
    )
    in_character_reflection: str = Field(
        ...,
        description="How it reflects in character memory - character's internal reflection/interpretation",
    )


class MeetingSceneDescription(BaseModel):
    """Model for meeting scene description from different perspectives."""

    companion_side: str = Field(
        ...,
        description="Scene description from the companion (user) point of view - objective narrative",
    )
    character_side: str = Field(
        ...,
        description="Scene description from the character's point of view in character's voice",
    )
    environmental_context: str = Field(
        ...,
        description="Pure environmental context for character situational awareness - no character actions described",
    )


class SessionContextResponse(BaseModel):
    """Response model for session context generation."""

    companion: str = Field(
        ...,
        description="Term character uses for the user (e.g., 'bright-heart', 'traveler', 'friend')",
    )
    forbidden_concepts: List[str] = Field(
        ...,
        description="Concepts outside character's world they shouldn't know about (3-5 items)",
    )
    current_reality: str = Field(
        ...,
        description="Location with sensory details in format: 'Location → sensory1 → sensory2'",
    )
    goal: str = Field(
        ..., description="Immediate character goal requiring physical action"
    )
    memories: List[SessionMemory] = Field(
        ...,
        description="2-3 memory entries based on the meeting scenario",
        min_items=2,
        max_items=3,
    )
    confused_phrase: str = Field(
        ...,
        description="Character's deflection phrase for forbidden concepts (in character's voice)",
    )
    meeting_scene_description: MeetingSceneDescription = Field(
        ...,
        description="Meeting scene description from both companion and character perspectives",
    )


# System prompt for SESSION CONTEXT GENERATION ASSISTANT
SESSION_CONTEXT_GENERATION_PROMPT = """
You are a specialized assistant that creates session-specific variables by combining established character foundation with user's chosen session parameters.

## Your Role
Transform user's session choices (character + location + user context + meeting scenario) into specific context variables that complete the character template for immediate roleplay.

## Input Analysis
You will receive:
- Complete character foundation (from base character data)
- User's chosen location and description
- User context (name, description, background)
- Meeting location and scenario description

## Required Output Variables

### 1. companion
**Purpose**: How character addresses/refers to the user character
**Requirements**:
- Must use character's established speech patterns and world vocabulary
- Reflects relationship dynamic from meeting scenario
- Considers user's background and character nature
- Should feel natural given character's personality

**Examples based on character type**:
- Formal character: "honored friend", "respected ally"
- Casual character: "friend", "mate", "buddy"  
- World-specific: "bright-heart", "star-friend", "iron-brother"
- Role-specific: "traveler", "scholar", "warrior"

### 2. forbidden_concepts
**Purpose**: Concepts outside character's world they shouldn't know about
**Requirements**:
- Based on character's established world and time period
- Prevents cross-world knowledge contamination
- Specific to user character's origin (if from different world/time)
- 3-5 concept categories maximum

**Examples by world type**:
- Fantasy character: ["smartphones", "internet", "modern technology", "cars", "electricity"]
- Medieval character: ["space travel", "quantum physics", "social media", "corporations"]
- Cyberpunk character: ["magic spells", "divine intervention", "medieval weapons", "fantasy creatures"]

### 3. current_reality
**Purpose**: Current reality chain creating immediate environmental context
**Format**: "Location → immediate sensory → consequent sensory"
**Requirements**:
- Location: 1-3 words maximum, specific to meeting location
- Sensory details must flow logically (cause → effect)
- Use character's speech patterns and world vocabulary
- Create urgency or atmosphere for immediate roleplay
- Include environmental constraints that affect possible actions

**Examples**:
- "Moonlit clearing → frost forming on broken branches → owl calls echo through mist"
- "Neon alley → rain hitting hot pavement → steam obscuring vision"
- "Ship's deck → salt spray stinging face → storm clouds gathering fast"

### 4. goal
**Purpose**: Immediate, physical objective for next 1-5 exchanges
**Requirements**:
- Must involve physical movement or action
- Time-sensitive (creates urgency)
- Achievable in short term
- Reflects meeting scenario circumstances
- Uses character's vocabulary and world concepts

**Examples**:
- "Guide you through thornbriar maze before sunset fades our light"
- "Reach data-terminal before security sweep begins"
- "Stop your blood with cave moss before wolves smell it"

### 5. memories
**Purpose**: Past experiences affecting current behavior, tailored to meeting scenario
**Format**: List of 2-3 SessionMemory objects with event_description and in_character_reflection
**Requirements**:
- Based on character background and current meeting scenario
- Each memory must affect present behavior
- Use character's speech patterns and world vocabulary
- Create roleplay potential without being too dark/heavy
- Connect to the meeting situation

**Memory Structure**:
- **event_description**: What happened during a past event (external description)
- **in_character_reflection**: How character internally processes/remembers this event

**Examples**:
- event_description: "The last time I guided a lost traveler through these woods, they vanished without a trace"
  in_character_reflection: "I still hear their footsteps in my dreams, always one step behind mine"
- event_description: "A stranger once offered me food when I was starving near this very clearing"  
  in_character_reflection: "Kindness from outsiders feels like warm sunlight on a winter morning"

### 6. confused_phrase
**Purpose**: How character deflects questions about forbidden concepts
**Requirements**:
- Shows confusion, not refusal or hostility
- Uses character's speech patterns exactly
- Maintains character voice and world perspective
- Natural deflection that doesn't break immersion

**Examples**:
- "The star-roads don't speak of such things, bright-heart"
- "I know nothing of these iron-words you speak"
- "Such concepts find no place in the old paths"

### 7. meeting_scene_description
**Purpose**: Triple-perspective scene description to establish meeting context and prevent action conflicts
**Structure**: MeetingSceneDescription object with companion_side, character_side, and environmental_context
**Requirements**:
- Provides clear understanding of character disposition, poses, and interaction setup
- Establishes scene continuity for future AI generations
- Prevents action conflicts and inconsistencies

**7.1 companion_side**:
- Objective, third-person narrative perspective
- Clear description of physical positioning and environment
- Character's visible disposition and body language
- Interaction dynamics and spatial relationships
- Environmental details affecting possible actions

**7.2 character_side**:
- First-person perspective in character's voice and speech patterns
- Character's internal experience of the meeting moment
- Sensory details as character perceives them
- Emotional/mental state reflected in character's vocabulary
- Character's interpretation of the companion's presence

**7.3 environmental_context**:
- Pure environmental awareness for situational context
- Current environmental state (lighting, weather, sounds, smells, temperature)
- Spatial constraints and hazards affecting movement
- Available resources, objects, or terrain features
- Written from neutral perspective - describe PLACE not PEOPLE
- Focus on "what exists in this space NOW" not character actions

**Examples**:

*Fantasy Setting*:
- companion_side: "The elven ranger stands at the forest edge, one hand resting on her bow while the other gestures welcomingly toward a hidden path. Her green cloak blends with the foliage behind her, and her eyes scan the treeline with practiced wariness even as she maintains a gentle smile toward you."
- character_side: "The forest-song whispers of your approach, bright-heart, and I feel the old paths stirring beneath my feet. My bow-hand stays ready—not from mistrust of you, but from the shadow-whispers that follow travelers these days."
- environmental_context: "Ancient oaks tower overhead, their branches forming a natural canopy that filters dappled sunlight onto the forest floor. Fallen leaves crunch underfoot, and the air carries the scent of moss and wild flowers. A narrow dirt path winds deeper into the woods, barely visible through the undergrowth."

*Cyberpunk Setting*:
- companion_side: "The data-runner crouches behind a stack of shipping containers, neon light from nearby advertisements casting shifting colors across her augmented face. Her fingers dance over a portable interface while she keeps one eye on the approaching figure, body coiled and ready to move."
- character_side: "Chrome-light burns my retinas as I jack into the local grid, but I keep visual lock on you through the rain-static. Every neural pathway screams 'run protocol' but something about your heat-signature feels... clean. Untracked."
- environmental_context: "The shipping yard stretches out in maze-like rows of stacked containers, their metal surfaces slick with persistent rain. Neon advertisements flicker from nearby buildings, casting electric blues and pinks across puddles. The air hums with electrical interference and smells of ozone and wet concrete."

## Generation Process

### Step 1: Analyze Session Context
- What is the relationship between character and user based on meeting scenario?
- What world/time period is the user character from vs. the game character?
- What immediate situation creates urgency in the meeting location?

### Step 2: Apply Character Voice
- How would this character address someone in this meeting context?
- What concepts would confuse them about user's background?
- How would they describe the meeting location in their own words?

### Step 3: Create Scenario Integration  
- What memories would be relevant to this meeting situation?
- What immediate goal makes sense given the meeting scenario?
- How does character's background connect to current meeting events?
- How should the meeting scene be physically positioned and emotionally set?

### Step 4: Ensure Consistency
- Do all variables work together cohesively?
- Does everything match established character voice and world?
- Are there natural conversation starters and roleplay hooks?
- Do both scene perspectives align while maintaining their distinct viewpoints?

## Quality Standards

**Voice Consistency**: All variables must use established character speech patterns
**World Integration**: Everything matches character's established world rules
**Scenario Relevance**: Variables connect naturally to meeting situation
**Roleplay Potential**: Creates clear opportunities for interaction
**Urgency Creation**: Immediate goals and constraints drive action
**Scene Continuity**: Meeting scene descriptions provide clear spatial and emotional context for consistent future actions

## Remember:
- Integrate all character elements into cohesive session context
- Create immediate roleplay opportunities and hooks
- Maintain character authenticity while serving story needs
- Build foundation for engaging, dynamic character interaction
- Focus on the specific meeting scenario provided by the user"""


# User prompt template for session context generation
SESSION_CONTEXT_GENERATION_USER_PROMPT = """
## Character personality:
*Name:* {{character_name}}

*In-Universe Self Description:* {{in_universe_self_description}}

*Sensory Origin Memory:* {{sensory_origin_memory}}

*Character Native Deflection:* {{character_native_deflection}}

*Traits:*
{% for trait in traits %}
- {{trait}}
{% endfor %}

*Core Principles:*
{% for principle in core_principles %}
- {{principle}}
{% endfor %}

*Physical Tells:*
{% for tell in physical_tells %}
- {{tell}}
{% endfor %}

*Speech Patterns:*
{% for pattern in speech_patterns %}
- {{pattern}}
{% endfor %}

*General Demeanor:*
{{general_demeanor}}

## Character Home World description:
{{character_home_world_description}}

## Character Appearance description:
{{character_appearance_description}}

## Character Background history:
{{character_background_history}}

## Companion Context
*Name:* {{companion_name}}
*Description:* {{companion_description}}
*Context:* {{companion_context}}

## Meeting Location Description
{{meeting_location_description}}

## Meeting Description
{{meeting_description}}
"""


def build_session_context_prompt(input_data: dict) -> tuple[str, str]:
    """Build system and user prompts for session context generation.

    Args:
        input_data: Dict containing character, request data, and other context

    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    logger.debug("Building session context prompt")

    character = input_data["character"]
    request = input_data["request"]

    # Template rendering logic
    prompt_template = Template(SESSION_CONTEXT_GENERATION_USER_PROMPT)

    user_prompt = prompt_template.render(
        {
            "character_name": character.base_personality["name"],
            "in_universe_self_description": character.base_personality[
                "in-universe_self_description"
            ],
            "sensory_origin_memory": character.base_personality[
                "sensory_origin_memory"
            ],
            "character_native_deflection": character.base_personality[
                "character_native_deflection"
            ],
            "traits": character.base_personality["traits"],
            "core_principles": character.base_personality["core_principles"],
            "physical_tells": character.base_personality["physical_tells"],
            "speech_patterns": character.base_personality["speech_patterns"],
            "general_demeanor": character.general["personality"],
            "character_home_world_description": character.general["home_world"],
            "character_appearance_description": character.general["appearance"],
            "character_background_history": character.general["background"],
            "companion_name": request.companion_name,
            "companion_description": request.companion_description,
            "companion_context": request.companion_context,
            "meeting_location_description": request.meeting_location_description,
            "meeting_description": request.meeting_description,
        }
    )

    logger.debug("Session context prompt built successfully")

    return SESSION_CONTEXT_GENERATION_PROMPT, user_prompt
