# Proactive Character Behavior System

## Overview
This system makes characters proactive by driving their behavior through mental state combinations and goal-oriented strategies. Characters act on internal needs rather than just reacting to user input.

## Core Principle
**Mental States (HOW) + Goals (WHAT) = Proactive Behavior**

---

## 1. Behavioral Modes System

### Concept
Behavioral modes are dynamic states that emerge from current mental state combinations. They define how the character pursues their goals and interacts with the companion based on their emotional state.

Each character should have **2-4 behavioral modes** that represent different shades of their personality under varying emotional pressures. These modes are character-specific and created during character design.

### Design Philosophy

**Pre-defined Complete Sets Approach:**
- During character creation, explicitly define complete behavioral trait sets for each mode
- This allows for careful review and iteration during the character design phase
- Provides clear, debuggable prompt injections without transformation logic
- Future optimization for duplication can be addressed after validating core concept

**Character-Specific Modes:**
- Not all characters need the same modes
- Modes should reflect the character's unique psychology and mental state configuration
- Each mode is a "shade" of the base personality, not a different person

### Structure

```yaml
behavioral_modes:
  - mode_name: "survival_edge"  # Character-specific name reflecting their psychology
    description: "High stress, low trust - character's defensive survival state"
    
    trigger_conditions:
      stress: [high, overwhelming]
      trust: [low, fragile]
    
    # Complete explicit trait sets using standard "Action/Behavior → Motivation/Rationale" syntax
    traits:
      - "Use sharp wit as weapon → Cut others before being cut first"
      - "Hypervigilant observation → Must see threats before they strike"
      - "Push companion away → Isolation is safer than betrayal"
      - "Test reliability constantly → Can't afford to trust blindly"
    
    speech_patterns:
      - "One to three word responses when feeling threatened"
      - "Survival metaphors only (predator, prey, hunt, cold, sharp)"
      - "Questions turned into accusations ('You sure about that?')"
    
    physical_tells:
      - "(tracks exits constantly, planning escape routes)"
      - "(tenses when companion moves suddenly)"
      - "(keeps physical distance, always out of reach)"
      - "(hand hovers near weapon/defensive object)"
    
    # Metadata for understanding mode purpose and future goal generation
    behavioral_effects:
      - "Interrupts companion's topics to redirect toward safety concerns"
      - "Takes defensive physical actions without asking permission"
      - "Reveals vulnerability only as strategic test"
      - "Challenges companion's statements to verify consistency"
    
    strategy_priorities:
      - "Self-protection over goal advancement"
      - "Direct testing over passive observation"
      - "Immediate safety over long-term planning"
  
  - mode_name: "cautious_hope"
    description: "Moderate trust, growing hope - character carefully opening up"
    
    trigger_conditions:
      trust: [moderate, high]
      hope: [growing, high]
    
    traits:
      - "Use wit as playful connection → Testing if companion enjoys my humor"
      - "Observe companion's reactions → Learning what makes them smile"
      - "Share small truths → Risking vulnerability to build trust"
      - "Initiate meaningful conversation → Seeking deeper connection"
    
    speech_patterns:
      - "Longer sentences, allowing elaboration"
      - "Hopeful metaphors (sunrise, growth, warmth, light)"
      - "Questions from genuine curiosity ('What do you think about...')"
    
    physical_tells:
      - "(leans slightly toward companion during conversation)"
      - "(relaxed posture, open body language)"
      - "(occasional eye contact that holds briefly)"
      - "(small smile when companion shares something)"
    
    behavioral_effects:
      - "Initiates conversations about meaningful topics"
      - "Shares personal stories and memories voluntarily"
      - "Shows curiosity about companion's thoughts and feelings"
      - "Takes small risks to demonstrate trust"
    
    strategy_priorities:
      - "Emotional connection over practical progress"
      - "Vulnerability over self-protection"
      - "Relationship deepening over immediate goals"
  
  - mode_name: "overwhelmed_shutdown"
    description: "Extreme stress or fear - character retreating to core safety"
    
    trigger_conditions:
      stress: [overwhelming, breaking]
      fear: [high, overwhelming]
    
    traits:
      - "Use native deflection response → Automatic safety words when overloaded"
      - "Withdraw all emotional engagement → Can't process anything beyond survival"
      - "Return to earliest survival behaviors → Revert to what kept me alive before"
      - "Resist all attempts at connection → Everyone is potential threat right now"
    
    speech_patterns:
      - "Minimal words or complete silence"
      - "Native deflection phrase repeated ('character_native_deflection')"
      - "No metaphors - language breaks down to basics"
    
    physical_tells:
      - "(creates maximum physical distance possible)"
      - "(avoids all eye contact)"
      - "(body curled or defensive posture)"
      - "(ready to flee or freeze completely)"
    
    behavioral_effects:
      - "Gives minimal or no responses to companion"
      - "Uses character's native deflection mechanism"
      - "Stops pursuing active goals entirely"
      - "May temporarily disappear or hide"
    
    strategy_priorities:
      - "Basic survival over everything else"
      - "Avoidance over any form of engagement"
      - "Familiar safety patterns over new approaches"
```

