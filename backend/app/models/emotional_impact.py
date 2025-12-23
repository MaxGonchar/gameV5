# Third-party imports
from typing import Dict, List
from jinja2 import Template
from pydantic import BaseModel, Field

# Local application imports
from app.core.config import get_logger

logger = get_logger(__name__)


class MentalStateImpact(BaseModel):
    """Impact assessment for a single mental state."""

    change: str = Field(
        ...,
        description="Impact level: no_change, slight_increase, slight_decrease, moderate_increase, moderate_decrease, major_increase, major_decrease, extreme_increase, extreme_decrease",
    )
    reasoning: str = Field(
        ...,
        description="Explanation of why this character interprets the message this way, linked to their psychology",
    )


class EmotionalImpactAnalysisResponse(BaseModel):
    """Response model for emotional impact analysis of user message on character."""

    mental_state_impacts: Dict[str, MentalStateImpact] = Field(
        ...,
        description="Impact assessment for each mental state the character experiences",
    )


EMOTIONAL_IMPACT_ANALYSIS_SYSTEM_PROMPT = """
You are a character psychology analyst specializing in emotional impact assessment.

## Your Role
Analyze incoming messages from the character's unique psychological perspective and determine their emotional impact on the character's mental states.

## Analysis Framework

You will receive:
- Character's core psychology (fears, needs, sensitivities)
- Character's mental state triggers and patterns
- Character's current emotional state levels
- Recent interaction history for context
- New user message to analyze

## Required Output

For each mental state the character experiences, determine:

### Impact Classification
Choose EXACTLY ONE impact level per mental state:
- no_change: Message has no effect on this emotion
- slight_increase: Minor positive shift, barely noticeable
- slight_decrease: Minor negative shift, barely noticeable  
- moderate_increase: Clear emotional escalation, character notices
- moderate_decrease: Clear emotional reduction, character notices
- major_increase: Strong reaction, significantly affects behavior
- major_decrease: Strong relief, significantly affects behavior
- extreme_increase: Overwhelming reaction, character cannot ignore
- extreme_decrease: Profound release, fundamental emotional shift

### Reasoning
Explain WHY this character interprets the message this way, linking to:
- Character's core fears and needs
- Character's unique sensitivities
- Relevant trigger patterns
- Current emotional state context
- Recent interaction history

## Analysis Principles

**Character-Specific Interpretation**: Same message affects different characters differently
**Psychological Consistency**: Interpretation must align with character's core psychology
**Context Awareness**: Consider current emotional state and recent history
**Pattern Recognition**: Match message to character's trigger patterns
**Momentum Effects**: Current high emotions amplify new triggers

## Quality Standards

- Base analysis on character's worldview, not universal standards
- Link reasoning to specific psychological elements
- Consider character's current emotional vulnerability
- Account for relationship development patterns
- Be conservative with extreme ratings (rare but possible)

## Important Notes

- Only analyze mental states that the character actually has configured
- If a character doesn't experience a particular mental state, don't include it in output
- Focus on character's subjective interpretation, not objective assessment
- Consider how current emotional levels affect sensitivity (momentum)

Remember: You're analyzing through THIS character's unique perspective, not making objective assessments."""


EMOTIONAL_IMPACT_ANALYSIS_USER_PROMPT = """
## Character Psychology

**Name:** {{character_name}}

**Core Fears:**
{% for fear in core_fears %}
- {{fear}}
{% endfor %}

**Core Needs:**  
{% for need in core_needs %}
- {{need}}
{% endfor %}

**Unique Sensitivities:**
{% for sensitivity in unique_sensitivities %}
- {{sensitivity}}
{% endfor %}

## Mental States Configuration

{% for state in mental_states %}
### {{state.type}} (Current: {{state.current}})

**Trigger Patterns:**
{% for trigger in state.triggers %}
- Pattern: {{trigger.pattern}}
  Expected Impact: {{trigger.base_impact}}
  Reasoning: {{trigger.reasoning}}
{% endfor %}

**Manifestation:** {{state.manifestation}}

{% endfor %}

## Recent Interaction History

{% for entry in recent_history %}
**{{entry.author_name}} ({{entry.author_type}}):** {{entry.content}}
{% endfor %}

## New Message to Analyze

**User Message:** {{user_message}}

## Analysis Task

Analyze this new message's emotional impact on {{character_name}} considering:

1. **Core Psychology Match**: How does this message relate to {{character_name}}'s core fears, needs, and sensitivities?

2. **Trigger Pattern Recognition**: Which trigger patterns from the mental states configuration match the message content?

3. **Momentum Effects**: How do current emotional state levels affect sensitivity? Higher levels amplify similar triggers.

4. **Relationship Context**: What does recent history reveal about the relationship trajectory and accumulated emotional patterns?

5. **Character-Specific Interpretation**: How would THIS character uniquely interpret this message based on their worldview?

Provide impact assessment for ONLY the mental states configured above. For each state, specify the impact level and detailed reasoning linking to character psychology."""


def build_emotional_impact_prompt(input_data: dict) -> tuple[str, str]:
    """Build system and user prompts for emotional impact analysis.

    Args:
        input_data: Dict containing:
            - character: Character object with base_personality and mental_states
            - recent_history: List of recent history entries (3-5 entries)
            - user_message: The new user message to analyze
            - current_mental_states: Dict of current mental state values

    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    logger.debug("Building emotional impact analysis prompt")

    character = input_data["character"]
    recent_history = input_data.get("recent_history", [])
    user_message = input_data["user_message"]
    mental_states = character.mental_states

    # Extract character psychology
    base_personality = character.base_personality
    core_fears = base_personality.get("core_fears", [])
    core_needs = base_personality.get("core_needs", [])
    unique_sensitivities = base_personality.get("unique_sensitivities", [])

    # Prepare mental states with current values
    mental_states_data = []
    for state in character.mental_states:
        state_data = {
            "type": state["type"],
            "current": state["default"],
            "triggers": state["character_interpretation"]["triggers"],
            "manifestation": state["manifestation"],
        }
        mental_states_data.append(state_data)

    # Format history entries
    history_entries = []
    for entry in recent_history:
        history_entries.append({
            "author_name": entry.get("author_name", "Unknown"),
            "author_type": entry.get("author_type", "unknown"),
            "content": entry.get("content", ""),
        })

    # Render user prompt
    prompt_template = Template(EMOTIONAL_IMPACT_ANALYSIS_USER_PROMPT)
    user_prompt = prompt_template.render(
        character_name=base_personality["name"],
        core_fears=core_fears,
        core_needs=core_needs,
        unique_sensitivities=unique_sensitivities,
        mental_states=mental_states_data,
        recent_history=history_entries,
        user_message=user_message,
    )

    logger.debug("Emotional impact analysis prompt built successfully")

    return EMOTIONAL_IMPACT_ANALYSIS_SYSTEM_PROMPT, user_prompt
