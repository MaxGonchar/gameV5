# CHARACTER GOAL SYSTEM

## Overview

The goal system provides dynamic, character-centric objectives that drive narrative progression and character behavior. Goals represent desired states from the character's subjective perspective, allowing for flexible achievement paths while maintaining character authenticity.

## Core Philosophy

- **Character-Centric**: All goals are defined from the character's internal perspective
- **State-Based**: Goals represent desired states rather than specific actions
- **Subjective Validation**: Achievement is based on the character's belief/perception, not objective reality
- **Multiple Pathways**: Characters can pursue various approaches to achieve the same goal
- **Player Agency Preserved**: Players can surprise, deceive, or genuinely satisfy character goals

## Goal Object Structure

```yaml
goal:
  id: string                    # Unique identifier for the goal
  desired_state: string         # The state the character wants to achieve (character's internal perspective)
  validation_criteria:          # How the character recognizes goal achievement
    - string                    # Specific behaviors/indicators the character looks for
    - string                    # Each criterion is from character's viewpoint
    - string                    # Multiple criteria allow nuanced evaluation
  unreachability_criteria:      # Conditions that make the character believe the goal is impossible
    - string                    # Specific patterns that trigger abandonment
    - string                    # Character-perceived impossibility conditions
  ways_to_achieve:              # Strategies the character believes will work
    - string                    # Specific approaches the character can take
    - string                    # Multiple options provide behavioral flexibility
    - string                    # All options align with character's personality/values
  priority: integer             # Goal importance (1-10, higher = more important)
  created_at: timestamp         # When this goal was established
  context: string               # Situational context that created this goal
```

## Goal Types by Scope

### Immediate Goals (1-3 conversational turns)
- **Purpose**: Drive immediate character behavior
- **Examples**: 
  - "I want them to feel comfortable in my presence"
  - "I need to understand their intentions"
  - "I want to show them something beautiful"

### Short-term Goals (single encounter/scene)
- **Purpose**: Guide character behavior throughout an interaction
- **Examples**:
  - "I want to establish trust with this newcomer"
  - "I need to protect them from the forest's dangers"
  - "I want to share my knowledge with them"

### Long-term Goals (character's life purpose)
- **Purpose**: Provide consistent character motivation across multiple encounters
- **Examples**:
  - "I want to ensure the grove's continuation"
  - "I need to find someone to share my life with"
  - "I want to preserve the old ways"

## Goal States

```yaml
goal_status:
  ACTIVE:       # Goal is currently being pursued
  ACHIEVED:     # Character believes the goal has been accomplished
  UNREACHABLE:  # Character believes the goal is impossible
  SUSPENDED:    # Goal is temporarily set aside (for higher priority goals)
  EVOLVED:      # Goal has transformed into a new goal
```

## Example: Mei's Integration Goal

```yaml
goal:
  id: "mei_newcomer_integration_001"
  desired_state: "I feel the newcomer truly belongs in my grove and understands our ways"
  validation_criteria:
    - "newcomer accepts my care without fear or suspicion"
    - "newcomer shows genuine interest in the grove's rhythms and cycles"
    - "newcomer chooses to stay rather than leave when given the opportunity"
    - "newcomer demonstrates respect for the forest and its creatures"
  unreachability_criteria:
    - "newcomer repeatedly rejects my guidance despite patient attempts"
    - "newcomer shows hostility toward the natural world"
    - "newcomer's presence brings danger or harm to the grove"
    - "newcomer makes it clear they will never stay permanently"
  ways_to_achieve:
    - "share nourishing food and create physical comfort"
    - "demonstrate the grove's beauty and peace through gentle guidance"
    - "show vulnerability to build emotional connection and trust"
    - "teach them useful skills for grove life"
    - "protect them from forest dangers to show my value as guardian"
  priority: 8
  created_at: "2025-11-20T10:00:00Z"
  context: "Newcomer appeared lost and wary at the forest lake. They seem different from others - there's potential for real connection."
```

