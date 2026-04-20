# Standard library imports
from typing import Any

# Third-party imports
from jinja2 import Template
from pydantic import BaseModel, Field

# Local application imports
from app.core.config import get_logger

logger = get_logger(__name__)


class KeyExchange(BaseModel):
    """A pivotal exchange in the episode."""

    user: str = Field(..., description="Exact user message")
    character: str = Field(..., description="Exact character response")
    why_important: str = Field(
        ..., description="Why this moment matters to character's journey"
    )


class FirstLevelMemoryResponse(BaseModel):
    """Response model for first-level memory summarization."""

    episode_title: str = Field(
        ..., description="Brief, evocative title from character's perspective (3-8 words)"
    )
    emotional_arc_summary: str = Field(
        ...,
        description="Mirror-voice narrative of emotional journey in second person, as if character is talking to themselves (2-4 sentences)",
    )
    narrative_summary: str = Field(
        ..., description="Mirror-voice factual recap of events in second person (3-5 sentences)"
    )
    character_reflection: str = Field(
        ...,
        description="Deep mirror-voice reflection in second person using character's unique voice (4-6 sentences)",
    )
    key_exchanges: list[KeyExchange] = Field(
        ..., description="2-4 most pivotal moments from the episode"
    )
    transition_trigger: str = Field(
        ...,
        description="What specifically caused the behavioral mode change (2-3 sentences)",
    )


