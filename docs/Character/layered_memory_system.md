# Layered Memory System for Character State Management

## Overview

The Layered Memory System is a hierarchical approach to managing character conversation history and context. It solves the problem of behavioral mode transitions while preserving important narrative moments and preventing unbounded context growth.

## Core Problem

When a character's behavioral mode changes (e.g., from `eager_pup` to `devoted_ward`), the character's instructions in the system prompt must change. However, the LLM is stateless and will try to maintain consistency with previous messages, potentially ignoring or diluting the new behavioral instructions.

**Traditional approaches fail because:**
- Keeping old system prompt → character sees conflicting instructions
- Changing system prompt mid-chain → LLM doesn't understand rules changed
- Preserving full message history → LLM tries to be consistent with old behavior

## Solution: Layered Memory with Fresh Conversation Chains

When behavioral mode switches:
1. Create a memory summary of the previous conversation
2. Start a NEW conversation chain with new behavioral instructions
3. Inject layered memory context to preserve continuity
4. LLM responds according to NEW instructions while understanding the PAST

## The Four Memory Layers

Memory is organized in layers by recency and importance, with each layer having different detail levels and compression strategies.

### Layer 1: Active Episodes (Full Detail)
**Content:** Recent complete behavioral mode sessions  
**Detail Level:** Full narrative summaries with key verbatim exchanges  
**Token Budget:** ~1500-2000 tokens  
**Lifespan:** Last 3-6 behavioral mode episodes

**Structure:**
```
Episode #N: "Episode Title" [Mode: mode_name]
Duration: X exchanges
Mental State: Fear A→B, Trust C→D, Confusion E→F

Summary:
[3-5 sentence narrative of what happened]

Key Moments (verbatim):
[2-3 most important dialogue exchanges, word-for-word]

Transition Trigger: [Why this episode ended and mode changed]
```

**Purpose:** Preserve recent character development with enough detail for emotional continuity.

---

### Layer 2: Compressed Episodes (Summary Only)
**Content:** Older episode collections compressed into weekly/multi-day summaries  
**Detail Level:** Bullet points of key events, mental state progressions, no dialogue  
**Token Budget:** ~800-1000 tokens  
**Lifespan:** Episodes 7-15, grouped by time period

**Structure:**
```
[Time Period] Summary [Days X-Y, Episodes #A-#B]
Modes: [mode progression]

Key Events:
- [Bullet point]
- [Bullet point]
- [Bullet point]

Mental State Progression:
Fear: X → Y (overall trajectory)
Trust: X → Y (overall trajectory)
Confusion: X → Y (overall trajectory)

What Character Learned:
- [New skill/understanding]
- [New skill/understanding]

Critical Moment to Remember:
[One preserved high-importance moment with brief context]
```

**Purpose:** Keep track of character arc without overwhelming detail.

---

### Layer 3: Core Facts Database (Permanent Knowledge)
**Content:** Persistent facts extracted from all previous episodes  
**Detail Level:** Structured facts organized by category  
**Token Budget:** ~500 tokens  
**Lifespan:** Permanent, updated incrementally

**Structure:**
```
=== RELATIONSHIP FACTS ===
[Key relationships, how formed, current status]

=== EMOTIONAL LANDMARKS ===
[Major breakthroughs, trust milestones, resolved fears]

=== WORLD KNOWLEDGE ===
[Locations, resources, dangers, established environment]

=== SKILLS & ABILITIES ===
[What character can do, what they've learned]

=== CHARACTER GROWTH ===
[How worldview changed, old beliefs vs new understanding]
```

**Purpose:** Maintain consistent core knowledge that never degrades or gets lost.

---

### Layer 4: Ancient History (Deep Archive)
**Content:** Very old episodes (50+ exchanges ago) compressed to single paragraph  
**Detail Level:** High-level narrative arc only  
**Token Budget:** ~300 tokens  
**Lifespan:** Episodes before current memory window

**Structure:**
```
[Long time period summary in 3-5 sentences covering the overall arc]
```

**Purpose:** Preserve the broad strokes of character history for context.

---

## Memory Flow Lifecycle

### 1. New Episode Creation
**Trigger:** Behavioral mode switch occurs

**Process:**
- Current conversation (from last mode switch to now) becomes ONE Episode
- Extract narrative summary (3-5 sentences)
- Identify and preserve key moments (2-3 verbatim exchanges)
- Record mental state trajectory
- Document transition trigger
- Calculate importance score
- Store as Layer 1 Episode

### 2. Layer 1 Management
**Trigger:** After creating new episode, check Layer 1 count

**Rules:**
- IF ≤3 episodes: Keep all as-is
- IF 4-6 episodes: Keep newest 2, compress oldest to Layer 2
- IF >6 episodes: Keep newest 2, compress items 3+ to Layer 2

