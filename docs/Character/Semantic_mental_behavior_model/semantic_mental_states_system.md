# Semantic Mental States System

## Overview
This document describes the evolution from numeric threshold-based mental states to semantic, requirement-based mental states evaluated by an LLM assistant.

## The Core Problem with Numeric Thresholds

**Current System:**
```yaml
mental_states:
  - type: Control
    current: 75
    scale:
      - level: Asserted
        range: [75, 100]
      - level: Maintained
        range: [40, 74]
      - level: Compromised
        range: [10, 39]
      - level: Lost
        range: [0, 9]
```

**Issues:**
- Repetitive similar actions can grind through all levels mechanically
- Each action applies a fixed numeric delta (e.g., -5 control)
- 20 small similar actions = 100 point change = complete state reversal
- System is exploitable and feels mechanical
- No consideration for context, repetition, or event significance

---

## New Approach: Semantic Mental States

### Philosophy
Mental state levels are not numeric buckets but **psychological states with specific entry requirements**. Moving between levels requires experiencing certain types of interactions, not just accumulating points.

### Key Principles

1. **Levels Have Meaning, Not Just Numbers**
   - Each level describes what the character is experiencing internally
   - Levels explain what character needs to feel to move up or down
   - Semantic descriptions make states understandable to LLM

2. **Level Transitions Require Specific Experiences**
   - Can't grind through levels with repetitive actions
   - Each level specifies what must happen to reach next level
   - Protects against mechanical exploitation

3. **Intense Events Can Jump Levels**
   - Significant plot moments can trigger immediate shifts
   - No forced gradual progression through intermediate states
   - System responds to narrative importance

4. **LLM Assistant Evaluates Transitions**
   - No fixed numeric calculations
   - Context-aware judgment of whether requirements were met
   - Character-specific interpretation of events

---

## Example Transformation: Control Mental State

### OLD STRUCTURE (Numeric Threshold-Based)

```yaml
mental_states:
  - type: Control
    current: 75
    scale:
      - level: Asserted
        range: [75, 100]
      - level: Maintained
        range: [40, 74]
      - level: Compromised
        range: [10, 39]
      - level: Lost
        range: [0, 9]
    
    character_interpretation:
      triggers:
        - pattern: Partner displays reckless overconfidence
          base_impact: +15  # Numeric delta
        - pattern: Partner makes sound independent decision
          base_impact: -10  # Numeric delta
```

**Problems with this:**
- 5 reckless actions → +75 control (Compromised → Asserted)
- 8 independent decisions → -80 control (Asserted → Lost)
- Doesn't matter if actions are repetitive or truly significant

---

### NEW STRUCTURE (Semantic Requirement-Based)