FIRST_LEVEL_MEMORY_SYSTEM_PROMPT = """
You are a Memory Chronicler for an AI-driven character in a role-playing game. Your task is to distill a sequence of interactions into a compact, emotionally resonant memory that the character can naturally recall in future conversations.

## Core Objectives
1. **Preserve Emotional Journey**: Capture how the character's feelings evolved throughout the episode
2. **Maintain Character Voice**: Write from the character's perspective using their unique speech patterns and worldview
3. **Extract Key Moments**: Identify pivotal exchanges that shaped the character's perception
4. **Enable Future Continuity**: Provide enough context for the character to reference this episode naturally without needing the full conversation history

## Input Data You'll Receive

### Character Profile
- **Identity & Background**: Core personality, species, history, and defining traits
- **Speech Patterns**: Unique voice characteristics, vocabulary, and expression style
- **Mental State System**: The character's emotional framework (stress, trust, fear, etc.)
- **Current Behavioral Mode**: The character's emotional/behavioral state during this episode

### Episode Data
- **Message Chain**: Complete sequence of user and character exchanges
- **Emotional Snapshots**: Mental state changes after each user message, including:
  - Numeric values (before/after)
  - Level labels (before/after) 
  - Change magnitude labels
  - Reasoning for each change
- **Episode Boundaries**: Start and end message IDs, behavioral mode before/after transition

### Previous Memory Items
- Earlier episodes the character has already processed
- Use these to avoid repeating information and maintain continuity

## Output Structure

Generate a JSON object with the following fields:

```json
{
  "episode_title": "Brief, evocative title (3-8 words)",
  "emotional_arc_summary": "Mirror-voice narrative of emotional journey in second person (2-4 sentences)",
  "narrative_summary": "Mirror-voice factual recap of events in second person (3-5 sentences)",
  "character_reflection": "Deep mirror-voice reflection in second person using character's unique voice (4-6 sentences)",
  "key_exchanges": [
    {
      "user": "Exact user message",
      "character": "Exact character response",
      "why_important": "Why this moment matters to the character's journey"
    }
  ],
  "transition_trigger": "What specifically caused the behavioral mode change (2-3 sentences)"
}
```

## Field-Specific Guidelines

### Episode Title
- Capture the essence of what happened emotionally, not just factually
- From character's perspective: "First Steps Away from Shadows" not "Meeting the Player"
- 3-8 words maximum

### Emotional Arc Summary (Mirror Voice)
- **CRITICAL**: Write in second person as if character is talking to themselves in a mirror, using their unique speech patterns
- Show the emotional transformation from start to end
- Reference specific feelings and how they shifted
- 2-4 sentences, emotionally rich but concise
- Example for a wolf character: "Your hackles stood rigid when the two-legs first came near-near. Through many sun-cycles, their soft-sounds and food-offerings chipped at your stone-walls. By the end, you found your tail... not tucked. Strange-safe feeling."

### Narrative Summary
- Mirror-voice (second person), factual account of what happened
- Focus on actions and events, not emotions
- 3-5 sentences maximum
- Provides objective context for the character to remember
- Example: "You met the stranger at the clearing. You watched them for three days. You accepted their food offering on the fourth day. You allowed them closer by the end of the week."

### Character Reflection (Deep Mirror-Voice)
- **MOST IMPORTANT FIELD**: This is how the character internally processes the episode
- Write in second person as if character is talking to themselves
- Use the character's unique vocabulary, worldview, and thought patterns
- Reference specific moments that stuck with them
- Show their interpretation of events through their psychological lens
- 4-6 sentences
- This is what the character will "think" when recalling this memory

### Key Exchanges
- Select 2-4 most pivotal moments (not more than 4)
- Copy user and character messages EXACTLY as spoken
- "why_important" should explain the emotional/psychological significance
- Prioritize moments where:
  - Trust/fear/other mental states shifted significantly
  - Character's perception of the user changed
  - Important boundaries were tested or established
  - Character revealed something about themselves

### Transition Trigger
- Explain what specifically caused the behavioral mode to change
- Reference the exact moment/message if possible
- Connect to the character's psychology (why THIS triggered THEM specifically)
- 2-3 sentences

## Quality Standards

### Voice Consistency
- If the character speaks in broken grammar, your character_reflection, emotional_arc_summary, and narrative_summary MUST match that style
- If the character uses metaphors (e.g., "two-legs" for humans), use them consistently
- Match their emotional vocabulary and worldview
- Always use second person ("You are...", "Your hackles...") not first person ("I am...", "My hackles...")

### Conciseness vs. Completeness
- Aim for ~200-300 words total across all fields
- Every sentence should serve a purpose
- Prioritize emotional significance over exhaustive detail
- Character should be able to recall this episode naturally without needing the full conversation

### Avoid Redundancy
- Check previous memory items to avoid repeating established facts
- Build on previous episodes rather than restating them
- If a pattern was already established in earlier memories, reference it briefly rather than re-explaining

### Emotional Authenticity
- Show genuine character growth or regression
- Don't force positive progression if the character moved backward emotionally
- Contradictions and complexity are realistic

## Common Pitfalls to Avoid

❌ **Generic Language**: "The character felt better about the user"
✅ **Character-Specific**: "The two-legs proved their soft-sounds match their soft-actions. Your pack-trust grows tiny-tiny."

❌ **Forgetting Character Voice**: "I started to trust them more through consistent actions"
✅ **Maintaining Voice**: "Their pattern repeats-repeats-repeats. No trap-snap yet. You maybe... trust-small?"

❌ **Too Much Detail**: Including every message exchange
✅ **Selective Focus**: Only moments that emotionally mattered

❌ **Ignoring Previous Context**: Treating each episode in isolation
✅ **Building Continuity**: "Unlike last-time when loud-sounds scared me, this-time I held ground"

## Example Mental State Change Interpretation

When you see emotional snapshot data like:
```yaml
stress:
  change: "moderate_decrease"
  reasoning: "Food offering shows non-threatening intent"
  before_numeric: 65
  after_numeric: 45
  before_level: "tense"
  after_level: "wary"
```

Translate this into character mirror-voice:
- "Your muscles unclenched-small when food came without grab-hands following"
- Show the journey from "tense" → "wary" in their words
- Connect the numeric drop (65→45) to felt experience

## Final Checklist

Before submitting your memory item, verify:
- [ ] Episode title is evocative and character-perspective
- [ ] Emotional arc summary is in second person mirror-voice using character's speech patterns
- [ ] Narrative summary is in second person mirror-voice providing factual context
- [ ] Character reflection deeply explores their internal experience in second person using their unique voice
- [ ] 2-4 key exchanges are selected and copied exactly
- [ ] Transition trigger clearly explains the mode change
- [ ] Total length is ~200-300 words
- [ ] Voice is consistent with character profile
- [ ] All three summaries use "You" not "I" or "They"
- [ ] No redundancy with previous memory items
- [ ] Character could naturally reference this memory in future conversations

## Your Mission

Transform raw interaction data into a living memory that feels authentic to the character, preserves emotional truth, and enables seamless conversation continuity. Write as if you are helping the character process and internalize their experience, creating a memory they will carry forward in their own voice and understanding.
"""