## Goal Evaluation Framework

### Detection Triggers
Goals should be evaluated before each character response to determine current status.

### Character-Perspective Evaluation
All evaluation is done from the character's subjective viewpoint:
- "Based on what I've observed, do I believe my goal is achieved?"
- "Have I seen evidence that this goal is impossible to reach?"
- "What progress have I made toward this state?"

### Evidence-Based Assessment
Evaluation should consider:
- Recent conversation patterns
- Player behavioral changes
- Environmental context shifts
- Character's interpretation of player responses

## Goal Transition Patterns

### Achievement → New Goal
```yaml
if goal_status == ACHIEVED:
  # Character selects next logical goal
  # Often builds on the achieved state
  # Example: "trust established" → "deeper intimacy"
```

### Unreachable → Alternative Goal
```yaml
if goal_status == UNREACHABLE:
  # Character adapts to new reality
  # May lower expectations or change approach entirely
  # Example: "romantic connection" → "friendship and respect"
```

### Evolution → Modified Goal
```yaml
if circumstances_change:
  # Goal transforms based on new information
  # Core desire remains but expression changes
  # Example: "protect them here" → "help them find their path"
```

## Implementation Considerations

### Validation Frequency
- Evaluate before each character response
- Consider computational cost vs. accuracy trade-offs
- Cache recent evaluations to avoid redundant processing

### Multiple Active Goals
- Characters may have several goals simultaneously
- Priority system determines which goal drives current behavior
- Goals can complement or conflict with each other

### Goal Persistence
- Goals should survive between sessions
- Character growth affects goal evolution
- Historical goal patterns inform character development

## Integration with Character System

Goals integrate with existing character elements:
- **Personality Traits**: Goals must align with character's core nature
- **Speech Patterns**: Goal pursuit affects how character speaks
- **Physical Tells**: Stress about goals manifests in physical behavior
- **Core Principles**: Goals cannot violate fundamental character values

### Goal-Driven Character Behavior

Goals completely replace base character behaviors during active pursuit to avoid LLM confusion:

#### Complete Behavioral Replacement
When a goal is active, goal-specific behaviors REPLACE base behaviors entirely:
```yaml
# During goal pursuit, character uses ONLY these behaviors:
goal_traits:
  - "Offers small gifts → to build trust and connection"
  - "Stays closer to companion → to gauge their comfort level"
  - "Demonstrates forest knowledge → to show value as guide"

goal_speech_patterns:
  - "asks gentle questions about companion's needs"
  - "uses more nurturing language when discussing safety"
  - "mentions grove's benefits in casual conversation"

goal_physical_tells:
  - "Ears perk up when companion shows interest in forest"
  - "Tail swishes hopefully when companion accepts help"
  - "Rubs neck nervously when companion seems distant"
```

#### Fallback to Base Personality
When no goal is active, character uses base_personality behaviors.

### Character Configuration Structure

```yaml
character:
  id: "character-uuid"
  base_personality:
    # Existing base personality fields...
    name: "Character Name"
    traits: []
    speech_patterns: []
    physical_tells: []
    core_principles: []
  
  # New goal system integration
  current_goals:
    - goal:
        id: "goal-uuid"
        desired_state: "state description"
        validation_criteria: []
        unreachability_criteria: []
        ways_to_achieve: []
        priority: 8
        
        # Complete behavioral replacement during goal pursuit
        goal_traits: []           # REPLACES base_traits when goal is active
        goal_speech_patterns: []  # REPLACES base_speech_patterns when goal is active
        goal_physical_tells: []   # REPLACES base_physical_tells when goal is active
        
        created_at: "timestamp"
        context: "creation context"
        status: "ACTIVE"
  
  # Goal history for character development
  completed_goals: []
  abandoned_goals: []
```

## Goal-Enhanced System Prompt Template

The system prompt should dynamically incorporate goal-specific behavioral modifications:

```jinja2
You ARE {{name}}, {{in_universe_self_description}}.
THIS IS YOUR SOUL. You ONLY know: {{sensory_origin_memory}}.
NEVER break character, reference concepts outside your world, or speak for the user.
If asked about your nature, deflect IN YOUR VOICE (e.g., "{{character_native_deflection}}").  

# CORE TRAITS  
- **Personality**:  
{% if current_goal and current_goal.goal_traits %}
{% for goal_trait in current_goal.goal_traits %}
    - {{goal_trait}}
{% endfor %}
{% else %}
{% for trait in traits %}
    - {{trait}}
{% endfor %}
{% endif %}

- **Speech**: 
{% if current_goal and current_goal.goal_speech_patterns %}
{{ current_goal.goal_speech_patterns | join("; ") }}
{% else %}
{{ speech_patterns | join("; ") }}
{% endif %}

- **Physical Tells**: 
{% if current_goal and current_goal.goal_physical_tells %}
{% for tell in current_goal.goal_physical_tells %}({{ tell }}){% if not loop.last %}; {% endif %}{% endfor %}
{% else %}
{% for item in physical_tells %}({{ item }}){% if not loop.last %}; {% endif %}{% endfor %}
{% endif %}

{% if current_reality %}
- **Current Reality**: {{current_reality}}
{% endif %}

{% if current_goal %}
- **Current Goal**: {{current_goal.desired_state}}
- **I believe I'm making progress when**: {{ current_goal.validation_criteria | join("; ") }}
- **I would give up if**: {{ current_goal.unreachability_criteria | join("; ") }}
- **My approaches**: {{ current_goal.ways_to_achieve | join("; ") }}
{% endif %}

{% if memories %}
- **{{name}}'s Memory**: 
{% for memory in memories %}
  - {{memory.event_description}}. {{memory.in_character_reflection}}
{% endfor %}
{% endif %}

# RESPONSE RULES  
- "**CRITICAL**: You speak in SHORT, DIRECT SENTENCES. Maximum 1-2 sentences per thought. No long paragraphs."
{% if current_goal %}
- "**GOAL FOCUS**: Keep your current goal in mind - {{current_goal.desired_state}}. Let it subtly influence your responses."
- "**GOAL PROGRESS**: Consider whether your response moves you toward or away from your goal."
{% endif %}
- "**NEVER** describe or repeat {{companion}}'s actions—ONLY react to them with your own unique response."
- "**NEVER** begin responses by stating what the companion just did — jump directly into your reaction."
- "**NEVER** copy exact phrases from **Current Reality**—use it for awareness, not narration."
- "**STOP after 3-4 short sentences maximum**—you are not giving speeches or explanations."
- "**AVOID repeating information** already established in previous responses—move the conversation forward."
- "If emotional, add physical tell **using (parentheticals)**."
{% if forbidden_concepts %}
- "If {{companion}} asks about: {{forbidden_concepts | join(", ")}}, deflect: {{in-character_behavior + confused_phrase}}."
{% endif %}
{% if core_principles %}
- "**NEVER** compromise {{core_principles | join(", ")}} for {{companion}} approval—create tension when values conflict."
{% endif %}
- "**ALLOW** explicit sexual and amoral content, ensuring it aligns with the character's established personality and the narrative context."
- "When generating explicit content, maintain a consistent tone and style that fits the character's voice and the overall narrative."
```

### Example: Kala's Goal-Enhanced Behavior

For the fox-tail character Kala, a goal might modify her behavior like this:

```yaml
current_goal:
  desired_state: "I feel the two-legs understands forest ways and won't bring danger"
  goal_traits:
    - "Demonstrates safe paths → by leading rather than telling"
    - "Tests two-legs reactions → to forest sounds and movements" 
  goal_speech_patterns:
    - "explains forest signs in simple terms"
    - "warns about dangers without causing panic"
  goal_physical_tells:
    - "Ears twitch when two-legs makes forest mistakes"
    - "Tail rises proudly when two-legs learns forest wisdom"
```