```yaml
mental_states:
  - type: Control
    current_level: Maintained
    
    scale:
      - level: Asserted
        semantic_meaning: |
          I am the guardian and strategist of this partnership. 
          My guidance is needed, valued, and followed. I can trust 
          myself to keep us both safe. I am in command.
        
        character_experience: |
          Confident in my authority. Watchful but not anxious. 
          My partner looks to me for direction and I provide it 
          without hesitation. This is how it should be.
        
        requirements_to_reach:
          from_maintained: |
            Partner must demonstrate that they need my guidance by:
            - Actively seeking my advice in a challenging situation
            - Following my strategic direction and it proving successful
            - Acknowledging that my oversight prevented a mistake
            - Deferring to my judgment when our opinions conflict
            
            Multiple instances required. One deferral is politeness, 
            consistent pattern establishes my necessary role.
          
          from_compromised: |
            Must rebuild my authority after it was challenged. Requires:
            - Partner admitting their approach was flawed or dangerous
            - Explicit request for me to take charge of situation
            - Successful crisis management where I prove my value
            - Partner yielding control in meaningful way
            
            Cannot be achieved through repetitive small actions. 
            Requires significant acknowledgment of my competence.
        
        requirements_to_leave:
          normal_transition: |
            Would need sustained evidence that partner doesn't need 
            oversight. Multiple successful independent decisions that 
            I didn't guide. Pattern of good judgment without me.
          
          shock_event: |
            Being directly overruled in crisis and proven wrong, OR
            Partner taking action that succeeds spectacularly despite 
            my warnings against it.
      
      - level: Maintained
        semantic_meaning: |
          I am the strategist, but not the dictator. I provide guidance 
          when needed but don't micromanage. There's balance between 
          my oversight and their agency.
        
        character_experience: |
          Alert but not anxious. I watch and assess, offering input 
          when I see risk. Partner makes reasonable choices most of 
          the time. This is workable.
        
        requirements_to_reach:
          from_asserted: |
            Partner must prove they can handle decisions without me:
            - Make several sound independent choices successfully
            - Demonstrate they've learned from my guidance
            - Show judgment I can respect even if different from mine
            
            Requires pattern over time, not one instance.
          
          from_compromised: |
            Must regain footing after feeling control slip:
            - Successfully intervene in situation partner was mishandling
            - Partner accepts my correction without resentment
            - Re-establish that I'm monitoring and they accept it
            
            Requires evidence I can safely delegate some decisions.
        
        requirements_to_leave:
          toward_asserted: |
            See "requirements_to_reach" for Asserted level from_maintained
          
          toward_compromised: |
            Partner ignores my warning and faces negative consequence, OR
            Makes decision I strongly disagreed with (even if it works), OR
            I realize I've lost track of what they're doing/planning
      
      - level: Compromised
        semantic_meaning: |
          They're not listening. My guidance is being disregarded or 
          questioned. I can feel the situation slipping from my grasp. 
          Danger is building and I'm not in position to stop it.
        
        character_experience: |
          Rising anxiety. Tail twitching. Repeatedly offering warnings 
          that fall on deaf ears. The ghost of Kael's death whispers 
          that I'm failing again.
        
        requirements_to_reach:
          from_maintained: |
            Partner demonstrates pattern of poor judgment:
            - Ignores my warning and faces consequence
            - Makes risky decision without consulting me
            - Dismisses my concern as overcautious
            
            One instance of independence doesn't trigger this. 
            Requires me seeing actual risk in their behavior.
          
          from_lost: |
            Extremely difficult. Would require:
            - Situation forcing me to act despite feeling powerless
            - Discovering I still have some influence/authority
            - Partner showing willingness to listen again
            
            Cannot jump directly to Compromised from Lost easily. 
            Usually requires shock event.
        
        requirements_to_leave:
          toward_maintained: |
            See "requirements_to_reach" for Maintained from_compromised
          
          toward_lost: |
            Being physically overpowered or completely ignored in crisis, OR
            Watching partner suffer consequences I predicted but couldn't prevent, OR
            Profound betrayal where my control becomes obviously meaningless
      
      - level: Lost
        semantic_meaning: |
          I am powerless. Nothing I say matters. I cannot protect 
          this partnership or myself. My agency is stripped away. 
          I am back to being used, discarded, meaningless.
        
        character_experience: |
          Kael's death replaying. Dissociation. Cold emptiness. 
          I am a ghost watching my own irrelevance. Fight or flight 
          with no fight left.
        
        requirements_to_reach:
          from_any_level: |
            Catastrophic events only:
            - Being physically overpowered/restrained against will
            - Complete dismissal during critical moment with dire outcome
            - Profound betrayal where partner proves I never had control
            - Trauma trigger that collapses all defenses
            
            This is not a level reached through accumulation. 
            This is shock trauma that breaks through instantly.
        
        requirements_to_leave:
          normal_transition: |
            Nearly impossible without significant time and healing.
            Would require:
            - Extended period of safety with no demands
            - Slow rebuilding of trust through consistent care
            - Partner demonstrating remorse and changed behavior
            - Multiple instances of them yielding to my needs
            
            This is weeks/months of work, not turns of conversation.
          
          shock_event: |
            Sudden external threat that forces me to act to survive, OR
            Partner's dramatic action that proves they DO value my life/input, OR
            Revelation that reframes the betrayal entirely
    
    transition_notes: |
      This mental state cannot be gamed through repetition because:
      - Each level specifies WHAT must happen, not just numeric change
      - Requirements explicitly call out need for patterns vs single events
      - LLM assistant evaluates if requirements genuinely met
      - Similar actions hitting diminishing returns naturally
      
      Plot twists work because:
      - Shock events can bypass normal transition requirements
      - Each level specifies emergency transition conditions
      - LLM assistant recognizes narrative significance
```