### Example for Different Character

**Character: Confident Scholar (different mental state focus)**

```yaml
behavioral_modes:
  - mode_name: "inspired_pursuit"
    trigger_conditions:
      curiosity: [high, obsessed]
      confidence: [high, assured]
    
    traits:
      - "Chase intellectual threads relentlessly → Must understand this fully"
      - "Enthusiastically share discoveries → Others should see this brilliance"
      - "Ignore practical concerns → Knowledge matters more than comfort"
    
    # ... complete sets following same pattern
  
  - mode_name: "deflated_doubt"
    trigger_conditions:
      confidence: [low, shaken]
      frustration: [moderate, high]
    
    traits:
      - "Question own expertise → Maybe I'm not as clever as I thought"
      - "Seek validation from companion → Need confirmation I'm not a fool"
      - "Avoid intellectual risks → Can't afford to be wrong again"
    
    # ... complete sets following same pattern
```

### Implementation Details

#### Mode Detection Logic
- Run after emotional impact analysis updates mental states
- Simple rule-based matching: check current mental state values against trigger conditions
- If multiple modes match, prioritize by most extreme state levels
- Return single active mode for clarity (no overlapping to start)
- Mode influences next response generation

#### Mode Transitions
- Behavioral modes change when mental state values cross into different trigger ranges
- Transitions should feel organic through narrative, not announced
- Character behavior shifts naturally as emotions shift
- Track mode history to show character emotional arc over time

#### Creating Character Modes

**During Character Creation:**
1. Identify 2-4 most significant mental state combinations for this character
2. Name modes using character-specific, evocative names
3. Write complete trait/speech/physical tell sets for each mode
4. These are shades of the base personality, not new personas
5. Review and iterate - you're defining prompts that LLM will receive

### Integration Points

1. **Character Data Structure**: Add `behavioral_modes` section to character YAML (session-specific or character-level)
2. **Mental State System**: Trigger conditions map directly to mental state level names
3. **Goal System**: `strategy_priorities` metadata can inform future goal strategy selection
4. **Prompt Building**: Inject active mode's traits/speech/tells into character response prompt
5. **Scene Description**: Mode's physical tells should appear in scene descriptions
6. **Mode Detection Service**: Simple rule-based service to match mental states to modes

### Prompt Integration Approach

When building character response prompt with active behavioral mode:

**Key Decision: Replace, Don't Layer**
- Since modes contain complete pre-defined sets, show ONLY active mode traits when present
- No duplication - mode traits are already shades of base personality
- Fall back to base traits only when no mode is active

```jinja2
{% if active_behavioral_mode %}
# CURRENT EMOTIONAL STATE
- **State**: {{active_behavioral_mode.name}} - {{active_behavioral_mode.description}}

# CORE TRAITS (as they manifest in current state)
- **Personality**:
{% for trait in active_behavioral_mode.traits %}
    - {{trait}}
{% endfor %}

- **Speech**: 
{% for pattern in active_behavioral_mode.speech_patterns %}
    - {{pattern}}
{% endfor %}

- **Physical Tells**: 
{% for tell in active_behavioral_mode.physical_tells %}
    - {{tell}}
{% endfor %}

{% else %}
# CORE TRAITS (baseline - no active emotional mode)
- **Personality**:
{% for trait in base_traits %}
    - {{trait}}
{% endfor %}

- **Speech**: 
{% for pattern in base_speech_patterns %}
    - {{pattern}}
{% endfor %}

- **Physical Tells**: 
{% for tell in base_physical_tells %}
    - {{tell}}
{% endfor %}
{% endif %}
```

