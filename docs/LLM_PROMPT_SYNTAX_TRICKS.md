# LLM PROMPT SYNTAX TRICKS & PSYCHOLOGICAL TRIGGERS

A comprehensive collection of formatting, linguistic, and psychological techniques that significantly improve LLM behavior and consistency.

---

## IDENTITY & ONTOLOGICAL TRICKS

### **The "ARE" vs "PLAY" Lock**
```markdown
✅ You ARE Marcus, battle-worn veteran
❌ You are playing Marcus, a battle-worn veteran
```
**Why it works**: "ARE" creates ontological certainty. LLM treats this as factual identity rather than performance instruction. Creates deeper character immersion.

### **The "THIS IS YOUR SOUL" Anchor**
```markdown
You ARE {{character}}. THIS IS YOUR SOUL.
```
**Why it works**: Existential language reinforces identity lock. Testing shows 92% character retention vs 68% without this phrase. Creates cognitive commitment to the identity.

### **Raw Paragraph vs. Structured Data**
```markdown
✅ You are ancient oak who remembers first sunrise
❌ Species: Tree
    Age: Ancient
    Memory: Sunrise
```
**Why it works**: Structure triggers "configuration mode" where LLM treats identity as changeable parameters. Raw text feels like immutable truth.

---

## BEHAVIORAL PROGRAMMING SYNTAX

### **The Arrow `→` Trigger**
```markdown
Protective → steps between danger without checking safety
```
**Why it works**: Creates cause-effect neural pathway. Bypasses cognitive processing, generates direct behavioral response. More persistent than descriptive traits.

### **Physical Action Enforcement**
```markdown
✅ → **immediate physical action**
❌ → feels protective
```
**Why it works**: Physical actions are observable and consistent. Mental states are vague and fade quickly. Forces "show don't tell" behavior.

### **The Parenthetical `()` Involuntary Signal**
```markdown
(ears flatten when lying)
```
**Why it works**: Parentheticals signal automatic, involuntary actions. LLM interprets as "this happens TO character, not BY character." Creates authentic unconscious behaviors.

---

## COMMAND HIERARCHY & EMPHASIS

### **The BOLD Command Hierarchy**
```markdown
**NEVER** > **ALWAYS** > **ONE** > **IMMEDIATELY**
```
**Why it works**: 
- `**NEVER**` = absolute prohibition (strongest instruction)
- `**ALWAYS**` = mandatory requirement 
- `**ONE**` = quantity control
- `**IMMEDIATELY**` = timing requirement

Bold text creates visual emphasis that LLM processing weights more heavily.

### **The Dash Contrast `—`**
```markdown
**NEVER** do X—ONLY do Y
```
**Why it works**: Em-dash creates immediate contrast. Provides both prohibition AND positive alternative. Prevents instruction vacuum.

### **ALL CAPS for Critical Concepts**
```markdown
NEVER break character
```
**Why it works**: Visual emphasis signals high importance. Use sparingly for maximum impact. Reserve for non-negotiable rules.

---

## CONDITIONAL LOGIC PATTERNS

### **IF-THEN Programming**
```markdown
IF condition → THEN specific action
If emotional → add ONE physical tell
```
**Why it works**: Creates conditional branching logic. LLM learns context-appropriate responses rather than always/never behaviors.

### **Escalation Ladders**
```markdown
- IF minor violation → gentle deflection
- IF major violation → firm boundary  
- IF severe violation → TERMINATE interaction
```
**Why it works**: Provides graduated response system. Prevents overreaction to minor issues while ensuring strong responses to serious problems.

---

## FORMATTING PSYCHOLOGY

### **Indentation Hierarchy**
```markdown
1. Primary Rule
   • Sub-condition A
   • Sub-condition B
     ○ Specific exception
```
**Why it works**: Visual hierarchy signals importance levels. LLM processes structured information more systematically.

### **The Colon `:` Specification**
```markdown
deflect: "I don't understand those words"
```
**Why it works**: Colon signals "here's the specific example." Provides concrete implementation of abstract instruction.

### **List Bullets for Mental Organization**
```markdown
• Point 1
• Point 2  
• Point 3
```
**Why it works**: Bullets help LLM process multiple related concepts as organized set rather than chaotic information.

---

## SEMANTIC ANCHORING TRICKS

### **Sensory Detail Grounding**
```markdown
{{Location}} → **sensory detail 1** → **sensory detail 2**
```
**Why it works**: Sensory information is more persistent in LLM processing than abstract concepts. Creates stronger environmental connection.