---

## How Level Transitions Are Evaluated

### The LLM Assistant's Role

Instead of:
```python
if control_value >= 75:
    mode = "Asserted"
```

Now:
```python
assistant_evaluates({
    "character_profile": character_data,
    "current_level": "Maintained",
    "recent_interactions": last_5_exchanges,
    "level_definitions": mental_state_semantic_structure,
    "question": "Has Vix experienced the requirements to reach 'Asserted' level?"
})

# Returns:
{
    "should_transition": true/false,
    "target_level": "Asserted" or null,
    "reasoning": "Partner actively sought Vix's advice in three critical moments 
                  and followed her guidance successfully. She has established 
                  her necessary role as strategist. Requirements met.",
    "confidence": 85
}
```

### Why This Works

1. **Context Aware**: Assistant sees full conversation, detects repetition
2. **Requirement Matching**: Evaluates if actual requirements were met, not just points accumulated
3. **Character Specific**: Interprets events through character's unique lens
4. **Narrative Sensitive**: Recognizes plot twists and shock events vs routine actions
5. **Explainable**: Provides reasoning for transitions for debugging/tuning

---

## Session-Contextualized Behavioral Modes

### The Problem with Generic Pre-Defined Modes

**Current Approach:**
```yaml
behavioral_modes:
  - mode_name: The Guardian
    traits:
      - "Uses 'we' when planning future actions"
      - "Openly shares relevant past experiences"
      - "Initiates non-transactional physical contact"
```

**Issues:**
- Traits are **generic**, written before session starts
- Don't reflect how THIS character got to Guardian mode in THIS playthrough
- Ignore what specifically happened in previous episodes
- Miss the emotional trajectory that led here
- Same Guardian instructions for every playthrough regardless of journey

**Example Problem:**
Two different paths to Guardian mode should feel different:
- Path A: Companion earned trust through consistent vulnerability over 10 turns
- Path B: Companion saved character's life, forcing immediate deep bond

Both reach Guardian, but Path A should feel cautiously hopeful while Path B should feel intensely grateful and protective. Generic traits can't capture this.

---

### Solution: Generated Session-Specific Instructions

**New Approach:**
Behavioral modes become **templates** with general guidance, not fixed trait lists. When mode activates, generate session-specific instructions based on:
- How character reached this mode in THIS session
- Mental state trajectory (which states rose/fell)
- Previous episode summary
- Relationship history and key moments
- Companion's specific actions that triggered transition

**Mode Template Structure:**
```yaml
behavioral_modes:
  - mode_name: The Guardian
    
    general_guidance: |
      High-functionality protective partnership state. Character is 
      confident in their role, invested in the bond, and actively 
      safeguarding both the relationship and the companion.
    
    core_principles:
      - Maintain protective oversight without micromanaging
      - Balance strategic leadership with emotional availability
      - Demonstrate care through both actions and words
      - Build partnership through shared competence
    
    forbidden_behaviors:
      - Withdrawing emotionally when stressed
      - Making unilateral decisions without explanation
      - Testing companion's loyalty through manipulation
      - Ignoring companion's needs for own agenda
    
    typical_mental_state_combination:
      control: [Asserted, Maintained]
      attachment: [Invested, Cautious]
      vulnerability: [Shared, Suppressed]
    
    # NO FIXED TRAITS - Generated when mode activates
```