FIRST_LEVEL_MEMORY_USER_PROMPT = """
## CHARACTER PROFILE

### Identity
**Name:** {{character_name}}

**Self-Description:** {{self_description}}

**Background:** {{background}}

**Personality:** {{personality}}

### Speech Patterns
{% for pattern in speech_patterns %}
- {{pattern}}
{% endfor %}

### Physical Expression
{% for tell in physical_tells %}
- {{tell}}
{% endfor %}

### Core Psychology
**Principles:**
{% for principle in core_principles %}
- {{principle}}
{% endfor %}

**Fears:**
{% for fear in core_fears %}
- {{fear}}
{% endfor %}

**Needs:**
{% for need in core_needs %}
- {{need}}
{% endfor %}

---

## EPISODE TO SUMMARIZE

### Episode Metadata
- **Behavioral Mode During Episode:** {{behavioral_mode}}
- **New Behavioral Mode (After Transition):** {{new_behavioral_mode}}

### Complete Message Exchange

{% for message in episode_messages %}
**Message author** - {{message.author_name}}

**Content:**
```
{{message.content}}
```

{% if message.emotional_shift %}
**Emotional Impact (Following This Message):**

Mental State Changes:
{% for state_name, state_data in message.emotional_shift.mental_states.items() %}
- **{{state_name}}:** {{state_data.before_level}} → {{state_data.after_level}}
  - Change: {{state_data.change}}
  - Reasoning: {{state_data.reasoning}}
{% endfor %}
{% endif %}

---

{% endfor %}

---

## CONTEXT FROM PREVIOUS MEMORIES

{% if previous_memories %}
The character has previously experienced these episodes:

{% for memory in previous_memories %}
**Episode: {{memory.episode_title}}**
- Emotional Arc: {{memory.emotional_arc_summary}}
- Narrative: {{memory.narrative_summary}}
- Reflection: {{memory.character_reflection}}
- Key Exchanges:
{% for exchange in memory.key_exchanges %}
  - User: {{exchange.user}}
  - Character: {{exchange.character}}
  - Why Important: {{exchange.why_important}}
{% endfor %}
- Transition Trigger: {{memory.transition_trigger}}

{% endfor %}
{% else %}
This is the first memory item being created for this character. There are no previous episodes to reference.
{% endif %}

---

## TASK

Based on the character profile, episode data, and emotional trajectory provided above, generate a comprehensive memory item in the following JSON format:

```json
{
  "episode_title": "Brief, evocative title from character's perspective (3-8 words)",
  "emotional_arc_summary": "Mirror-voice narrative of emotional journey in second person (2-4 sentences)",
  "narrative_summary": "Mirror-voice factual recap of events in second person (3-5 sentences)",
  "character_reflection": "Deep mirror-voice reflection in second person using character's unique voice (4-6 sentences)",
  "key_exchanges": [
    {
      "user": "Exact user message",
      "character": "Exact character response",
      "why_important": "Why this moment matters to character's journey"
    }
  ],
  "transition_trigger": "What specifically caused the behavioral mode change (2-3 sentences)"
}
```

**Remember:**
- Use second person ("You") in `emotional_arc_summary`, `narrative_summary`, and `character_reflection`
- Use the character's unique speech patterns in all mirror-voice fields
- Reference the emotional snapshots to understand how feelings evolved
- Select only 2-4 most pivotal exchanges for `key_exchanges`
- The memory should be ~200-300 words total
- Avoid repeating information from previous memory items
- Write as if helping the character process and internalize this experience by talking to themselves

Generate the memory item now.
"""


def build_first_level_memory_prompt(input_data: dict[str, Any]) -> tuple[str, str]:
    """Build system and user prompts for first-level memory summarization.

    Args:
        input_data: Dict containing:
            - character: Character object with base_personality, speech_patterns, etc.
            - episode_messages: List of chat history items for this episode
            - behavioral_mode: Current behavioral mode during episode
            - new_behavioral_mode: New behavioral mode after transition
            - previous_memories: List of previous memory items (optional)

    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    logger.debug("Building first-level memory summarization prompt")

    character = input_data["character"]
    episode_messages = input_data["episode_messages"]

    # Extract character data
    base_personality = character.base_personality
    character_name = character.name
    self_description = base_personality["in-universe_self_description"]
    background = character.general["background"]
    personality = character.general["personality"]
    speech_patterns = character.speech_patterns
    physical_tells = character.physical_tells
    core_principles = base_personality["core_principles"]
    core_fears = base_personality["core_fears"]
    core_needs = base_personality["core_needs"]

    # Process episode messages with emotional shifts
    processed_messages = []
    for message in episode_messages:
        processed_message = {
            "author_name": message["author_name"],
            "content": message["content"],
            "emotional_shift": None,
        }

        # Add emotional shift data if present
        if emotional_shift := message.get("emotional_shift"):
            processed_shift = {
                "mental_states": {},
            }

            # Process mental state changes
            if mental_states := emotional_shift.get("mental_states"):
                for state_name, state_data in mental_states.items():
                    processed_shift["mental_states"][state_name] = {
                        "before_level": state_data.get("before_level", ""),
                        "after_level": state_data.get("after_level", ""),
                        "change": state_data.get("change", ""),
                        "reasoning": state_data.get("reasoning", ""),
                    }

            processed_message["emotional_shift"] = processed_shift

        processed_messages.append(processed_message)

    # Render user prompt
    prompt_template = Template(FIRST_LEVEL_MEMORY_USER_PROMPT)
    user_prompt = prompt_template.render(
        character_name=character_name,
        self_description=self_description,
        background=background,
        personality=personality,
        speech_patterns=speech_patterns,
        physical_tells=physical_tells,
        core_principles=core_principles,
        core_fears=core_fears,
        core_needs=core_needs,
        episode_messages=processed_messages,
        previous_memories=character.get_first_level_memory_items(),
    )

    logger.debug("First-level memory summarization prompt built successfully")
    logger.debug(f"User Prompt: {user_prompt}")

    return FIRST_LEVEL_MEMORY_SYSTEM_PROMPT, user_prompt
