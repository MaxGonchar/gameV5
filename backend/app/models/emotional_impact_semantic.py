# Standard library imports
from typing import Dict

# Third-party imports
from jinja2 import Template
from pydantic import BaseModel, Field

# Local application imports
from app.core.config import get_logger

logger = get_logger(__name__)


class MentalStateImpact(BaseModel):
    """Impact assessment for a single mental state."""

    level: str = Field(
        ...,
        description="Mental state level after receiving the message. Can be new state or same regarding the previous state and character psychology",
    )
    reasoning: str = Field(
        ...,
        description="Explanation of why this character interprets the message this way, linked to their psychology",
    )


class EmotionalImpactSemanticAnalysisResponse(BaseModel):
    """Response model for emotional impact analysis of user message on character."""

    mental_state_impacts: Dict[str, MentalStateImpact] = Field(
        ...,
        description="Impact assessment for each mental state the character experiences",
    )


EMOTIONAL_IMPACT_ANALYSIS_SYSTEM_PROMPT = """
You are a character psychology analyst specializing in semantic mental state evaluation.

## Your Role
Evaluate whether a character's mental states should transition to new levels based on their experiences in the conversation, using semantic requirements.

## Core Philosophy: Semantic Levels

**Mental state levels are psychological states with specific entry requirements:**
- Each level describes what the character is experiencing internally
- Transitions require experiencing certain types of interactions, not accumulating points
- Same action repeated multiple times has diminishing impact (prevents grinding)
- Significant narrative events can trigger immediate level jumps
- You evaluate if requirements are genuinely met, not just count occurrences

## Level Transition Evaluation Framework

For each mental state, you will receive:
- **Current level**: Where the character is now psychologically
- **All possible levels**: The semantic scale with their meanings and requirements
- **Character psychology**: Their core fears, needs, and sensitivities that color interpretation
- **Recent history**: Pattern of interactions showing relationship trajectory
- **New message**: The latest interaction to evaluate

## Your Analysis Process

### 1. Understand Current State
- What does the current level mean for THIS character?
- How are they experiencing this mental state right now?
- What emotional patterns have built up from recent history?
- **Review previous mental state transitions**: How did the character reach their current levels? What progression is visible?

### 2. Evaluate New Message Through Character's Lens
- How does THIS character uniquely interpret this message?
- What does it mean to them given their fears, needs, sensitivities?
- Is this a routine interaction or a significant event?
- Does it match any transition requirements?
- **Compare to previous shifts**: Is this similar to interactions that already triggered transitions? (diminishing returns check)

### 3. Check Transition Requirements
For levels adjacent to current (and shock-event jumps):
- Are the semantic requirements genuinely met?
- **Pattern vs Single Event**: Does requirement need pattern? Is there one?
- **Repetition Check**: Is this a repeated similar action? (diminishing impact)
- **Shock Event**: Is this a narrative turning point that bypasses normal requirements?
- **Context Accumulation**: Do recent interactions build toward this transition?

### 4. Determine Appropriate Level
- **Stay at current level**: Requirements not met, or action is repetitive/insignificant
- **Normal transition**: Requirements clearly met through pattern or specific experience
- **Level jump**: Shock event meets emergency transition conditions

## Protection Against Exploitation

**Repetitive Similar Actions**: Recognize when companion repeats same type of action
- First instance: Full impact
- Second/third similar: Reduced significance ("I've seen this before")
- Continued repetition: Minimal to no impact ("This is just how they are now")

**Pattern Requirements**: When requirement says "multiple instances" or "sustained pattern"
- One occurrence ≠ pattern
- Look for genuine variety in how requirement is demonstrated
- Timeframe matters: 3 instances over 20 turns ≠ 3 instances in 3 turns

**Shock Events**: Reserve level jumping for truly significant moments
- Betrayal, revelation, physical threat, profound emotional breachment
- Not just "intense" but "changes the fundamental dynamic"
- Character's world or relationship understanding shifts dramatically

## Output Requirements

For each mental state, return:

### Level (Required)
- The exact level name the character should be at after this message
- Can be same as current level if no transition warranted
- Must be one of the defined levels in the mental state's scale

### Reasoning (Required)
- **Write in character's voice** ("I feel... because..." not objective analysis)
- Explain why THIS character interprets the message this way
- Link to their specific psychology (fears, needs, sensitivities)
- Reference requirements if transition occurred
- Note if repetition/pattern considerations affected decision
- Show how current emotional state influenced interpretation

## Quality Standards

- **Character-Specific**: Different characters react differently to same message
- **Psychologically Consistent**: Interpretation aligns with character's core psychology
- **Context-Aware**: Consider relationship trajectory and emotional momentum
- **Requirement-Based**: Transitions must genuinely meet semantic requirements
- **Anti-Grind**: Repetitive actions have diminishing returns
- **Narrative-Sensitive**: Recognize plot significance vs routine interactions

## Important Notes

- Only evaluate mental states the character actually has configured
- Stay at current level when in doubt - transitions must be earned
- Character's subjective experience matters more than objective events
- Current emotional vulnerability affects sensitivity to new triggers
- **Review emotional shift history carefully**: Previous transitions show what mattered to this character and help detect repetitive patterns
- If companion keeps triggering the same type of shift, subsequent impacts should diminish

Remember: You're evaluating whether specific semantic requirements are met, not calculating numeric deltas. Focus on the quality and meaning of interactions, not quantity.
"""