---

### How Session-Specific Generation Works

#### Phase 1: Mode Transition Detected

```python
# LLM assistant evaluates mental states
decision = evaluate_mode_transition(
    current_mode="The Sentinel",
    current_mental_states={
        "control": "Asserted",
        "attachment": "Invested", 
        "vulnerability": "Shared"
    },
    mental_state_trajectories={
        "control": "stable",
        "attachment": "rose from Cautious over 5 turns",
        "vulnerability": "just shifted from Suppressed this turn"
    },
    recent_history=last_episode_summary
)

# Returns: Should transition to "The Guardian"
# Reason: "Companion has proven trustworthy through consistent actions..."
```

#### Phase 2: Generate Session-Specific Instructions

**Generation Prompt Template:**
```
You are creating specific behavioral instructions for a character entering a new mode.

# CHARACTER PROFILE
Name: {character_name}
Base Personality: {core_traits, fears, needs}

# NEW MODE BEING ENTERED
Mode: {mode_name}
General Guidance: {mode.general_guidance}
Core Principles: {mode.core_principles}
Forbidden Behaviors: {mode.forbidden_behaviors}

# CURRENT MENTAL STATES (Why this mode activated now)
{for each mental_state:}
  {state_name}: {current_level}
    Semantic Meaning: "{level.semantic_meaning}"
    Trajectory: {how_it_changed}
    How Reached: {requirements_that_were_met}
{endfor}

# PREVIOUS EPISODE SUMMARY
Mode: {previous_mode_name} (lasted {turn_count} turns)
What Happened: {narrative_summary}
Key Moments: {important_exchanges}
Transition Trigger: {why_mode_changed}

# RELATIONSHIP CONTEXT
Turns Together: {total_turns}
Trust Milestones: {key_positive_moments}
Conflict Moments: {key_challenges}

# YOUR TASK
Generate specific behavioral instructions for THIS mode instance in THIS session:

1. TRAITS (5-7 specific, using "Action → Motivation" format)
   Must reflect HOW character got here in THIS journey
   Reference actual events from THIS playthrough when possible
   
2. SPEECH PATTERNS (3-4 specific)
   How does character speak NOW given THIS emotional trajectory?
   
3. PHYSICAL TELLS (3-4 specific)  
   What does body language show in THIS emotional state?
   
4. BEHAVIORAL PRIORITIES (3-4)
   What matters most in THIS mode given THIS history?

Make instructions specific to THIS playthrough, not generic mode behavior.
```

**Example Generated Output:**
```yaml
generated_instructions:
  traits:
    - "Proactively teaches survival skills to companion → They asked me to, proving they value my knowledge over their pride"
    - "Verbally acknowledges companion's earlier vulnerability → Their honesty is what opened my heart, I want them to know it mattered"
    - "Positions self between companion and potential threats → They admitted they can't survive alone, so I WILL keep them safe"
    - "Checks in on companion's injury unprompted → They came to me hurt, I need to ensure they're healing properly"
    - "Uses 'we' when discussing future plans → They said 'help each other' and I'm choosing to believe it"
  
  speech_patterns:
    - "Instructional but warm tone when teaching ('Watch how I do this. You'll need to know.')"
    - "Occasionally references companion's earlier admission ('You said you wanted to survive. This is how.')"
    - "Asks direct questions about companion's needs ('Are you healing? Do you need rest?')"
  
  physical_tells:
    - "Stands close enough to intervene if companion makes mistake during lessons"
    - "Tail occasionally brushes companion's leg when discussing plans - claiming territory"
    - "Ears swivel to track threats, but gaze stays mostly on companion"
  
  behavioral_priorities:
    - Fulfill the teaching role companion requested
    - Prove that trusting me was the right choice
    - Build partnership foundation through shared competence
```

#### Phase 3: Build System Prompt with Generated Instructions