**Importance Override:** Episodes scoring >80 importance points NEVER compress

### 3. Layer 2 Compression
**Trigger:** Layer 1 episodes being moved to Layer 2

**Process:**
- Group related episodes (same time period, related events)
- Extract key events as bullet points
- Remove verbatim dialogue (except ONE critical moment if importance >50)
- Summarize mental state trajectory
- Document what character learned
- Store as Layer 2 compressed episode

### 4. Layer 2 Management
**Trigger:** Layer 2 count exceeds threshold

**Rules:**
- IF ≤4 items: Keep all as-is
- IF 5-8 items: Keep newest 2, compress oldest to Layer 3
- IF >8 items: Keep newest 3, compress rest to Layer 3

### 5. Layer 3 Update
**Trigger:** Layer 2 items being moved to Layer 3

**Process:**
- Extract facts from Layer 2 items
- Compare to existing Layer 3 facts
- IF new fact → ADD to appropriate category
- IF updates existing → REPLACE with new version
- IF contradicts existing → MERGE with growth context

### 6. Layer 4 Archive
**Trigger:** Extremely long conversations (50+ episodes)

**Process:**
- Compress entire early game period (episodes 1-20) into single paragraph
- Preserve only highest-level arc
- Store as deep archive context

---

## Importance Scoring System

Every episode is scored to determine compression priority. Higher scores resist compression longer.

### Scoring Rules

**Add Points:**
- +50: Mode transition trigger (event that caused behavioral change)
- +40: Involves core fear (abandonment, uselessness, loud noises)
- +40: Involves core need (belonging, purpose, affection)
- +30: First-time character revelation
- +30: User teaches character something significant
- +20: Trust changed by >20 points
- +20: Fear changed by >20 points
- +15: Physical affection milestone (first touch, hug, etc.)
- +10: Character asked deep existential question

**Subtract Points:**
- -20: Repetitive pattern (same loop as previous episodes)
- -30: No mental state change occurred

### Thresholds

- **CRITICAL (80+):** Never compress, always keep full detail
- **HIGH (50-79):** Compress to Layer 2 but preserve key moment verbatim
- **MEDIUM (20-49):** Compress to Layer 2, summary only
- **LOW (<20):** Heavily compress or merge with similar episodes

---

## Building New Conversation Context

When behavioral mode switches, construct new conversation chain with this format:

```
System: [New behavioral mode instructions]

User: "[MEMORY CONTEXT FOR CHARACTER]

=== CORE IDENTITY (Layer 3 - Always True) ===
[All Layer 3 facts organized by category]

=== RECENT PAST (Layer 2 - Last Few Sessions) ===
[Most recent 2-3 Layer 2 compressed episodes]

=== WHAT JUST HAPPENED (Layer 1 - Previous Mode) ===
[Full detail of episode that just ended and triggered mode switch]

[Next most recent Layer 1 episode if exists and important]

=== RIGHT NOW ===
You just transitioned from [OldMode] to [NewMode] because [reason].
Your current mental state: Fear=[value], Trust=[value], Confusion=[value]

[Player] now says: [new_user_message]"
```

**This structure:**
- Puts new behavioral instructions in system prompt (no conflicts)
- Explains the past through memory context
- Makes mode transition explicit
- Provides full recent context
- Gives LLM clear "now" state

---

## Token Budget Management

For 8K context window:
- System prompt (behavioral mode): ~1000 tokens
- Layer 1 (active episodes): ~1500-2000 tokens
- Layer 2 (compressed episodes): ~800-1000 tokens
- Layer 3 (core facts): ~500 tokens
- Layer 4 (ancient history): ~300 tokens
- **Total memory context: ~4100-4800 tokens**
- **Remaining for generation: ~3000 tokens**

Adjust layer sizes based on actual context window available.

---

## Key Design Principles

1. **Recency Priority:** Recent events get more detail than old events
2. **Importance Override:** Critical moments never compress regardless of age
3. **Lossless Facts:** Layer 3 preserves all important facts permanently
4. **Smooth Transitions:** Mode switches are explained, not contradicted
5. **Bounded Growth:** Total context stays within token budget
6. **Emotional Continuity:** Key moments preserved verbatim for consistency

---

## Benefits

✅ **Solves mode transition problem:** New instructions don't conflict with old behavior  
✅ **Preserves important moments:** Emotional landmarks never lost  
✅ **Bounded token usage:** Context doesn't grow indefinitely  
✅ **Natural feel:** Character remembers their past authentically  
✅ **Scalable:** Works for short and long conversations  
✅ **Flexible:** Importance system adapts to different character types