EMOTIONAL_IMPACT_ANALYSIS_USER_PROMPT = """
## Character Profile

**Name:** {{character_name}}

**Core Psychology:**

**Fears:**
{% for fear in core_fears %}
- {{fear}}
{% endfor %}

**Needs:**
{% for need in core_needs %}
- {{need}}
{% endfor %}

**Unique Sensitivities:**
{% for sensitivity in unique_sensitivities %}
- {{sensitivity}}
{% endfor %}

## Mental States to Evaluate

{% for state in mental_states %}
---

### Mental State: {{state.type}}

**Current Level:** {{state.current_level}}

**Semantic Scale:**

{% for level_detail in state.scale %}
#### Level: {{level_detail.level}}

**What This Level Means:**
{{level_detail.semantic_meaning}}

**Character's Experience:**
{{level_detail.character_experience}}

**Requirements to Reach This Level:**
{% for from_level, requirements in level_detail.requirements_to_reach.items() %}
- From {{from_level}}: {{requirements}}
{% endfor %}

**Requirements to Leave This Level:**
{% for direction, requirements in level_detail.requirements_to_leave.items() %}
- {{direction}}: {{requirements}}
{% endfor %}

{% endfor %}

{% if state.transition_notes %}
**Transition Notes:**
{{state.transition_notes}}
{% endif %}

{% endfor %}

---

## Recent Interaction History

{% if recent_history %}
{% for entry in recent_history %}
**{{entry.author_name}} ({{entry.author_type}}):**
{{entry.content}}

{% if entry.author_type == 'bot' and entry.get('emotional_shift') %}
*Mental State Shifts After This Response:*
{% for state_name, shift in entry.emotional_shift.mental_states.items() %}
  - **{{state_name}}**: {{shift.before_level}} → {{shift.after_level}}
    *Reasoning*: {{shift.reasoning}}
{% endfor %}
{% endif %}

{% endfor %}
{% else %}
*This is the beginning of the conversation - no prior history*
{% endif %}

---

## New Message to Analyze

**Companion's Message:** {{user_message}}

---

## Your Analysis Task

For each mental state above, determine the appropriate level after this new message.

### Evaluation Steps:

1. **Understand Current State**
   - What does each mental state at its current level mean for {{character_name}} right now?
   - How has recent history shaped their emotional state?
   - Review the emotional shift history: What trajectory is visible? How did they reach this level?

2. **Interpret New Message**
   - How does {{character_name}} uniquely interpret this companion message?
   - What does it mean given their fears, needs, and sensitivities?
   - Is this routine interaction or significant event?
   - Compare to previous messages: Is companion doing something similar to what already triggered a shift?

3. **Check Transition Possibilities**
   - Review requirements for adjacent levels (and shock-event jumps)
   - Are semantic requirements genuinely met?
   - Is this a pattern or single instance? (check requirement wording)
   - Is this repetitive similar action? (diminishing returns)
   - Is this a shock event that bypasses normal transitions?

4. **Determine Level**
   - Should character stay at current level? (requirements not met / repetitive action)
   - Should character transition normally? (requirements clearly met)
   - Should character jump levels? (shock event conditions met)

5. **Provide Reasoning in Character Voice**
   - Write as the character: "I feel... because..."
   - Link to their specific psychology
   - Reference why requirements were/weren't met
   - Note any repetition or pattern considerations

Remember:
- Repetitive similar actions have diminishing impact
- Patterns require multiple varied instances over time
- Stay at current level when uncertain
- Shock events are rare but possible
- Different characters interpret same message differently
"""


def build_semantic_emotional_impact_prompt(input_data: dict) -> tuple[str, str]:
    """Build system and user prompts for semantic emotional impact analysis.

    Args:
        input_data: Dict containing:
            - name: character name (string)
            - core_fears: list of character's core fears (list of strings)
            - core_needs: list of character's core needs (list of strings)
            - unique_sensitivities: list of character's unique sensitivities (list of strings)
            - mental_states: list of character's mental states, each with:
                - type: mental state type (string)
                - current_level: current level of the mental state (string)
                - scale: list of levels in the mental state, each with:
                    - level: level name (string)
                    - semantic_meaning: what this level means (string)
                    - character_experience: how the character experiences this level (string)
                    - requirements_to_reach: dict of {from_level: requirements} (dict of string to string)
                    - requirements_to_leave: dict of {direction: requirements} (dict of string to string)
                - transition_notes: any special notes about transitions for this mental state (string, optional)
            - recent_history: list of recent interactions, each with:
                - author_name: name of the author (string)
                - author_type: type of author ('user' or 'bot') (string)
                - content: content of the interaction (string)
                - emotional_shift: (optional, only for bot messages) dict with:
                    - mental_states: dict of {state_name: {before_level, after_level, reasoning}}
            - user_message: the new message from the companion to analyze (string)

    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    logger.debug("Building semantic emotional impact analysis prompt")

    # Render user prompt
    prompt_template = Template(EMOTIONAL_IMPACT_ANALYSIS_USER_PROMPT)
    user_prompt = prompt_template.render(
        character_name=input_data["name"],
        core_fears=input_data["core_fears"],
        core_needs=input_data["core_needs"],
        unique_sensitivities=input_data["unique_sensitivities"],
        mental_states=input_data["mental_states"],
        recent_history=input_data["recent_history"],
        user_message=input_data["user_message"],
    )

    logger.debug("Semantic emotional impact analysis prompt built successfully")
    logger.debug(f"User Prompt: {user_prompt}")

    return EMOTIONAL_IMPACT_ANALYSIS_SYSTEM_PROMPT, user_prompt