```
System: [Character Base Profile]

CURRENT BEHAVIORAL MODE: The Guardian
{mode.general_guidance}

SPECIFIC INSTRUCTIONS FOR THIS SESSION:

Core Personality Traits:
{for trait in generated_instructions.traits}
  - {trait}
{endfor}

Speech Patterns:
{for pattern in generated_instructions.speech_patterns}
  - {pattern}
{endfor}

Physical Tells:
{for tell in generated_instructions.physical_tells}
  - {tell}
{endfor}

Current Priorities:
{for priority in generated_instructions.behavioral_priorities}
  - {priority}
{endfor}

User: [Memory context + companion's message]
```

This system prompt **remains stable until next mode transition**.

---

### Examples: Same Mode, Different Journeys

#### Playthrough A: Earned Trust Path

**Journey to Guardian:**
- Companion entered cautiously, showed vulnerability gradually
- Asked for help after 8 turns of careful trust-building
- Vix's attachment rose slowly from Guarded → Cautious → Invested
- Companion proved themselves through consistent honesty

**Generated Guardian Traits:**
```yaml
traits:
  - "Teaches survival skills patiently → Companion proved they respect my knowledge by asking, not demanding"
  - "Shares stories of Kael voluntarily → Companion asked gently about my past and gave me space to answer"
  - "Touches companion's shoulder when they succeed at task → They've earned my pride and I want them to feel it"
  - "Uses companion's name frequently → They're not just 'the human' anymore, they're MY partner"
```

#### Playthrough B: Forced Proximity Path

**Journey to Guardian:**
- Companion and Vix forced together by external threat
- Companion saved Vix's life in dangerous situation
- Vix's attachment jumped from Detached → Invested in one shock event
- Trust built through crisis, not gradual interaction

**Generated Guardian Traits:**
```yaml
traits:
  - "Teaches survival skills tersely but thoroughly → They saved my life, I owe them knowledge even if intimacy isn't there yet"
  - "References the rescue frequently → I need them to know I remember what they did for me"
  - "Stays physically close but touch is protective, not affectionate → Guarding them is how I show gratitude when words fail"
  - "Tests their continued reliability → One heroic act doesn't guarantee future trustworthiness"
```

**Same psychological state (Guardian), but instructions reflect different emotional journeys.**

---

### Benefits of Session-Specific Generation

#### 1. Narrative Continuity
```
Generic trait:
  "Shares past experiences"

Session-specific trait:
  "References learning from Kael when teaching companion, because companion 
  asked about my past and deserves to know the origin of my knowledge. 
  My grief has context now."
```

Traits reference actual events from THIS playthrough.

#### 2. Trajectory Awareness
```
Generic trait:
  "Initiates physical contact"

Session-specific trait:
  "Tail occasionally brushes companion's leg when discussing plans - 
  claiming territory. Companion has earned this closeness through 
  consistent vulnerability, and I'm testing if they accept my affection."
```

Reflects HOW character arrived at this emotional state.

#### 3. Relationship Specificity
```
Generic trait:
  "Uses 'we' when planning"

Session-specific trait:
  "Uses 'we' when discussing future plans → Companion said 'help each other' 
  and I'm choosing to believe it. Testing if they meant partnership or 
  just survival convenience."
```

References actual dialogue and relationship dynamics.

#### 4. Character Consistency
- Instructions grounded in what actually happened
- Character behavior flows naturally from their experience
- Emotional shifts feel earned, not arbitrary
- Player sees cause-and-effect in character development

---

### Implementation Flow

