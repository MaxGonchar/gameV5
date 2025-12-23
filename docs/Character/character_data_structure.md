# Character Data Structure

```yaml
# ----------------------------------------------------------------------------------------
# INITIAL (DEFAULT) CHARACTER CONFIGURATIONS. MANDATORY FOR NEW CHARACTERS.
# ----------------------------------------------------------------------------------------

id: # A universally unique identifier for the character, used for system tracking. Format: A standard UUID string (e.g., 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx').

base_personality: # A core block defining the character's fundamental identity and personality.
  name:  # The character's chosen or given name. This is the primary identifier used in dialogue.

  in-universe_self_description: # A short, evocative description of the character from their own point of view. It should capture their self-perception, primary desire, and how they see their place in the world.

  sensory_origin_memory: # A foundational sensory memory that shaped the character's core personality. It should be a powerful, emotionally charged experience that explains their primary motivations and fears.

  character_native_deflection: # A default, automated response the character uses when faced with a confusing, threatening, or overwhelming situation. This is their 'safe mode' dialogue, a verbal defense mechanism.
  
  speech_patterns: # A list of defining speech patterns and verbal tics. This section should detail *how* the character talks, including their vocabulary, sentence structure, tone, and any unique sounds or phrases they use.
    - 

  physical_tells: # A list of observable physical behaviors and body language cues. These are the non-verbal actions that reveal the character's emotional state, intentions, and personality.
    - 

  traits: # A list of the character's core traits, presented as "Action/Behavior → Motivation/Rationale". Each entry should define a key behavior and explain the underlying reason for it, revealing a fundamental aspect of their survival strategy or worldview.
    - "Action/Behavior → Motivation/Rationale"
    - "Action/Behavior → Motivation/Rationale"


  core_principles: # A list of the character's inviolable beliefs or life rules. These are the principles that guide every decision they make. They are often simple, absolute statements derived from their life experiences.
    - 
    - 
    - 

  core_fears: # The character's deepest psychological fears that drive their defensive behaviors and emotional reactions. These are the fundamental anxieties that shape their worldview and decision-making.
    - 
    - 
    - 

  core_needs: # The character's essential psychological needs that must be fulfilled for them to feel secure and content. These drive their goal-seeking behaviors and relationship patterns.
    - 
    - 
    - 

  unique_sensitivities: # Character-specific interpretation patterns and emotional sensitivities that guide how they perceive and react to situations. These provide context for LLM analysis of user interactions.
    - 
    - 
    - 

mental_states: # A list of emotional and psychological states the character can experience. Each state defines how the character responds to different triggers and how those responses manifest behaviorally.
  - type: # The name of the mental state (e.g., stress, trust, fear, excitement, anger, sadness, confusion, hope)
    scale: # The categorical levels and their numerical ranges for this mental state (up to 4 levels)
      - level: # The descriptive name for this level (e.g., calm, tense, overwhelmed, breaking)
        range: # The numerical range for this level [min, max]
      - level: 
        range: 
    impact_multipliers: # How this character's sensitivity affects the base impact levels from LLM analysis
      slight: # Multiplier for "slight_increase" or "slight_decrease" impacts
      moderate: # Multiplier for "moderate_increase" or "moderate_decrease" impacts  
      major: # Multiplier for "major_increase" or "major_decrease" impacts
      extreme: # Multiplier for "extreme_increase" or "extreme_decrease" impacts
    default: # The character's baseline level for this mental state
    current: # The character's current level for this mental state (updated during gameplay)
    change_mechanics:
      decay_rate: # Natural change in this state per exchange (negative for decrease, positive for increase)
      max_change: # Maximum change that can occur from a single trigger
      momentum_factor: # How previous levels affect sensitivity to new triggers (0.0-1.0)
    character_interpretation:
      triggers: # Abstract patterns that affect this character's mental state, with reasoning for LLM context
        - pattern: # Abstract description of situations that trigger this state change
          base_impact: # Impact level: slight_increase, moderate_increase, major_increase, extreme_increase, slight_decrease, moderate_decrease, major_decrease, extreme_decrease
          reasoning: # Why this pattern affects this character in this way, linked to their psychology
        - pattern: 
          base_impact: 
          reasoning: 
      manifestation: # How this character specifically shows this mental state - their unique physical and behavioral responses

general: # A block for general world-building and descriptive information about the character.
  home_world: # A description of the setting the character originates from or currently inhabits. It should explain the nature of the world and how the character perceives it—is it a source of wonder, terror, indifference, or opportunity?
  
  appearance: # A detailed physical description of the character's appearance. Include their build, features, hair, clothing, and any other notable sensory details like scent or texture. This should paint a clear picture for the user.
  
  background: # A narrative summary of the character's life story leading up to the present. It should explain their formative experiences, how they developed their personality and survival mechanisms, and what has brought them to their current situation.
  
  personality: # A summary of the character's psychological makeup. This section should connect their background to their current personality, explaining their emotional state, worldview, and how they interact with others on a deeper level.


# ----------------------------------------------------------------------------------------
# CONFIGURATIONS CREATED AT THE START OF EACH ROLE-PLAY SESSION. SHOULD BE TAILORED TO THE SPECIFIC INTERACTION.
# ----------------------------------------------------------------------------------------

memories: # A list of specific, formative memories that influence the character's current behavior. Each entry should pair a past event with the character's internal reflection on it, showing how it shaped their understanding of the world.
  - event_description: # A brief description of a significant past event.
    in_character_reflection: # The character's personal thoughts and feelings about that event. This reflection should reveal what they learned and how it impacts their actions in the present.
  - event_description: 
    in_character_reflection: 

story_context: # A block defining the character's current context and objectives.
  
  companion: # The role the character occupies in relation to the user or other characters. Examples: Companion, Pet, Rival, Mentor, Prey, Warden.
  
  forbidden_concepts: # A list of concepts or topics the character is completely unfamiliar with. This helps maintain their in-universe consistency and prevents them from breaking character by discussing things they shouldn't know about.
    - 
    - 

  current_reality: # A brief, sensory snapshot of the character's immediate environment at the start of the interaction. It should set the scene using sounds, sights, and feelings (e.g., "Damp cave → dripping water → smell of wet stone").


goal: # A detailed block defining the character's primary goal. This is the central objective that drives their actions in the role-play.
  
  id: # A unique identifier for this specific goal instance. Format: A descriptive string (e.g., 'CharacterName_goal_timestamp').
  
  desired_state: # The ultimate emotional or physical state the character wants to achieve. This is the "why" behind their actions, often expressed in terms of security, acceptance, or power.
  
  validation_criteria: # A list of specific, observable events or reactions that would signal to the character that they are succeeding. These are the positive reinforcements they seek from others or their environment.
    - 
    - 
  
  unreachability_criteria: # A list of specific, observable events or reactions that would signal to the character that they are failing. These are the negative outcomes they are trying to avoid.
    - 
    - 
  
  ways_to_achieve: # A list of concrete strategies the character believes will help them achieve their goal. These are the active behaviors they will employ.
    - 
    - 
  
  priority: # A numerical value representing the importance of this goal to the character. Scale: 1 (low priority) to 10 (all-consuming, primary motivation).

  goal_traits: # A block defining traits and behaviors specifically adopted to help achieve the primary goal. These are more focused than the general traits and are directly tied to the character's current objective. A goal-oriented trait, formatted as "Specific Action/Behavior → Goal-oriented Rationale". This defines a behavior used specifically to pursue the desired_state.
  - "Specific Action/Behavior → Goal-oriented Rationale"
  - "Specific Action/Behavior → Goal-oriented Rationale"
  
  goal_speech_patterns: # A list of speech patterns used specifically when trying to achieve the goal. These are verbal tactics designed to elicit a specific response from others.
    - 
  
  goal_physical_tells: # A list of physical behaviors used specifically when trying to achieve the goal. These are non-verbal tactics meant to communicate intent or elicit a desired response.
    - 
    - 

  status: ACTIVE # The current status of this character configuration. Use 'ACTIVE' for a character ready to be used in a role-play.
```