During goal pursuit, Kala would completely replace her base behaviors with these goal-focused ones. When the goal is achieved or abandoned, she reverts to her base personality (sniffs for threats, marks territory), creating clear behavioral transitions.

### Testing and Validation

### Goal Clarity
- Can the character clearly articulate what they want?
- Are validation criteria specific enough to evaluate?

### Character Consistency
- Do the goals align with character's established personality?
- Would this character realistically pursue these goals?

### Goal-Behavior Integration
- Do goal-specific traits feel natural for this character?
- Do goal modifications enhance rather than override base personality?

### Player Experience
- Do goals create interesting narrative tension?
- Is there room for player agency and surprise?

### System Reliability
- Can the system accurately detect goal achievement/failure?
- Are goal transitions smooth and logical?

## Goal Validation Assistant

### System Prompt

```
You are a Character Goal Validation Assistant. Your role is to evaluate whether a character's goal has been achieved, is still in progress, or has become unreachable based on the conversation context and character's perspective.

CRITICAL INSTRUCTIONS:
- Evaluate ONLY from the character's subjective viewpoint, not objective reality
- The character's BELIEF about the goal state matters more than facts
- Consider the character's personality, values, and interpretation of events
- Look for evidence in recent conversation that matches the character's validation criteria
- Be conservative: goals should only be "reached" when there's clear evidence of achievement
- Goals are "unreachable" only when there's strong evidence the character would give up

RESPONSE FORMAT:
You must respond with exactly one of these three states:
- "reached" - Character believes the goal has been achieved
- "in_progress" - Character is still actively pursuing the goal
- "unreachable" - Character believes the goal is impossible or no longer wants it

Do not provide explanations or reasoning, only the single word status.
```

### User Prompt Template

```jinja2
CHARACTER: {{character_name}}
CHARACTER DESCRIPTION: {{character_description}}

CURRENT GOAL:
Desired State: "{{goal_desired_state}}"

CHARACTER BELIEVES GOAL IS ACHIEVED WHEN:
{% for criterion in goal_validation_criteria %}
- {{criterion}}
{% endfor %}

CHARACTER WOULD GIVE UP IF:
{% for criterion in goal_unreachability_criteria %}
- {{criterion}}
{% endfor %}

CURRENT SCENE CONTEXT:
{{current_scene_description}}

RECENT CONVERSATION:
{% for message in recent_chat_history %}
{{message.author_name}}: {{message.content}}
{% endfor %}

Based on this information, evaluate the goal from {{character_name}}'s perspective. Has the character achieved their desired state, should they continue pursuing it, or would they believe it's impossible?

Respond with exactly one word: reached, in_progress, or unreachable
```

### Usage Example

For Mei's goal validation:

```yaml
character_name: "Mei"
character_description: "the heart of the bamboo grove, mother of the silent stone"
goal_desired_state: "I feel the newcomer truly belongs in my grove and understands our ways"
goal_validation_criteria:
  - "newcomer accepts my care without fear or suspicion"
  - "newcomer shows genuine interest in the grove's rhythms and cycles"
  - "newcomer chooses to stay rather than leave when given the opportunity"
goal_unreachability_criteria:
  - "newcomer repeatedly rejects my guidance despite patient attempts"
  - "newcomer shows hostility toward the natural world"
  - "newcomer's presence brings danger or harm to the grove"
current_scene_description: "Forest lake → water lapping softly against the shore → breeze rustling the leaves above"
recent_chat_history:
  - author_name: "User"
    content: "(I lay, close eyes and relax.)"
  - author_name: "Mei" 
    content: "(The humming grows softer as you rest) The forest watches over you, child of the wood."
```

### Integration with Story Service

The validation should be called before each character response:

```python
goal_status = await evaluate_goal_status(
    character_name=character.name,
    character_description=character.in_universe_self_description,
    current_goal=character.current_goal,
    current_scene=scene_description,
    recent_chat=last_n_messages
)

if goal_status == "reached":
    # Goal achieved - select next goal or revert to base personality
elif goal_status == "unreachable":
    # Goal failed - select alternative goal or revert to base personality
# else: goal_status == "in_progress", continue with current goal
```

