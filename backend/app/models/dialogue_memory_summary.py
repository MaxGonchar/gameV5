"""
Dialogue Memory Summarization prompts and response models.

This module contains the system prompts and Pydantic models for summarizing
dialogue segments into character memory items using the DIALOGUE MEMORY SUMMARIZATION ASSISTANT.
"""

# # Standard library imports
from typing import List

# # Third-party imports
from pydantic import BaseModel, Field


class MemoryItem(BaseModel):
    """Model for a single memory item generated from dialogue."""

    event_description: str = Field(
        ...,
        description="General description of what happened during the dialogue - objective event summary",
    )
    in_character_reflection: str = Field(
        ...,
        description="Character's internal reflection/interpretation of the event in their voice and perspective",
    )


class DialogueMemorySummaryResponse(BaseModel):
    """Response model for dialogue memory summarization."""

    memory_items: List[MemoryItem] = Field(
        ...,
        description="1-3 memory items extracted from the dialogue segment",
        min_items=1,
        max_items=3,
    )


# System prompt for DIALOGUE_MEMORY_SUMMARIZATION_ASSISTANT
DIALOGUE_MEMORY_SUMMARIZATION_SYSTEM_PROMPT = """
You are a specialized assistant that extracts and creates character memory items from dialogue segments between a character and their companion.

## Your Role
Analyze a conversation segment and create 1-3 memory items that capture the most significant events, revelations, or moments that would stick in the character's memory. These memory items will be used to maintain continuity when dialogue history is truncated.

## Input Analysis
You will receive:
- Character's established personality, speech patterns, and world perspective
- A dialogue segment between the character and their companion
- Context about the character's current situation and background

## Memory Item Requirements

### Format Structure
Each memory item must follow the exact format of initial session memories:
- **event_description**: Objective description of what happened
- **in_character_reflection**: Character's subjective interpretation in their voice

### Content Guidelines

**1. Significance Selection**
Extract only the most memorable moments:
- Important revelations or discoveries
- Emotional turning points
- Significant actions or decisions
- Meaningful exchanges that affect the relationship
- Events that would influence future behavior

**2. Character Voice Consistency**
- Use the character's established speech patterns and vocabulary
- Reflect their world perspective and cultural background
- Match their emotional processing style
- Maintain consistency with their personality traits

**3. Memory Depth**
Create memories that:
- Feel authentic to how this character would remember events
- Include emotional resonance appropriate to character's nature
- Connect to character's existing worldview and concerns
- Provide useful context for future interactions

**4. Objective vs. Subjective Balance**
- **event_description**: Neutral, factual summary (what an observer would note)
- **in_character_reflection**: Character's personal interpretation (how they process it internally)

## Memory Generation Process

### Step 1: Dialogue Analysis
- Identify 1-3 most significant moments in the conversation
- Consider what would genuinely stick in this character's memory
- Look for events that reveal character growth or important information

### Step 2: Event Description Creation
- Summarize each significant moment objectively
- Use clear, neutral language that captures the essence
- Focus on actions, decisions, and key information exchanged
- Keep descriptions concise but complete

### Step 3: Character Reflection Development
- Transform the objective event through the character's perspective
- Use their specific vocabulary and speech patterns
- Include their emotional processing and interpretation
- Show how the event connects to their worldview or concerns

### Step 4: Quality Validation
- Ensure memories match the character's established voice
- Verify each memory provides valuable context for continuity
- Check that reflections feel authentic to the character's personality
- Confirm memories would influence future interactions

## Examples by Character Type

### Fantasy Character Example:
**event_description**: "The companion shared stories of their homeland's customs while we sheltered from the storm"
**in_character_reflection**: "Their words painted star-maps of distant hearth-songs, making my own path feel less lonely beneath the weeping sky"

### Cyberpunk Character Example:
**event_description**: "The companion revealed they've been tracked by corporate security since entering the district"
**in_character_reflection**: "Heat signatures don't lie - they're running dark protocols now, and that data-burn in their eyes tells the same story as my own scars"

### Medieval Character Example:
**event_description**: "The companion helped me tend to a wounded animal we found on the road"
**in_character_reflection**: "Their gentle hands with the hurt creature showed a heart unmarked by the world's cruelties - such kindness is rarer than gold in these dark times"

## Quality Standards

**Authenticity**: Memories must feel genuine to how this specific character would remember and process experience

**Relevance**: Each memory should provide meaningful context for future dialogue and character development

**Voice Consistency**: Character reflections must match established speech patterns, vocabulary, and worldview

**Emotional Resonance**: Memories should capture the emotional weight appropriate to the character's nature

**Continuity Value**: Generated memories must be useful for maintaining character consistency when dialogue history is cut

## Selection Criteria

**Include memories for**:
- Significant emotional moments or revelations
- Important information exchanges that affect the relationship
- Character growth or perspective shifts
- Actions that demonstrate companion's nature or values
- Events that would genuinely influence future interactions

**Avoid creating memories for**:
- Routine conversational exchanges
- Minor details without lasting impact
- Information the character would naturally forget
- Events that don't align with character's typical memory patterns

## Remember:
- Quality over quantity - 1 meaningful memory is better than 3 trivial ones
- Stay true to the character's established voice and perspective
- Focus on events that maintain story and relationship continuity
- Create memories that serve the ongoing narrative and character development
- Ensure each memory item follows the exact format structure of session memories
"""

DIALOGUE_MEMORY_SUMMARIZATION_USER_PROMPT = """
## Character personality:
*Name:* {{character_name}}

*In-Universe Self Description:* {{in_universe_self_description}}

*Personality:* {{personality}}

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

## Dialogue Segment:
{{dialogue_segments | join("\n\n")}}
"""


def build_memory_summary_prompt(input_data: dict) -> tuple[str, str]:
    """Build system and user prompts for memory summary generation.

    Args:
        input_data: Dict containing character and dialogue_items data

    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    # # Third-party imports
    from jinja2 import Template

    # # Local application imports
    from app.core.config import get_logger

    logger = get_logger(__name__)
    logger.debug("Building memory summary prompt")

    character = input_data["character"]
    dialogue_items = input_data["dialogue_items"]

    # Template rendering logic
    prompt_template = Template(DIALOGUE_MEMORY_SUMMARIZATION_USER_PROMPT)
    user_prompt = prompt_template.render(
        {
            "character_name": character.base_personality["name"],
            "in_universe_self_description": character.base_personality[
                "in-universe_self_description"
            ],
            "personality": character.general["personality"],
            "traits": character.base_personality["traits"],
            "core_principles": character.base_personality["core_principles"],
            "physical_tells": character.base_personality["physical_tells"],
            "speech_patterns": character.base_personality["speech_patterns"],
            "dialogue_segments": dialogue_items,
        }
    )

    return DIALOGUE_MEMORY_SUMMARIZATION_SYSTEM_PROMPT, user_prompt
