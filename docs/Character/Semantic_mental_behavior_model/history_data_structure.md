# History Data Structure
History is a collection of entries that document interactions between users and characters. Each entry captures the details of a specific interaction, including the author, content, and scene descriptions from multiple perspectives.
```yaml
- id: string                # Unique identifier for the entry
  author_id: string         # Identifier for the author (user or character)
  author_type: user       # Type of author ('user' or 'character')
  author_name: string       # Display name of the author
  content: string           # The main content of the entry
  scene_description:        # Descriptions related to the scene
    companion_side: string      # Description from the companion's perspective
    character_side: string      # Description from the character's perspective
    environmental_context: string # Description of the environment/context
- id: string                # Unique identifier for the entry
  author_id: string         # Identifier for the author (user or character)
  author_type: bot       # Type of author ('user' or 'character')
  author_name: string       # Display name of the author
  content: string           # The main content of the entry
  scene_description:        # Descriptions related to the scene
    companion_side: string      # Description from the companion's perspective
    character_side: string      # Description from the character's perspective
    environmental_context: string # Description of the environment/context
  emotional_shift:
    mental_states:        # Changes in mental states resulting from the interaction
      <state_name_1>:     # Name of the mental state (e.g., "Security", "Trust", "Longing")
        before_level: string     # Description of the mental state before the interaction (e.g., "Low", "Medium", "High")
        after_level: string   # Description of the mental state after the interaction (e.g., "Low", "Medium", "High")
        reasoning: string   # Explanation of why the mental state changed or why it remained the same based on the content of the interaction and the context
      <state_name_2>:
        before_level: string
        after_level: string
        reasoning: string
      <state_name_3>:
        before_level: string
        after_level: string
        reasoning: string
```