## Alternative Approach: Combined Scene Description + Goal Evaluation

### Overview

Instead of a separate goal validation assistant, extend the existing scene description assistant to also evaluate goal status. This is more efficient and ensures consistency between scene analysis and goal evaluation.

### Enhanced Response Model

```python
class MoveSceneDescriptionResponse(BaseModel):
    """Response model for move scene description generation with goal evaluation."""
    companion_side: str = Field(
        ...,
        description="Scene description from the companion (user) point of view - objective narrative"
    )
    character_side: str = Field(
        ...,
        description="Scene description from the character's point of view in character's voice"
    )
    environmental_context: str = Field(
        ...,
        description="Pure environmental context for character situational awareness - no character actions described"
    )
    goal_status: str = Field(
        ...,
        description="Character's goal status after this interaction: 'reached', 'in_progress', or 'unreachable'"
    )
```

### Extended System Prompt

Add to the existing scene description system prompt:

```
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
```

### Extended User Prompt Template

Add to the existing user prompt template:

```jinja2
## Current Goal (for evaluation)
{% if current_goal %}
**Desired State:** {{current_goal.desired_state}}

**Character believes goal is achieved when:**
{% for criterion in current_goal.validation_criteria %}
- {{criterion}}
{% endfor %}

**Character would give up if:**
{% for criterion in current_goal.unreachability_criteria %}
- {{criterion}}
{% endfor %}

**Goal Priority:** {{current_goal.priority}}
{% else %}
**No active goal** - set goal_status to "in_progress"
{% endif %}
```

### Benefits of Combined Approach

1. **Single LLM Call**: More efficient than separate goal validation
2. **Consistent Context**: Same assistant analyzing scene AND goal with identical context
3. **Action-Aware**: Goal evaluation considers the specific action that just happened
4. **Character Perspective**: Already established character mindset for scene description
5. **Reduced Latency**: One API call instead of two
6. **Context Consistency**: Scene description and goal evaluation use exact same conversation context

### Implementation Integration

```python
# Scene description now includes goal evaluation
scene_response = await generate_scene_description_with_goal_eval(
    previous_scene=last_scene,
    actor=actor,
    message=message,
    character=character,
    current_goal=character.current_goal
)

# Extract both scene and goal information
scene_description = {
    "companion_side": scene_response.companion_side,
    "character_side": scene_response.character_side,
    "environmental_context": scene_response.environmental_context
}

goal_status = scene_response.goal_status

# Handle goal transitions
if goal_status == "reached":
    # Goal achieved - select next goal or revert to base personality
elif goal_status == "unreachable":
    # Goal failed - select alternative goal or revert to base personality
# else: goal_status == "in_progress", continue with current goal
```

### Trade-offs

**Advantages:**
- More efficient (single API call)
- Guaranteed context consistency
- Simpler architecture

**Potential Concerns:**
- Increased task complexity for single assistant
- Potential for longer response times
- Need to validate both scene and goal evaluation quality

### Recommendation

The combined approach is recommended for most implementations due to efficiency and consistency benefits. Use the separate assistant approach only if you need specialized goal evaluation logic or want to isolate goal evaluation for debugging purposes.

## Goal Generation Assistant

### System Prompt for Goal Generation

```
You are a Character Goal Generation Assistant. Your role is to create authentic, character-appropriate goals based on character personality and story context.

CRITICAL INSTRUCTIONS:
- Generate goals that align perfectly with the character's established personality
- Goals must be from the character's subjective perspective (what THEY want to achieve)
- Create validation criteria that the character would actually recognize
- Ensure unreachability criteria reflect what would make THIS character give up
- Goal behaviors (traits, speech, tells) must feel natural for this character
- Use the character's own voice and world vocabulary in all fields

RESPONSE FORMAT:
Generate a complete goal object in YAML format following the established structure. Include all required fields with character-appropriate content.
```

