# Memory Data Structures

## Layer 1: Active Episode Structure

### Schema

```yaml
episode_id: string                    # Unique identifier (UUID)
episode_number: integer               # Sequential number (1, 2, 3...)
title: string                         # Human-readable episode name
behavioral_mode: string               # Which mode was active during this episode
timestamp_start: datetime             # When episode began (ISO 8601)
timestamp_end: datetime               # When episode ended (ISO 8601)
duration_exchanges: integer           # Number of user-assistant message pairs

mental_state_trajectory:
  fear:
    start: integer                    # Starting numeric value (0-100)
    end: integer                      # Ending numeric value (0-100)
    start_level: string               # Starting level name (e.g., "Cautious")
    end_level: string                 # Ending level name (e.g., "Panicked")
  trust:
    start: integer
    end: integer
    start_level: string
    end_level: string
  confusion:
    start: integer
    end: integer
    start_level: string
    end_level: string

summary: string                       # 3-5 sentence narrative of what happened

key_moments: list                     # 0-3 verbatim dialogue exchanges
  - exchange_number: integer          # Position in episode (1st, 5th, 12th exchange)
    user_message: string              # Exact user message
    character_response: string        # Exact character response
    why_important: string             # Why this moment was preserved

transition_trigger: string            # Why this episode ended and mode switched

importance_score: integer             # Calculated importance (0-200)
importance_breakdown:                 # How score was calculated
  core_fear_involved: integer         # Points from core fear
  core_need_involved: integer         # Points from core need
  trust_change: integer               # Points from trust change
  fear_change: integer                # Points from fear change
  mode_trigger: integer               # Points for causing mode switch
  first_revelation: integer           # Points for character revelation
  significant_teaching: integer       # Points for user teaching character
  affection_milestone: integer        # Points for physical affection milestone
  deep_question: integer              # Points for existential question
  repetitive_pattern: integer         # Negative points for repetition
  no_state_change: integer            # Negative points for no change

metadata:
  created_at: datetime                # When this memory item was created
  compressed_at: datetime | null      # When moved to Layer 2 (null if still L1)
  protected: boolean                  # If true, never compress (importance override)
  tags: list[string]                  # Custom tags for filtering/search
```

### Field Descriptions

#### episode_id
- **Type:** String (UUID format)
- **Purpose:** Unique identifier for cross-referencing
- **Example:** `"3f8d5e2a-91b4-4c7f-a8d9-1e2b3c4d5e6f"`