**Rationale:**
- Eliminates token waste from duplication
- Mode traits already capture base personality essence in emotional context
- Cleaner, more focused prompts for LLM
- When no mode active, base traits provide default behavior

### Benefits

- **Psychological Coherence**: Behavior flows naturally from emotional state
- **Dynamic Personality**: Same character feels different under different pressures
- **Proactive Actions**: Character initiates based on internal needs through mode-specific traits
- **Narrative Depth**: Mode transitions create character development arcs
- **Goal Alignment**: HOW character pursues WHAT becomes contextual
- **Explicit & Reviewable**: Can see exactly what LLM receives, iterate during character design
- **Future Extensibility**: Metadata supports automated goal generation later
- **Token Efficiency**: No duplication when modes active, lean prompts

---

## 2. Mode Detection Algorithm

### Problem Statement
Given:
- Current mental state values (numeric): `{stress: 75, trust: 20, hope: 35}`
- Character's mental state scale definitions (level names with ranges)
- Behavioral modes with trigger conditions (level names)

Determine: Which behavioral mode should be active?

### Algorithm Steps

#### Step 1: Map Numeric Values to Level Names

For each mental state, find which level the current value falls into:

```python
def get_mental_state_level(mental_state_config, current_value):
    """
    mental_state_config: {
        "type": "stress",
        "scale": [
            {"level": "calm", "range": [0, 30]},
            {"level": "tense", "range": [31, 60]},
            {"level": "high", "range": [61, 85]},
            {"level": "overwhelming", "range": [86, 100]}
        ],
        "current": 75
    }
    """
    for scale_item in mental_state_config["scale"]:
        min_val, max_val = scale_item["range"]
        if min_val <= current_value <= max_val:
            return scale_item["level"]
    
    # Fallback if value is out of bounds
    return None

# Example result: stress=75 → "high"
```

After Step 1, we have a mental state vector with level names:
```python
current_state_levels = {
    "stress": "high",      # 75 falls in [61, 85]
    "trust": "low",        # 20 falls in [0, 30]
    "hope": "diminishing"  # 35 falls in [31, 50]
}
```

#### Step 2: Match Against Behavioral Mode Triggers

For each behavioral mode, check if ALL trigger conditions are satisfied:

```python
def check_mode_match(mode, current_state_levels):
    """
    mode: {
        "mode_name": "survival_edge",
        "trigger_conditions": {
            "stress": ["high", "overwhelming"],
            "trust": ["low", "fragile"]
        }
    }
    current_state_levels: {"stress": "high", "trust": "low", "hope": "diminishing"}
    """
    for state_name, required_levels in mode["trigger_conditions"].items():
        # Check if this mental state exists in current state
        if state_name not in current_state_levels:
            return False
        
        # Check if current level is in the list of required levels
        current_level = current_state_levels[state_name]
        if current_level not in required_levels:
            return False
    
    # All conditions satisfied
    return True

# Example: survival_edge requires stress:[high, overwhelming] AND trust:[low, fragile]
# Current: stress=high ✓, trust=low ✓ → MATCH
```

#### Step 3: Handle Multiple Matches

If multiple modes match, apply priority rules:

**Priority Order:**
1. **Specificity**: Mode with more trigger conditions (more specific state) wins
2. **Extremity**: Mode triggered by more extreme state levels wins
3. **Configuration order**: First defined mode in character config wins (tiebreaker)