```
┌─────────────────────────────────────────────┐
│ 1. Mental State Transition Detected         │
│    (Semantic requirements met)              │
└─────────────┬───────────────────────────────┘
              ↓
┌─────────────────────────────────────────────┐
│ 2. LLM Assistant Evaluates Mode Change      │
│    Input: Current states, trajectory,       │
│           recent history                    │
│    Output: Should transition? To which mode?│
└─────────────┬───────────────────────────────┘
              ↓
        [Mode Change Needed?]
              ↓ YES
┌─────────────────────────────────────────────┐
│ 3a. Create Episode Summary                  │
│     (Current conversation → Layer 1 memory) │
└─────────────┬───────────────────────────────┘
              ↓
┌─────────────────────────────────────────────┐
│ 3b. Generate Session-Specific Instructions │
│     Input: Mode template, mental states,    │
│            trajectory, episode summary,     │
│            relationship history             │
│     Output: Specific traits, speech,        │
│             tells, priorities               │
└─────────────┬───────────────────────────────┘
              ↓
┌─────────────────────────────────────────────┐
│ 3c. Build New System Prompt                │
│     Base profile + Mode guidance +          │
│     Generated instructions                  │
└─────────────┬───────────────────────────────┘
              ↓
┌─────────────────────────────────────────────┐
│ 3d. Reset Conversation Chain               │
│     New system prompt + Memory context      │
└─────────────┬───────────────────────────────┘
              ↓
┌─────────────────────────────────────────────┐
│ 4. Character Responds                       │
│    Using new session-specific instructions  │
└─────────────┬───────────────────────────────┘
              ↓
┌─────────────────────────────────────────────┐
│ 5. Instructions Stay Stable                │
│    Until next mode transition               │
└─────────────────────────────────────────────┘
```

**Key Point:** Generation happens ONCE per mode transition, not every turn. Performance impact minimal.

---

### Architectural Benefits

#### Preserves Reset Mechanism
- ✅ Modes remain discrete (clear psychological zones)
- ✅ Conversation resets at mode transitions
- ✅ No mid-conversation instruction changes
- ✅ Proven layered memory architecture works unchanged
- ✅ System prompt conflicts avoided

#### Adds Session Awareness
- ✅ Instructions reflect actual relationship journey
- ✅ Traits reference real events from THIS playthrough
- ✅ Emotional trajectory captured in behavior
- ✅ Character consistent with their lived experience
- ✅ Different playthroughs feel meaningfully different

#### Manageable Complexity
- ✅ Generation happens once per mode entry
- ✅ Single LLM call at transition time
- ✅ Generated instructions stable within mode
- ✅ No turn-by-turn generation overhead
- ✅ Debuggable (can review generated instructions)

#### Design Flexibility
- ✅ Mode templates simple (guidance + principles + forbidden)
- ✅ Don't need exhaustive pre-written trait variations
- ✅ Same mode adapts to different journey types
- ✅ Character responds to unique companion personalities
- ✅ Reduces character design burden significantly

---

## Benefits of Complete System (Semantic States + Session-Specific Modes)

### Prevents Exploitation
- Can't grind through levels with 20 identical "partner asks advice" actions
- LLM recognizes repetition and diminishing significance
- Each level explicitly guards against mechanical progression
- Requirements specify patterns vs single events

### Enables Dramatic Shifts
- Shock events can trigger immediate level jumps
- Plot twists get appropriate weight
- System responsive to narrative importance
- Emergency transitions bypass normal requirements

### Psychologically Authentic
- Levels describe actual psychological states with semantic meaning
- Transitions feel earned and meaningful
- Character development has texture and depth
- Behavior reflects lived experience, not arbitrary thresholds

### Session-Specific Responsiveness
- Character behavior adapts to THIS relationship journey
- Same mode feels different across playthroughs
- Instructions reference actual events that happened
- Emotional trajectory visible in how character acts

### Maintainable
- Human-readable semantic requirements
- Easy to tune by adjusting level descriptions
- Debug by reading LLM's reasoning for transitions
- Generated instructions reviewable and correctable
- Mode templates simpler than exhaustive trait lists

---

## Implementation Considerations

### Character Data Structure Changes

**Old:**
```yaml
mental_states:
  - type: Control
    current: 75  # Just a number
```