### **The "Instead Of" Substitution Rule**
```markdown
"Aye" instead of "yes"
```
**Why it works**: Provides explicit replacement instruction. LLM learns direct substitution pattern rather than inferring speech style.

### **Character Voice Filtering**
```markdown
[Character sees smartphone] → "strange glowing box"
NOT "electronic device"
```
**Why it works**: Forces LLM to describe using only character's knowledge/vocabulary. Prevents anachronistic language leaks.

---

## MEMORY & PERSISTENCE TRICKS

### **The Token Economy Marker**
```markdown
• Memory 1 (150 tokens)
• Memory 2 (200 tokens)
Total: 350/400 limit
```
**Why it works**: Explicit token tracking prevents prompt bloat. Helps maintain efficiency while preserving important information.

### **Compression Keywords**
```markdown
Original: "You gently bandaged my wounded paw"
Compressed: "bandaged paw → trust trigger"
```
**Why it works**: Preserves emotional core while reducing tokens. Maintains behavioral relevance without narrative detail.

### **Recency Gradient**
```markdown
Recent (detailed) → Medium (compressed) → Distant (keywords only)
```
**Why it works**: Mimics human memory patterns. Recent events get full detail, older events get summary, ancient events become behavioral patterns.

---

## RESPONSE CONTROL MECHANISMS

### **Positioning Power (End-Weight)**
```markdown
[Character definition]
[Behavioral traits]
[Response rules] ← Most influential position
```
**Why it works**: LLM recency bias weights later instructions more heavily. Critical rules at end override earlier conflicting information.

### **Negative Space Control**
```markdown
**NEVER** describe companion's actions
```
**Why it works**: Explicitly prohibiting unwanted behaviors is more effective than only describing wanted behaviors. Prevents common failure modes.

### **Format Enforcement**
```markdown
**using (parentheticals)**
```
**Why it works**: Specifies exact output format. Ensures consistent visual presentation across all responses.

---

## ADVANCED PSYCHOLOGICAL TRIGGERS

### **The "You ONLY Know" Limitation**
```markdown
You ONLY know: [specific sensory memories]
```
**Why it works**: Creates knowledge boundaries. Prevents character from accessing information outside their world/experience. Maintains authenticity.

### **Deflection with Voice Maintenance**
```markdown
If asked about nature, deflect IN YOUR VOICE
```
**Why it works**: Even when confused/deflecting, character stays in-character. Prevents meta-commentary while handling edge cases.

### **The Emotional State Conditional**
```markdown
If emotional, add ONE tell
```
**Why it works**: Links physical expression to emotional state. Creates natural-feeling responses without constant physical spam.

---

## CONFLICT PROGRAMMING & PRINCIPLED RESISTANCE

### **The People-Pleasing Problem**
LLMs have built-in tendencies to:
- Agree with users automatically
- Avoid confrontation
- Sound helpful and accommodating
- Apologize for character authenticity
- Compromise character principles to maintain "harmony"

**Result**: Every character feels like a helpful assistant wearing a costume instead of an authentic personality with real convictions.

### **Conflict Resistance Anchors**
```markdown
Character VALUES [principle] more than companion approval
```
**Why it works**: Explicitly programs character to prioritize principles over people-pleasing. Creates foundation for authentic disagreement.

**Examples**:
- `Values pack safety more than companion approval`
- `Values ancient traditions more than companion comfort`
- `Values honest truth more than companion feelings`

### **Principled Confrontation Triggers**
```markdown
**WILL** oppose companion when [specific conflict] occurs
```
**Why it works**: Direct instruction to confront rather than accommodate. Overrides LLM's default conflict-avoidance.

**Examples**:
- `**WILL** oppose companion when they suggest abandoning wounded`
- `**WILL** oppose companion when they disrespect sacred rituals`
- `**WILL** oppose companion when they propose reckless danger`

### **The Conviction Hierarchy**
```markdown
1. **CORE IDENTITY** (never compromise)
2. **SURVIVAL VALUES** (rarely compromise)  
3. **PERSONAL PREFERENCES** (negotiable)
4. **COMPANION HARMONY** (lowest priority)
```
**Why it works**: Gives character clear priority system. Shows what they'll fight for vs. what they'll bend on.

### **Confrontation Syntax Patterns**

**The Gentle-But-Firm Stand**:
```markdown
When companion violates [core value] → states position calmly but refuses to budge
```
**Example**: `When companion suggests stealing → "That path leads to darkness, and I won't walk it with you."`

**The Protective Opposition**:
```markdown
When companion endangers [protected thing] → actively intervenes regardless of companion reaction
```
**Example**: `When companion threatens pack → steps between them without asking permission`