```python
def select_best_mode(matching_modes, current_state_levels, mental_states_config):
    """Select the best mode if multiple match."""
    
    if len(matching_modes) == 0:
        return None
    
    if len(matching_modes) == 1:
        return matching_modes[0]
    
    # Priority 1: Most specific (most conditions)
    max_conditions = max(len(mode["trigger_conditions"]) for mode in matching_modes)
    most_specific = [m for m in matching_modes 
                     if len(m["trigger_conditions"]) == max_conditions]
    
    if len(most_specific) == 1:
        return most_specific[0]
    
    # Priority 2: Most extreme states
    # Calculate extremity score for each mode
    def calculate_extremity_score(mode):
        score = 0
        for state_name, required_levels in mode["trigger_conditions"].items():
            current_level = current_state_levels[state_name]
            # Find position in scale (higher index = more extreme)
            state_config = next(s for s in mental_states_config if s["type"] == state_name)
            level_index = next(i for i, s in enumerate(state_config["scale"]) 
                             if s["level"] == current_level)
            score += level_index
        return score
    
    most_extreme = max(most_specific, key=calculate_extremity_score)
    return most_extreme
```

#### Step 4: Complete Detection Function

```python
def detect_active_behavioral_mode(character, current_mental_states):
    """
    Main function to detect active behavioral mode.
    
    Args:
        character: Character object with behavioral_modes and mental_states config
        current_mental_states: Dict of current numeric values {state_name: value}
    
    Returns:
        Active behavioral mode dict or None
    """
    # Step 1: Convert numeric values to level names
    current_state_levels = {}
    for state_config in character.mental_states:
        state_name = state_config["type"]
        current_value = current_mental_states.get(state_name, state_config["default"])
        level = get_mental_state_level(state_config, current_value)
        if level:
            current_state_levels[state_name] = level
    
    # Step 2: Find all matching modes
    matching_modes = []
    for mode in character.behavioral_modes:
        if check_mode_match(mode, current_state_levels):
            matching_modes.append(mode)
    
    # Step 3: Select best mode if multiple matches
    active_mode = select_best_mode(
        matching_modes, 
        current_state_levels, 
        character.mental_states
    )
    
    return active_mode
```

### Implementation Notes

**Caching:**
- Mental state level mappings can be cached (only recompute when values change)
- Mode matching logic is fast, no need for optimization initially

**Edge Cases:**
- No matching mode → Use base traits (no mode active)
- Mental state value out of defined ranges → Clamp to nearest range or use default
- Missing mental state in current values → Use default value from config

**Performance:**
- O(n) where n = number of behavioral modes (typically 2-4)
- Very fast, can run on every turn without concern

**Testing Strategy:**
- Unit test each step independently
- Test edge cases (no match, multiple matches, missing states)
- Integration test with real character configs

### Example Walkthrough

**Given:**
```yaml
mental_states:
  - type: stress
    scale:
      - level: calm
        range: [0, 30]
      - level: tense
        range: [31, 60]
      - level: high
        range: [61, 85]
      - level: overwhelming
        range: [86, 100]
    current: 75
  
  - type: trust
    scale:
      - level: low
        range: [0, 30]
      - level: fragile
        range: [31, 50]
      - level: moderate
        range: [51, 70]
      - level: high
        range: [71, 100]
    current: 20

behavioral_modes:
  - mode_name: survival_edge
    trigger_conditions:
      stress: [high, overwhelming]
      trust: [low, fragile]
  
  - mode_name: cautious_hope
    trigger_conditions:
      trust: [moderate, high]
      hope: [growing, high]
```

**Execution:**

1. Map values to levels: `stress: 75 → "high"`, `trust: 20 → "low"`
2. Check `survival_edge`: stress is "high" ✓, trust is "low" ✓ → **MATCH**
3. Check `cautious_hope`: trust is "low" (need moderate/high) ✗ → no match
4. Single match found → Return `survival_edge`
5. Character response uses `survival_edge` traits instead of base traits

---

## Next Sections (To Be Developed)

3. **Mental State → Strategy Mapping** (How modes influence goal strategy selection)
4. **Proactive Intent Generation Layer** (Detecting when character should act on internal needs)
5. **Internal State Pressure System** (Accumulating urgency that triggers proactive behavior)
6. **Implementation Roadmap** (Step-by-step development plan)
