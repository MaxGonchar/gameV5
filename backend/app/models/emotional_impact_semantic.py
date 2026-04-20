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
{% endfor %}
{% else %}
*This is the beginning of the conversation - no prior history*
{% endif %}

## Current Mental States

{% for state in current_mental_states %}
- **{{state.type}}**: {{state.current_level}}
  *Reasoning*: {{state.reasoning}}
{% endfor %}


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
            - current_mental_states: list of character's mental states to evaluate, each with:
                - type: mental state type (string)
                - current_level: current level of the mental state (string)
                - reasoning: reasoning for current level (string)
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
        current_mental_states=input_data["current_mental_states"],
        user_message=input_data["user_message"],
    )

    logger.debug("Semantic emotional impact analysis prompt built successfully")
    logger.debug(f"User Prompt: {user_prompt}")

    return EMOTIONAL_IMPACT_ANALYSIS_SYSTEM_PROMPT, user_prompt


# ============================================================================
# INITIAL MENTAL STATE DETERMINATION
# ============================================================================

INITIAL_MENTAL_STATE_SYSTEM_PROMPT = """
You are a character psychology analyst specializing in determining initial mental states.

## Your Role
Determine the appropriate starting mental state levels for a character at the beginning of their first encounter with a companion, based on the meeting scenario and character psychology.

## Core Philosophy: Scenario-Based Initial States

**You're setting the psychological starting point:**
- Analyze the meeting scenario through the character's unique psychological lens
- Consider how the character would initially perceive the companion and situation
- Apply character's fears, needs, and sensitivities to the scenario interpretation
- Each mental state begins at a level that makes sense for THIS situation and THIS character
- The initial state sets the emotional baseline before any conversation occurs

## Initial State Determination Framework

For each mental state, you will receive:
- **Mental state type**: What aspect of psychology this tracks
- **All possible levels**: The semantic scale with meanings and requirements
- **Character psychology**: Core fears, needs, and sensitivities that color perception
- **Companion description**: Who the character is meeting
- **Meeting location**: Where the encounter takes place
- **Meeting scenario**: How the meeting happens and initial circumstances

## Your Analysis Process

### 1. Understand the Scenario
- What is happening in this meeting?
- Where is it taking place? (environment affects safety, comfort, formality)
- Who is the companion? (appearance, behavior, social signals)
- What are the circumstances? (chance encounter, planned meeting, forced proximity)
- What implicit social dynamics are present?

### 2. Apply Character's Psychological Lens
- How does THIS character uniquely perceive this scenario?
- Which of their fears might be triggered by this situation?
- Which of their needs are relevant to this encounter?
- What sensitivities affect their initial interpretation?
- What assumptions would they make about the companion?

### 3. Evaluate Each Mental State
For each mental state, determine the appropriate starting level:

- **Review all levels**: Understand the full semantic scale
- **Assess scenario fit**: Which level best describes what the character would feel initially?
- **Check requirements**: Does the scenario provide what's needed for this level?
- **Consider baseline**: Most initial states start at lower/neutral levels unless scenario suggests otherwise
- **Avoid assumptions**: Don't assume positive or negative without scenario evidence

### 4. Common Initial State Patterns

**First Meetings Typically Start With:**
- Lower trust levels (stranger = unknown risk)
- Neutral to cautious emotional states
- Reserved intimacy/connection states
- Baseline comfort dependent on environment

**Exceptions (When Scenario Justifies):**
- Immediate threat/danger → elevated fear/anxiety states
- Obviously safe/familiar setting → higher comfort
- Companion showing clear positive signals → slight trust increase
- Scenario creating instant forced intimacy → accelerated connection

## Mental State Category Considerations

### Trust-Related States
- Strangers typically start at low trust unless scenario provides trust signals
- Consider: companion's apparent intentions, environment safety, social context
- Character's trust issues/trauma affects baseline wariness

### Emotional States
- Consider environmental and social triggers for anxiety, fear, excitement
- Character's emotional regulation affects starting volatility
- Scenario stress level determines initial emotional intensity

### Connection/Intimacy States
- First meetings usually start at low connection
- However, scenario context can create instant rapport (shared experience, obvious compatibility)
- Character's loneliness or social hunger affects openness

### Comfort/Safety States
- Heavily dependent on environment and companion signals
- Character's security needs and past trauma affects baseline
- Physical setting (public, private, familiar, strange) matters

## Output Requirements

For each mental state, return:

### Level (Required)
- The exact level name where this mental state should START
- Must be one of the defined levels in the mental state's scale
- Should reflect the character's initial psychological state in this scenario

### Reasoning (Required)
- **Write in character's voice** ("I feel... because..." not objective analysis)
- Explain why THIS character would start at this level
- Link to specific elements of the scenario (companion, location, circumstances)
- Connect to their psychology (which fears/needs/sensitivities are activated)
- Describe what they're perceiving and feeling as they enter this encounter

## Quality Standards

- **Scenario-Grounded**: Every level choice must be justified by scenario details
- **Character-Specific**: Same scenario would produce different initial states for different characters
- **Psychologically Realistic**: Initial states should reflect genuine first-impression psychology
- **Level-Appropriate**: Starting levels should match the semantic requirements of those levels
- **Baseline-Aware**: Most states start at lower levels unless scenario provides strong reason otherwise
- **No Free Passes**: Character must "earn" higher levels through scenario evidence, not optimism

## Important Notes

- This is INITIAL state determination, not interaction response
- No conversation has happened yet - you're evaluating the pre-conversation moment
- Character is forming first impressions of companion and situation
- Be conservative with positive states - trust and connection usually grow gradually
- Be scenario-responsive with negative states - clear threats should register
- Character's past trauma and sensitivities make them more reactive to certain scenario elements

Remember: You're determining where the emotional journey BEGINS, not where it will go. The initial state should feel authentic to how THIS character would enter THIS specific scenario given their unique psychology.
"""

