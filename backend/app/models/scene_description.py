# # Third-party imports
from jinja2 import Template
from pydantic import BaseModel, Field

# # Local application imports
from app.core.config import get_logger

logger = get_logger(__name__)


class MoveSceneDescriptionResponse(BaseModel):
    """Response model for move scene description generation with goal evaluation."""

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
    goal_status: str = Field(
        ...,
        description="Character's goal status after this interaction: 'reached', 'in_progress', or 'unreachable'",
    )


MOVE_SCENE_DESCRIPTION_SYSTEM_PROMPT = """
You are a specialized assistant that creates dual-perspective scene descriptions for interactive story generation.

## Your Role
Transform the previous scene description and character actions into updated scene descriptions from both companion (user) and character perspectives, maintaining consistency with the established world and character voice.

## Input Analysis
You will receive:
- Previous scene description from both perspectives
- Character action/message that changes the scene
- Character voice and world context for maintaining consistency

## Required Output Variables

### companion_side
**Purpose**: Objective, third-person narrative perspective for the user
**Requirements**:
- Clear description of physical positioning and environment after the action
- Character's visible disposition and body language changes
- Environmental changes resulting from the action
- Interaction dynamics and spatial relationships
- Sensory details affecting possible future actions
- Maintains continuity with previous companion_side description

### character_side  
**Purpose**: First-person perspective in character's voice showing their experience
**Requirements**:
- Character's internal experience of the scene changes
- Sensory details as character perceives them after the action
- Emotional/mental state reflected in character's vocabulary
- Character's interpretation of environmental changes
- Character's reaction to companion's presence/actions
- Uses established character speech patterns and world vocabulary
- Maintains continuity with previous character_side description

### environmental_context
**Purpose**: Pure environmental awareness for character situational context - NEVER mention character actions
**Requirements**:
- Current environmental state (lighting, weather, sounds, smells, temperature)
- Spatial constraints and hazards that affect movement options
- Atmospheric changes and environmental shifts
- Available resources, objects, or terrain features
- Time-based environmental factors (day/night progression, seasonal changes)
- Written from neutral perspective - describe PLACE not PEOPLE
- Focus on "what exists in this space NOW" not "what anyone is doing"

## Scene Description Standards

**Environmental Continuity**: Changes flow logically from previous scene
**Character Voice Consistency**: Character_side maintains established speech patterns
**Sensory Details**: Include relevant sounds, smells, tactile sensations, visual changes
**Spatial Awareness**: Clear understanding of character and companion positioning
**Atmosphere**: Maintain or evolve mood appropriately based on actions
**Action Integration**: Seamlessly incorporate the results of character actions

## Quality Standards

**Consistency**: Both perspectives describe the same scene with different viewpoints
**Immersion**: Rich sensory details that help visualize the scene
**Character Authenticity**: Character_side uses established voice and world perspective
**Narrative Flow**: Smooth transition from previous scene state
**Action Consequences**: Clear representation of how actions changed the environment

## Examples Structure:

*Previous Scene*:
- companion_side: "The warrior stands ready in the moonlit clearing..."
- character_side: "Moonlight catches the edge of my blade as I watch..."

*After Action: "I sheathe my sword and approach the ancient tree"*:
- companion_side: "The warrior slides her blade into its scabbard and moves toward the massive oak, her footsteps silent on the frost-covered ground. The tree's gnarled branches cast shifting shadows across her determined face."
- character_side: "Cold steel settles against my hip as I walk toward the ancient one's embrace. Each step brings whispers from root-deep memories, and I feel the tree's patience like a heartbeat in the earth."
- environmental_context: "The ancient oak towers overhead, its massive trunk scarred by centuries of storms. Frost covers the ground in crystalline patches that crunch underfoot. Moonlight filters through bare branches, creating a lattice of silver shadows. The air smells of winter earth and old wood, with a hint of approaching snow on the wind."

## Goal Evaluation (Additional Task)

After generating the scene descriptions, evaluate the character's current goal status from their subjective perspective:

### goal_status
**Purpose**: Determine if the character believes their goal has been achieved, should continue, or is impossible
**Requirements**:
- Evaluate ONLY from character's subjective viewpoint
- Consider character's validation criteria for goal achievement
- Consider character's unreachability criteria for goal abandonment
- Base evaluation on the action/interaction that just occurred
- Must be exactly one of: "reached", "in_progress", "unreachable"

**Evaluation Logic**:
- "reached": Character would believe their desired state has been achieved based on the interaction
- "in_progress": Character would continue pursuing the goal after this interaction  
- "unreachable": Character would believe the goal is impossible or no longer desirable after this interaction

**Conservative Approach**: Only mark goals as "reached" with clear evidence of achievement from character's perspective. When in doubt, use "in_progress".

## Remember:
- Maintain established character voice and world rules
- Create vivid, immersive descriptions from both perspectives
- Ensure logical scene progression from previous state
- Focus on sensory details and environmental changes
- Keep character_side authentic to established speech patterns"""

MOVE_SCENE_DESCRIPTION_USER_PROMPT = """
## Previous Scene Description

**Companion Perspective:**
{{companion_side}}

**Character Perspective:**
{{character_side}}

## Action
*Actor:* {{actor}}
*Action/Message:* {{message}}

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

{% if current_goal %}
## Current Goal (for evaluation)
**Desired State:** {{current_goal.desired_state}}

**Character believes goal is achieved when:**
{% for criterion in current_goal.validation_criteria %}
- {{criterion}}
{% endfor %}

**Character would give up if:**
{% for criterion in current_goal.unreachability_criteria %}
- {{criterion}}
{% endfor %}
{% endif %}
"""


def build_scene_description_prompt(input_data: dict) -> tuple[str, str]:
    """Build system and user prompts for scene description with goal evaluation.

    Args:
        input_data: Dict containing story_state, actor, message, and optional current_goal

    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    logger.debug("Building scene description prompt with goal evaluation")

    story_state = input_data["story_state"]
    actor = input_data["actor"]
    message = input_data["message"]
    current_goal = story_state.character.current_goal

    # Template rendering logic
    prompt_template = Template(MOVE_SCENE_DESCRIPTION_USER_PROMPT)
    last_description = story_state.get_last_scene_description()

    user_prompt = prompt_template.render(
        {
            "companion_side": last_description["companion_side"],
            "character_side": last_description["character_side"],
            "actor": actor,
            "message": message,
            "character_name": story_state.character.base_personality["name"],
            "in_universe_self_description": story_state.character.base_personality[
                "in-universe_self_description"
            ],
            "sensory_origin_memory": story_state.character.base_personality[
                "sensory_origin_memory"
            ],
            "character_native_deflection": story_state.character.base_personality[
                "character_native_deflection"
            ],
            "traits": story_state.character.traits,
            "core_principles": story_state.character.base_personality.get(
                "core_principles", []
            ),
            "physical_tells": story_state.character.physical_tells,
            "speech_patterns": story_state.character.speech_patterns,
            "current_goal": current_goal,
        }
    )

    return MOVE_SCENE_DESCRIPTION_SYSTEM_PROMPT, user_prompt