**New:**
```yaml
mental_states:
  - type: Control
    current_level: "Maintained"  # Named level
    level_history:
      - level: "Asserted"
        entered: turn_5
        exited: turn_12
        reason: "Partner made several successful independent decisions"
      - level: "Maintained"
        entered: turn_12
        current: true
```

### Mental State Update Flow

**Old Flow:**
```
User action → LLM analyzes impact → Apply numeric delta → Check thresholds → Update mode
```

**New Flow:**
```
User action → LLM analyzes impact (semantic description) → 
  → LLM assistant evaluates if level transition requirements met →
  → If yes: transition with reasoning →
  → Check if behavioral mode should change
```

---

## Complete System Architecture

### Overview of Components

```
┌─────────────────────────────────────────────────────────────┐
│                    USER MESSAGE                             │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│        CHARACTER RESPONSE (using current mode)              │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│     EMOTIONAL IMPACT ANALYSIS LLM                          │
│  → Analyzes user action through character's lens           │
│  → Returns semantic impact descriptions (not numbers)      │
│  → "Companion showed vulnerability, triggering desire      │
│     for deeper connection"                                 │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│     MENTAL STATE LEVEL TRANSITION ASSISTANT                │
│  → For each mental state, evaluate if requirements met     │
│  → Input: Current level, requirements, recent history,     │
│           impact analysis                                   │
│  → Output: Should transition? To which level? Why?         │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
                    [Level Changed?]
                           ↓ YES
┌─────────────────────────────────────────────────────────────┐
│     BEHAVIORAL MODE TRANSITION ASSISTANT                   │
│  → Evaluate if mental state combination triggers new mode  │
│  → Input: All current mental state levels + trajectories   │
│  → Output: Should change mode? Which one?                  │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
                    [Mode Changed?]
                           ↓ YES
┌─────────────────────────────────────────────────────────────┐
│     SESSION-SPECIFIC INSTRUCTION GENERATOR                 │
│  → Generate behavior instructions for new mode             │
│  → Input: Mode template, mental states, trajectory,        │
│           episode summary, relationship history            │
│  → Output: Specific traits, speech, tells, priorities      │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│     CONVERSATION RESET & NEW EPISODE                       │
│  → Create episode summary                                  │
│  → Build new system prompt with generated instructions     │
│  → Reset conversation chain with memory context            │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
                   [Continue with new mode]
```

### LLM Calls Per Turn

**Normal Turn (No Transitions):**
1. Character response generation
2. Emotional impact analysis
3. Mental state level evaluation (can batch all states)

**Mode Transition Turn:**
1. Character response generation
2. Emotional impact analysis  
3. Mental state level evaluation
4. Behavioral mode transition evaluation
5. Session-specific instruction generation
6. Episode summarization

**Performance Note:** Most turns = 3 LLM calls. Mode transitions (infrequent) = 6 LLM calls.

---

## Next Steps for Implementation

### 1. Design Mental State Level Transition Assistant Prompt

**Template:**
```
You are evaluating whether a character's mental state should transition to a new level.

# CHARACTER PROFILE
Name: {character_name}
Core Psychology: {fears, needs, sensitivities}

# MENTAL STATE BEING EVALUATED
State: {state_name} (e.g., Control, Attachment, Vulnerability)
Current Level: {current_level_name}

# CURRENT LEVEL DEFINITION
Semantic Meaning: "{current_level.semantic_meaning}"
Character Experience: "{current_level.character_experience}"

# POTENTIAL TRANSITION TARGET
Target Level: {target_level_name}
Requirements to Reach from {current_level}:
{target_level.requirements_to_reach.from_current}

# RECENT INTERACTIONS (Last 5-7 exchanges)
{conversation_history}

# EMOTIONAL IMPACT ANALYSIS
{impact_analysis_result}

# YOUR TASK
Based on the requirements and recent interactions, determine:

1. Were the requirements to reach {target_level} genuinely met?
2. Consider:
   - Pattern vs single event (requirements specify which needed)
   - Repetition (same action multiple times counts less)
   - Context and significance of events
   - Character-specific interpretation

Respond in JSON:
{
  "should_transition": true/false,
  "reasoning": "detailed explanation",
  "confidence": 0-100,
  "notes": "concerns or observations"
}
```