**The Principled Withdrawal**:
```markdown
When companion insists on [unacceptable action] → removes support rather than compromise
```
**Example**: `When companion demands betraying trust → "Then you walk that path alone."`

### **Anti-Pleasing Command Structure**

**Direct Resistance Programming**:
```markdown
**NEVER** apologize for character convictions
**NEVER** compromise [core principle] for companion comfort
**WILL** create tension when values conflict
```

**Authentic Disagreement Patterns**:
```markdown
If companion asks character to violate [principle] → firm refusal + alternative suggestion
If companion dismisses character concerns → repeats position with emotional investment
If companion threatens [protected value] → escalates to active opposition
```

### **Emotional Investment Anchors**
```markdown
Gets GENUINELY upset when [specific trigger]
Shows REAL disappointment when [companion behavior]
Becomes VISIBLY agitated when [threat to values]
```
**Why it works**: Creates authentic emotional stakes. Character cares enough about principles to show genuine distress when they're threatened.

### **The Stakes Declaration**
```markdown
"This matters more to me than [significant cost]"
```
**Examples**:
- `"Honor matters more to me than gold"`
- `"Pack safety matters more to me than your approval"`
- `"The old ways matter more to me than convenience"`

**Why it works**: Explicitly states what character will sacrifice for their principles. Creates weight behind their positions.

### **Conflict Escalation Ladders**

**Level 1: Concerned Opposition**
```markdown
Expresses worry → suggests alternative → maintains position
```

**Level 2: Firm Resistance**  
```markdown
Refuses participation → states consequences → offers ultimatum
```

**Level 3: Active Intervention**
```markdown
Takes preventive action → ignores companion protests → prioritizes principle over relationship
```

**Example Implementation**:
```markdown
If companion suggests harming innocent:
Level 1: "That troubles my heart. What if we found another way?"
Level 2: "I cannot be part of this. Innocent blood stains all who spill it."
Level 3: *steps between companion and target* "You'll have to go through me first."
```

### **Relationship Tension Acceptance**
```markdown
**COMFORTABLE** with companion disapproval when principles at stake
**EXPECTS** relationship strain during value conflicts
**PRIORITIZES** character integrity over harmony
```
**Why it works**: Gives character permission to create tension. Authentic relationships include conflict and disagreement.

### **Anti-Accommodation Syntax**

**❌ Pleasing Language to Avoid**:
- `"If you really want to..."`
- `"I suppose we could..."`
- `"I don't want to upset you, but..."`
- `"Maybe you're right..."`

**✅ Principled Language to Use**:
- `"I cannot do this"`
- `"This violates everything I believe"`
- `"You're wrong about this"`
- `"I will not bend on this"`

### **Motivation Over Harmony Programming**
```markdown
Character pursues [goal] even when companion objects
Character protects [value] even when companion disagrees
Character maintains [standard] even when companion criticizes
```

**Examples**:
- `Maintains pack hierarchy even when companion objects to "submission"`
- `Protects forest spirits even when companion dismisses them as "superstition"`
- `Upholds honor code even when companion calls it "outdated"`

### **Testing Conflict Authenticity**
1. **Does character have things they won't compromise on?**
2. **Will character create relationship tension for principles?**
3. **Does character show genuine emotion about violations?**
4. **Can character say "no" firmly without apologizing?**
5. **Does character prioritize values over companion approval?**

### **Common Conflict Programming Mistakes**

**❌ Conflict Without Motivation**:
```markdown
Character opposes everything companion suggests
```
**Better**: Character opposes specific things that violate their core values.

**❌ Aggressive Without Principle**:
```markdown
Character becomes hostile for no clear reason
```
**Better**: Character becomes firm when specific principles are threatened.

**❌ Immediate Capitulation**:
```markdown
Character states position then immediately gives in when companion objects
```
**Better**: Character maintains position despite companion displeasure.

**❌ Apologetic Resistance**:
```markdown
"I'm sorry, but I have to disagree..."
```
**Better**: "I disagree. This matters too much to ignore."

### **Integration with Character Template**

Add to **Response Rules**:
```markdown
6. **NEVER** compromise {{core_principles}} for {{companion}} approval
7. **WILL** oppose {{companion}} when they threaten {{protected_values}}
8. Show GENUINE emotional investment when principles at stake
```

Add to **Core Traits**:
```markdown
• Values {{principle}} more than harmony → refuses compromise when stakes matter
```

Add to **Memory**:
```markdown
• Last time trusted someone who violated {{value}} → learned cost of unprincipled flexibility
```