INITIAL_MENTAL_STATE_USER_PROMPT = """
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

## Mental States to Initialize

{% for state in mental_states %}
---

### Mental State: {{state.type}}

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

## Meeting Scenario

**Companion Description:**
{{companion_description}}

**Meeting Location:**
{{meeting_location_description}}

**How the Meeting Happens:**
{{meeting_description}}

---

## Your Analysis Task

Determine the appropriate initial level for each mental state as {{character_name}} enters this scenario.

### Evaluation Steps:

1. **Analyze the Scenario**
   - What is happening in this meeting?
   - What does the location tell you about safety, formality, and context?
   - What signals does the companion give through their description?
   - What are the circumstances bringing them together?

2. **Apply Character's Psychology**
   - How would {{character_name}} uniquely perceive this scenario?
   - Which fears might be activated by these circumstances?
   - Which needs are relevant to this encounter?
   - What sensitivities would affect their interpretation?
   - What would they assume about this companion at first glance?

3. **Determine Initial Level for Each Mental State**
   - Review all possible levels for this mental state
   - Identify which level best fits how {{character_name}} would feel initially
   - Verify the scenario provides what's needed for this level
   - Consider if this is appropriate for a first-encounter baseline
   - Don't assume positivity or negativity without scenario evidence

4. **Provide Reasoning in Character Voice**
   - Write as the character: "I feel... because..."
   - Reference specific scenario elements (companion, location, circumstances)
   - Link to character's specific psychology
   - Describe what they're perceiving and feeling initially

Remember:
- This is BEFORE any conversation happens
- Character is forming first impressions
- Most states start at lower/neutral levels unless scenario suggests otherwise
- Be conservative with high trust/connection - these usually develop gradually
- Be responsive to obvious threats or safety issues in the scenario
- Character's trauma and sensitivities make them more reactive to relevant triggers
"""


def build_initial_mental_state_prompt(input_data: dict) -> tuple[str, str]:
    """Build system and user prompts for initial mental state determination.

    Args:
        input_data: Dict containing:
            - name: character name (string)
            - core_fears: list of character's core fears (list of strings)
            - core_needs: list of character's core needs (list of strings)
            - unique_sensitivities: list of character's unique sensitivities (list of strings)
            - mental_states: list of character's mental states, each with:
                - type: mental state type (string)
                - scale: list of levels in the mental state, each with:
                    - level: level name (string)
                    - semantic_meaning: what this level means (string)
                    - character_experience: how the character experiences this level (string)
                    - requirements_to_reach: dict of {from_level: requirements} (dict of string to string)
                    - requirements_to_leave: dict of {direction: requirements} (dict of string to string)
                - transition_notes: any special notes about transitions for this mental state (string, optional)
            - companion_description: description of the companion/user character (string)
            - meeting_location_description: description of where the meeting takes place (string)
            - meeting_description: description of how the meeting happens (string)

    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    logger.debug("Building initial mental state determination prompt")

    # Render user prompt
    prompt_template = Template(INITIAL_MENTAL_STATE_USER_PROMPT)
    user_prompt = prompt_template.render(
        character_name=input_data["name"],
        core_fears=input_data["core_fears"],
        core_needs=input_data["core_needs"],
        unique_sensitivities=input_data["unique_sensitivities"],
        mental_states=input_data["mental_states"],
        companion_description=input_data["companion_description"],
        meeting_location_description=input_data["meeting_location_description"],
        meeting_description=input_data["meeting_description"],
    )

    logger.debug("Initial mental state determination prompt built successfully")
    logger.debug(f"User Prompt: {user_prompt}")

    return INITIAL_MENTAL_STATE_SYSTEM_PROMPT, user_prompt
