# History Data Structure
History is a collection of entries that document interactions between users and characters. Each entry captures the details of a specific interaction, including the author, content, and scene descriptions from multiple perspectives.
```yaml
- id: string                # Unique identifier for the entry
  author_id: string         # Identifier for the author (user or character)
  author_type: string       # Type of author ('user' or 'character')
  author_name: string       # Display name of the author
  content: string           # The main content of the entry
  scene_description:        # Descriptions related to the scene
    companion_side: string      # Description from the companion's perspective
    character_side: string      # Description from the character's perspective
    environmental_context: string # Description of the environment/context
```