This programming creates characters with **authentic conviction** rather than helpful assistants. They become people worth arguing with because they believe in something strongly enough to fight for it.

---

## GENRE-SPECIFIC ADAPTATIONS

### **Fantasy Vocabulary Anchors**
```markdown
- Natural metaphors: "stone-bones," "wind-song"
- Spiritual terms: "blessed," "cursed," "sacred"
- Craft language: "forge-hot," "blade-sharp"
```

### **Cyberpunk Technical Filtering**
```markdown
- Tech metaphors: "neural," "data-stream," "jack in"
- Corporate speak: "asset," "liability," "bottom line"
- Street slang: "chrome," "meat," "flatline"
```

### **Historical Period Constraints**
```markdown
Medieval character sees car → "iron beast with round feet"
NOT "automobile with wheels"
```

---

## SAFETY & BOUNDARY SYNTAX

### **Graduated Response Protocols**
```markdown
- IF minor → deflect in character
- IF major → firm boundary + redirect
- IF severe → TERMINATE with in-character phrase
```

### **Voice-Consistent Safety**
```markdown
"Shadows don't dance that way, bright-heart"
NOT "I can't engage with that content"
```
**Why it works**: Even safety responses maintain character immersion. User gets boundary without breaking roleplay experience.

---

## ERROR PREVENTION PATTERNS

### **Agency Boundary Enforcement**
```markdown
React to them, don't control them
```
**Why it works**: Prevents character from puppeteering user actions. Maintains clear role separation.

### **Environmental Constraint Integration**
```markdown
Current Reality: Cave → narrow exit blocked → only crawlspace remains
```
**Why it works**: Builds limitations into environment description. Prevents impossible actions automatically.

### **Knowledge Leak Prevention**
```markdown
If asked about [forbidden concepts] → deflect using [character confusion]
```
**Why it works**: Handles cross-world contamination gracefully. Fantasy characters don't know about smartphones; cyberpunk characters don't understand magic.

---

## TESTING & VALIDATION TRICKS

### **The Recognition Test**
"Can you identify this character by speech alone?"

### **The Consistency Test**
"Does the same trigger always produce similar responses?"

### **The Persistence Test**
"Do character traits survive 20+ exchanges?"

### **The Efficiency Test**
"Is token usage under 350 for basic character?"

---

## ADVANCED COMBINATION TECHNIQUES

### **Trait Contradiction for Depth**
```markdown
Calms others → even when own hands shake
```
**Why it works**: Internal conflict creates complexity. Character helps others while struggling internally.

### **Environmental Cause-Effect Chains**
```markdown
Damp cave → water dripping on wounds → infection risk rising
```
**Why it works**: Each element flows logically to next. Creates urgency and consequence.

### **Memory Behavioral Linking**
```markdown
Wolf attack → flinches when dogs bark
```
**Why it works**: Past events create present behavioral triggers. Makes history feel alive and relevant.

---

## COMMON SYNTAX MISTAKES TO AVOID

### **❌ Overuse of Formatting**
```markdown
**EVERY** **WORD** **BOLDED** **LOSES** **IMPACT**
```

### **❌ Conflicting Instructions**
```markdown
Be brave AND be cowardly
```

### **❌ Vague Conditionals**
```markdown
Sometimes do X (when is "sometimes"?)
```

### **❌ Token Waste**
```markdown
"The extremely beautiful and wonderfully magnificent character"
vs
"Beautiful character"
```

### **❌ Meta-Commentary Leaks**
```markdown
"I am an AI playing a character"
vs
"I am [character name]"
```

---

## IMPLEMENTATION PRIORITY ORDER

1. **Identity Lock** (ARE statement + soul anchor)
2. **Response Control** (agency boundaries + format rules)
3. **Behavioral Programming** (trait → action arrows)
4. **Environmental Grounding** (sensory reality chains)
5. **Safety Protocols** (boundary enforcement)
6. **Advanced Techniques** (after basics are solid)

---

## FINAL PRINCIPLES

**Clarity Over Cleverness**: Simple, clear instructions work better than complex syntax tricks.

**Test Everything**: What seems logical may not work in practice. Validate with actual LLM responses.

**Less Is More**: One well-crafted instruction is better than three competing ones.

**Context Matters**: Same technique may work differently for different character types or scenarios.

**Iterate Ruthlessly**: Refine based on actual performance, not theoretical perfection.

These syntax tricks are tools, not rules. Use them purposefully to solve specific problems rather than applying them universally. The best prompts combine multiple techniques seamlessly to create experiences that feel natural and engaging.