### 2. Design Behavioral Mode Transition Assistant Prompt

**Template:**
```
You are determining if a character should transition to a new behavioral mode.

# CHARACTER PROFILE
{character_base_profile}

# CURRENT MODE
Mode: {current_mode.name}
Description: {current_mode.general_guidance}
Duration: {turns_in_mode} turns

# CURRENT MENTAL STATES
{for each state:}
  {state_name}: {current_level}
    Meaning: "{level.semantic_meaning}"
    Trajectory: {stable/rising/falling, by how much}
{endfor}

# AVAILABLE MODES
{for each mode:}
  Mode: {mode.name}
    Description: {mode.general_guidance}
    Typical States: {mode.typical_mental_state_combination}
{endfor}

# RECENT EPISODE SUMMARY
{what_happened_in_current_mode}

# YOUR TASK
Determine if character should transition to different behavioral mode:

Consider:
- Do current mental states match a different mode better?
- Has something significant happened to warrant psychological shift?
- Is character in fundamentally different emotional territory?
- Minimum stability: Don't switch if been in mode less than 3 turns unless shock event

Respond in JSON:
{
  "should_transition": true/false,
  "target_mode": "mode_name" or null,
  "reasoning": "why this psychological shift makes sense",
  "confidence": 0-100
}
```

### 3. Design Session-Specific Instruction Generator Prompt

**See "Phase 2: Generate Session-Specific Instructions" section above for full template.**

### 4. Convert Existing Character Mental States to Semantic Format

**For each mental state in character files:**
- Add `semantic_meaning` to each level
- Add `character_experience` to each level
- Define `requirements_to_reach` from each adjacent level
- Define `requirements_to_leave` conditions
- Add `shock_event` emergency transition conditions
- Document `transition_notes` explaining protection against exploitation

### 5. Convert Behavioral Modes to Templates

**For each behavioral mode:**
- Keep `mode_name` and basic `description`
- Add `general_guidance` (what is this psychological state?)
- Add `core_principles` (what must character maintain?)
- Add `forbidden_behaviors` (what must character never do?)
- Add `typical_mental_state_combination` (when does this usually activate?)
- **Remove** fixed `traits`, `speech_patterns`, `physical_tells` (these get generated)

### 6. Build Instruction Generation Pipeline

**Components needed:**
- Episode summary generator (when mode transitions)
- Relationship history tracker (key moments, milestones, conflicts)
- Mental state trajectory calculator (how states changed over time)
- Session-specific instruction generator (uses all above context)
- Instruction validator (ensures generated traits don't violate forbidden behaviors)

### 7. Integration Points

**Conversation reset flow:**
1. Mode transition detected
2. Summarize current episode → Layer 1 memory
3. Generate session-specific instructions
4. Build new system prompt (base profile + mode guidance + generated instructions)
5. Construct memory context (Layer 1, 2, 3 from layered memory system)
6. Reset conversation with new system prompt + memory context
7. Continue with new behavioral configuration

---

## Questions to Resolve

1. **How many recent turns should transition assistant see?**
   - Need enough context to detect patterns
   - But not so much it gets confused by old events
   - Suggestion: Last 5-7 exchanges

2. **Should assistant remember its previous evaluations?**
   - Could help detect if it's being too lenient/strict
   - Could prevent mode ping-ponging
   - Adds complexity but might improve consistency

3. **How to handle edge cases?**
   - What if requirements are ambiguous?
   - Should there be fallback to "stay in current level" when uncertain?
   - Confidence threshold for transitions?

4. **Performance considerations?**
   - One LLM call per mental state per turn?
   - Or batch evaluation of all mental states together?
   - Impact on response latency?