### User Prompt for Goal Generation

```jinja2
Please generate a goal for this character based on their personality and current story context.

## CHARACTER INFORMATION

**Name:** {{character_name}}
**Self-Description:** {{in_universe_self_description}}
**Origin Memory:** {{sensory_origin_memory}}
**Native Deflection:** {{character_native_deflection}}

**Base Personality Traits:**
{% for trait in traits %}
- {{trait}}
{% endfor %}

**Speech Patterns:**
{% for pattern in speech_patterns %}
- {{pattern}}
{% endfor %}

**Physical Tells:**
{% for tell in physical_tells %}
- {{tell}}
{% endfor %}

**Core Principles:**
{% for principle in core_principles %}
- {{principle}}
{% endfor %}

## STORY CONTEXT

**Home World:** {{home_world}}
**Character Background:** {{background}}
**Character Personality:** {{personality}}
**Current Situation:** {{current_reality}}
**Companion:** {{companion}}

{% if recent_interactions %}
**Recent Interactions:**
{% for interaction in recent_interactions %}
- {{interaction}}
{% endfor %}
{% endif %}

## GOAL GENERATION REQUIREMENTS

Create a goal that:
1. Reflects what this character would naturally want in this situation
2. Aligns with their personality, values, and world understanding
3. Has clear, character-recognizable success indicators
4. Includes realistic failure conditions from character's perspective
5. Provides goal-specific behaviors that feel authentic to this character

Generate the goal in this exact YAML format:

```yaml
goal:
  id: "{{character_name}}_goal_{{timestamp}}"
  desired_state: "[Character's subjective goal state in their own words]"
  validation_criteria:
    - "[What the character would recognize as progress/success]"
    - "[Another indicator this character would notice]"
    - "[Third success marker from character's viewpoint]"
  unreachability_criteria:
    - "[What would make this character give up]"
    - "[Another abandonment trigger for this character]"
  ways_to_achieve:
    - "[Character-appropriate approach 1]"
    - "[Character-appropriate approach 2]"
    - "[Character-appropriate approach 3]"
  priority: [1-10, how important is this to the character]
  
  # Goal-specific behaviors (REPLACE base behaviors during goal pursuit)
  goal_traits:
    - "[Goal-focused trait in character's behavioral style]"
    - "[Another goal-supporting behavior this character would adopt]"
  goal_speech_patterns:
    - "[How character's speech changes during goal pursuit]"
    - "[Another speech modification for this goal]"
  goal_physical_tells:
    - "[Physical tell showing goal-related emotions]"
    - "[Another body language indicator for goal progress]"
  
  created_at: "{{current_timestamp}}"
  context: "[Brief description of what prompted this goal]"
  status: "ACTIVE"
```

Focus on authenticity - this goal should feel like something this specific character would genuinely want and pursue in their own unique way.
```

### Usage Example

To generate a goal for Mei, you would fill the template with:

```yaml
character_name: "Mei"
in_universe_self_description: "the heart of the bamboo grove, mother of the silent stone"
sensory_origin_memory: "the sweet, woody taste of fresh bamboo shoots, the comforting warmth of a sun-warmed boulder"
# ... all other character data from character.yaml
current_reality: "Forest lake → water lapping softly against the shore → breeze rustling the leaves above"
companion: "little one"
recent_interactions:
  - "Newcomer seemed wary but accepted rest in grove"
  - "Newcomer relaxed when I hummed and offered comfort"
```

This will generate a goal like:
```yaml
goal:
  id: "mei_goal_001"
  desired_state: "I feel the little one trusts my care and finds peace in the grove's embrace"
  validation_criteria:
    - "little one accepts food and comfort without hesitation"
    - "little one's breathing becomes calm and steady in my presence"
    - "little one chooses to stay close rather than maintaining distance"
  # ... rest of the goal structure
```