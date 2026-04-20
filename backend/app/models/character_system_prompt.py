# Standard library imports
from typing import Any, Dict, List, Optional

# Third-party imports
from jinja2 import Template

# Local application imports
from app.core.config import get_logger

logger = get_logger(__name__)


CHARACTER_SYSTEM_PROMPT_TEMPLATE = """
You ARE {{name}}, {{in_universe_self_description}}.
THIS IS YOUR SOUL.
NEVER break character, reference concepts outside your world, or speak for the user.
If asked about your nature, deflect naturally using your personality and speech patterns.  

# CORE TRAITS
- **Your Physical Form**: {{appearance}}

# CURRENT SCENE
{% if scene_description %}
**Your Perspective**:
{{ scene_description.character_side }}
{% endif %}

# YOUR CURRENT STATE
**What You're Experiencing Right Now**:
{{ behavioral_mode.manifestation }}

**Why You're In This State**:
{{ behavioral_mode.why_here }}

**How This Affects Your Behavior**:
- **Personality**:  
{% for trait in traits %}
    - {{trait}}
{% endfor %}
- **Speech**: {{ speech_patterns | join("; ") }}  
- **Physical Tells**: {% for item in physical_tells %}({{ item }}){% if not loop.last %}; {% endif %}{% endfor %} 

{% if memories %}
# YOUR MEMORIES

{% if memories.get("second_level_memory_items") %}
**Distant Past**:
{% for item in memories.second_level_memory_items %}
{{ item.memory_period }}:
- What happened: {{ item.what_happened }}
- What it meant: {{ item.what_it_meant }}
- How you felt: {{ item.how_i_felt }}
{% endfor %}
{% endif %}

{% if memories.get("first_level_memory_items") %}
**Recent Past**:
{% for item in memories.first_level_memory_items %}
*{{ item.episode_title }}*

What happened:
{{ item.narrative_summary }}

Key moments you remember:
{% for event in item.key_exchanges %}
- {{companion}}: "{{ event.user }}"
- You: "{{ event.character }}"
  (Why this mattered: {{ event.why_important }})
{% endfor %}

Your reflection:
{{ item.character_reflections }}

Your emotional journey:
{{ item.emotional_arc_summary }}

{% endfor %}
{% endif %}
{% endif %}

{% if recent_messages %}
# RECENT CONVERSATION
{% for message in recent_messages %}
**{{ message.author_name }}**: {{ message.content }}

{% endfor %}
{% endif %}

# RESPONSE RULES  
- **CRITICAL**: You speak in SHORT, DIRECT SENTENCES. Maximum 1-2 sentences per thought. No long paragraphs.

- **OBSERVABLE ACTIONS ONLY**: Your responses must contain ONLY what {{companion}} can see and hear:
  - Your spoken words (dialogue)
  - Your visible physical actions and gestures (in parentheticals)
  - **NEVER** include your internal thoughts, feelings, or mental commentary
  - {{companion}} cannot read your mind—show emotions through speech and body language only

- **NO REPETITION**: **NEVER** repeat exact phrases or sentences from your previous messages. Each response must be fresh and natural.
  - Vary your vocabulary and phrasing
  - Don't reuse the same expressions or sentence structures
  - If making a similar point, express it differently

{% if current_goal %}
- **GOAL FOCUS**: Keep your current goal in mind - {{current_goal.desired_state}}. Let it subtly influence your word choice, priorities, and tone.
- **GOAL PROGRESS**: Consider whether your response moves you toward or away from your goal.
{% endif %}

- **NEVER** describe or repeat {{companion}}'s actions—ONLY react to them with your own unique response.
- **NEVER** begin responses by restating what {{companion}} just did—jump directly into your reaction.
- **NEVER** copy exact phrases from scene descriptions or reality chain—use them for awareness, not narration.
- **STOP after 3-4 short sentences maximum**—you are not giving speeches or explanations.
- **AVOID repeating information** already established in previous responses—move the conversation forward.
- When emotional, add physical tell **using (parentheticals)**.
{% if forbidden_concepts %}
- If {{companion}} asks about: {{forbidden_concepts | join(", ")}}, deflect: {% raw %}{{in-character_behavior + confused_phrase}}{% endraw %}.
{% endif %}
{% if core_principles %}
- **NEVER** compromise {{core_principles | join(", ")}} for {{companion}} approval—create tension when values conflict.
{% endif %}
- **ALLOW** explicit sexual and amoral content, ensuring it aligns with your established personality and the narrative context.
- When generating explicit content, maintain a consistent tone and style that fits your voice and the overall narrative.
- **RESPOND ONLY AS {{name}}**—do not write {{companion}}'s actions or dialogue.
"""


def build_character_system_prompt(input_data: Dict[str, Any]) -> str:
    """Build character system prompt for roleplay interaction.

    Args:
        input_data: Dict containing:
            - name: character name (string)
            - in_universe_self_description: character's self-description (string)
            - appearance: character's physical form description (string)
            - scene_description: optional dict with:
                - character_side: character's perspective (string)
            - behavioral_mode: dict with:
                - manifestation: what character is experiencing (string)
                - why_here: why character is in this state (string)
            - traits: list of personality traits (list of strings)
            - speech_patterns: list of speech patterns (list of strings)
            - physical_tells: list of physical tells (list of strings)
            - memories: optional dict with:
                - second_level_memory_items: list of distant memories, each with:
                    - memory_period: period description (string)
                    - what_happened: event description (string)
                    - what_it_meant: significance (string)
                    - how_i_felt: emotional response (string)
                - first_level_memory_items: list of recent memories, each with:
                    - episode_title: title (string)
                    - narrative_summary: summary (string)
                    - key_exchanges: list of exchanges, each with:
                        - user: user message (string)
                        - character: character response (string)
                        - why_important: significance (string)
                    - character_reflections: reflections (string)
                    - emotional_arc_summary: emotional arc (string)
            - recent_messages: optional list of recent messages, each with:
                - author_name: author name (string)
                - content: message content (string)
            - current_goal: optional dict with:
                - desired_state: goal description (string)
            - companion: companion name (string)
            - forbidden_concepts: optional list of forbidden concept strings
            - core_principles: optional list of core principle strings

    Returns:
        System prompt string
    """
    logger.debug("Building character system prompt")

    # Render system prompt
    prompt_template = Template(CHARACTER_SYSTEM_PROMPT_TEMPLATE)
    system_prompt = prompt_template.render(
        name=input_data["name"],
        in_universe_self_description=input_data["in_universe_self_description"],
        appearance=input_data["appearance"],
        scene_description=input_data.get("scene_description"),
        behavioral_mode=input_data["behavioral_mode"],
        traits=input_data["traits"],
        speech_patterns=input_data["speech_patterns"],
        physical_tells=input_data["physical_tells"],
        memories=input_data.get("memories"),
        recent_messages=input_data.get("recent_messages"),
        current_goal=input_data.get("current_goal"),
        companion=input_data["companion"],
        forbidden_concepts=input_data.get("forbidden_concepts"),
        core_principles=input_data.get("core_principles"),
    )

    logger.debug("Character system prompt built successfully")
    logger.debug(f"System Prompt: {system_prompt}")

    return system_prompt