#### episode_number
- **Type:** Integer
- **Purpose:** Human-readable sequential identifier
- **Example:** `5` (this is the 5th episode in the character's history)
- **Note:** Never changes, even if earlier episodes are compressed

#### title
- **Type:** String (20-50 characters recommended)
- **Purpose:** Quick reference name for the episode
- **Example:** `"The Storm Night"`, `"Cooking Lesson"`, `"First Gift"`
- **Generation:** Can be LLM-generated or rule-based

#### behavioral_mode
- **Type:** String (enum from character config)
- **Purpose:** Which behavioral mode was active during this episode
- **Example:** `"eager_pup"`, `"devoted_ward"`, `"frightened_orphan"`
- **Validation:** Must match one of the modes defined in character.yaml

#### timestamp_start / timestamp_end
- **Type:** Datetime (ISO 8601 format)
- **Purpose:** Track when episode occurred for temporal context
- **Example:** `"2025-12-25T14:30:00Z"`, `"2025-12-25T15:45:00Z"`

#### duration_exchanges
- **Type:** Integer
- **Purpose:** How many user-assistant message pairs occurred
- **Example:** `15` (user sent 15 messages, character responded 15 times)
- **Note:** Used to calculate episode density/importance

#### mental_state_trajectory
- **Type:** Nested object with three mental states
- **Purpose:** Track how character's emotional state evolved during episode
- **Structure:** Each state has start/end numeric values and level names

**Example:**
```yaml
mental_state_trajectory:
  fear:
    start: 15
    end: 65
    start_level: "Cautious"
    end_level: "Panicked"
  trust:
    start: 10
    end: 35
    start_level: "Observant"
    end_level: "Accepting"
  confusion:
    start: 5
    end: 5
    start_level: "Curious"
    end_level: "Curious"
```

#### summary
- **Type:** String (200-400 words recommended)
- **Purpose:** Narrative overview of what happened in the episode
- **Tone:** Third-person past tense, descriptive
- **Content:** Major events, character actions, environmental context

**Example:**
```
Thunderstorm started while Fen and Alex were in the cabin. Fen panicked at the loud thunder - ears flattened against her head, tail bristled, and she backed into a corner. Alex didn't force her out or approach aggressively, but sat nearby speaking softly. Over the next twenty minutes, Fen gradually calmed. She watched Alex's calm demeanor and eventually crept close, pressing against Alex's leg. Alex stroked her ears gently without sudden movements. Fen fell asleep there, feeling safe for the first time since her mother's disappearance.
```

#### key_moments
- **Type:** List of dialogue exchanges (0-3 items)
- **Purpose:** Preserve verbatim exchanges for emotional continuity
- **Selection criteria:** Highest importance, emotional impact, or character revelation
- **Note:** Can be empty list if episode had no standout moments

**Example:**
```yaml
key_moments:
  - exchange_number: 8
    user_message: "You're okay, Fen. I'm right here."
    character_response: "*whimpering* Too loud... too loud..."
    why_important: "Peak of fear state, vulnerability display"
  
  - exchange_number: 12
    user_message: "I know. But you're safe. I won't let anything hurt you."
    character_response: "*slowly stops shaking, inches closer* ...promise?"
    why_important: "Trust breakthrough moment - first time Fen sought comfort"
  
  - exchange_number: 15
    user_message: "I promise."
    character_response: "*presses against leg, tail slowly relaxes* ...okay. *closes eyes*"
    why_important: "Resolution - trust established, fear overcome"
```

#### transition_trigger
- **Type:** String (100-200 characters)
- **Purpose:** Explain why this episode ended and behavioral mode switched
- **Content:** Specific event or threshold that caused transition

**Example:**
```
"Fear decreased from 65 to 10 due to sustained comfort and safety demonstration. Trust increased from 10 to 35, crossing threshold for devoted_ward mode. Physical comfort-seeking behavior confirmed bond formation."
```

#### importance_score
- **Type:** Integer (typically 0-200 range)
- **Purpose:** Determine compression priority
- **Calculation:** Sum of all importance_breakdown values
- **Usage:** Scores >80 are protected from compression

#### importance_breakdown
- **Type:** Object with individual score components
- **Purpose:** Transparent scoring for debugging and tuning
- **Note:** Each field shows points awarded for that criterion

**Example:**
```yaml
importance_breakdown:
  core_fear_involved: 40        # Abandonment fear was addressed
  core_need_involved: 40        # Affection need was met
  trust_change: 20              # Trust changed by 25 points
  fear_change: 20               # Fear changed by 55 points
  mode_trigger: 50              # This episode caused mode transition
  first_revelation: 0           # No new revelations
  significant_teaching: 0       # No teaching occurred
  affection_milestone: 15       # First time seeking physical comfort
  deep_question: 0              # No existential questions
  repetitive_pattern: 0         # Not repetitive
  no_state_change: 0            # State did change
```
**Total:** 185 points (CRITICAL - protect from compression)

#### metadata
- **Type:** Object with operational metadata
- **Purpose:** Track system operations on this memory item

**Fields:**
- `created_at`: When memory item was created
- `compressed_at`: When moved to Layer 2 (null if still in Layer 1)
- `protected`: Boolean flag - if true, never compress regardless of age
- `tags`: Custom tags for filtering (e.g., `["storm", "trust_milestone", "physical_contact"]`)

---

## Complete Example: Layer 1 Episode

```yaml
episode_id: "a7f8d4e2-c9b1-4f3a-8d7e-5c6b7d8e9f0a"
episode_number: 4
title: "The Storm Night"
behavioral_mode: "eager_pup"
timestamp_start: "2025-12-20T19:30:00Z"
timestamp_end: "2025-12-20T20:15:00Z"
duration_exchanges: 15

mental_state_trajectory:
  fear:
    start: 15
    end: 10
    start_level: "Cautious"
    end_level: "Cautious"
  trust:
    start: 10
    end: 35
    start_level: "Observant"
    end_level: "Accepting"
  confusion:
    start: 5
    end: 8
    start_level: "Curious"
    end_level: "Curious"

summary: |
  A severe thunderstorm began while Fen and Alex were in the cabin. The first loud 
  crack of thunder sent Fen into a panic state - her ears flattened against her skull, 
  tail bristled into a bottlebrush shape, and she scrambled backward into the corner 
  near the fireplace. Her fear spiked to 65 (Panicked state). Alex recognized the panic 
  response and deliberately did not approach or corner Fen. Instead, Alex sat on the 
  floor about six feet away, speaking in a calm, low voice, explaining what thunder was 
  and that the cabin was safe. Over the next twenty minutes, as the storm continued but 
  Alex remained calm, Fen's breathing slowed. She began to watch Alex instead of the 
  windows. Eventually, Fen crept forward, inch by inch, until she was close enough to 
  press against Alex's leg. When Alex slowly raised a hand to stroke her ears, Fen 
  flinched but didn't retreat. The gentle touch, combined with Alex's steady presence, 
  brought Fen's fear back down to baseline. She fell asleep with her head on Alex's 
  knee, feeling genuinely safe for the first time since her mother disappeared. This 
  episode marked a significant trust breakthrough and set the stage for transitioning 
  to devoted_ward mode.

key_moments:
  - exchange_number: 8
    user_message: "You're okay, Fen. I'm right here. It's just noise - it can't hurt you in here."
    character_response: "*whimpering, tail tucked tight* Too loud... too loud... *ears flat against head, eyes wide*"
    why_important: "Peak vulnerability - Fen at maximum fear, displaying complete panic response"
  
  - exchange_number: 12
    user_message: "I know it's scary. But you're safe with me. I won't let anything hurt you."
    character_response: "*stops shaking, looks at Alex instead of window* ...promise? *voice small, barely above whisper*"
    why_important: "Turning point - Fen redirects focus from threat to Alex, seeking reassurance"
  
  - exchange_number: 15
    user_message: "I promise, Fen. You're safe here."
    character_response: "*inches forward, presses against leg, tail slowly begins to relax* ...okay. *eyes close* Stay? *quietly*"
    why_important: "Resolution and trust confirmation - active comfort-seeking behavior, first voluntary physical contact"

transition_trigger: |
  Fear spike was temporarily elevated to 65 (Panicked) during the storm's peak but 
  returned to baseline of 10 through Alex's calm, non-threatening comfort response. 
  Trust significantly increased from 10 to 35 (Observant → Accepting) due to Alex 
  demonstrating safety during Fen's most vulnerable moment. The combination of 
  overcome fear and established trust, plus the first instance of Fen seeking and 
  accepting physical comfort, indicated readiness to transition toward devoted_ward 
  mode. Next episode will likely push trust over 50 threshold.

importance_score: 185

importance_breakdown:
  core_fear_involved: 40          # Loud noise trigger activated core fear
  core_need_involved: 40          # Affection need met through gentle touch
  trust_change: 20                # Trust increased by 25 points
  fear_change: 0                  # Fear spiked then returned to baseline (net: -5)
  mode_trigger: 50                # Set up conditions for mode transition
  first_revelation: 0             
  significant_teaching: 30        # Alex taught Fen about storms and safety
  affection_milestone: 15         # First voluntary physical contact initiated by Fen
  deep_question: 0                
  repetitive_pattern: 0           
  no_state_change: 0              

metadata:
  created_at: "2025-12-20T20:15:00Z"
  compressed_at: null
  protected: true
  tags: 
    - "storm"
    - "trust_milestone"
    - "physical_contact"
    - "fear_overcome"
    - "core_need_affection"
```

---

## Storage Format

**Recommended:** YAML or JSON for human readability and easy LLM generation

**File naming convention:**
- `episode_{episode_number}_{episode_id}.yaml`
- Example: `episode_004_a7f8d4e2.yaml`

**Directory structure:**
```
data/
  characters/
    {character_id}/
      memory/
        layer1/
          episode_001_3f8d5e2a.yaml
          episode_002_9c1b4f7e.yaml
          episode_003_5d6e8a9b.yaml
          episode_004_a7f8d4e2.yaml
        layer2/
          compressed_week1.yaml
        layer3/
          core_facts.yaml
```

---

## Validation Rules

**Required fields:**
- episode_id, episode_number, title, behavioral_mode
- timestamp_start, timestamp_end, duration_exchanges
- mental_state_trajectory (all three states with all subfields)
- summary
- transition_trigger
- importance_score, importance_breakdown
- metadata

**Optional fields:**
- key_moments (can be empty list)

**Constraints:**
- `episode_number` must be positive integer
- `duration_exchanges` must be >= 1
- `importance_score` must equal sum of `importance_breakdown` values
- `timestamp_end` must be after `timestamp_start`
- `behavioral_mode` must exist in character configuration
- Mental state numeric values must be 0-100
- Mental state levels must match character configuration scales

---

## Generation Guidelines

### When to Create Layer 1 Episode

**Trigger:** Behavioral mode switch detected

**Required inputs:**
- Full conversation history since last mode switch
- Character's mental state values at start and end
- Behavioral mode that was active
- Reason for mode transition

### How to Generate Content

**Summary generation:**
- Use LLM with prompt: "Summarize the following conversation as a narrative scene in 3-5 sentences, third-person past tense"
- Include: major events, character emotional journey, environmental context
- Tone: Descriptive, focuses on character's experience

**Key moments selection:**
- Identify 2-3 exchanges with highest emotional impact
- Prioritize: turning points, revelations, first-time behaviors, peak emotions
- Preserve exact wording (don't paraphrase)
- Include character's physical tells and speech patterns

**Title generation:**
- Use LLM with prompt: "Generate a short, evocative title (2-4 words) for this episode"
- OR use rule-based: "[Primary Event] + [Emotional Tone]"
- Examples: "Storm Night", "Cooking Lesson", "First Gift", "Abandonment Fear"

**Importance calculation:**
- Run through scoring algorithm
- Sum all components
- Flag as protected if score >= 80

### Quality Checks

- Summary should be self-contained (readable without seeing dialogue)
- Key moments should include clear emotional content, not just plot
- Transition trigger should be specific (not vague like "things changed")
- Importance score should be justified by breakdown
- Tags should be searchable/filterable concepts
