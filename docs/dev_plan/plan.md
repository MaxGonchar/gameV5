# Features

## new character prompt template
- [x] develop new character prompt template
- [ ] develop a prompts helping user to crete a character
- [ ] develop new scene description prompt template
  - [ ] it should generate scene description for user and for character separately
- [ ] develop new memory generation prompt template
  - [ ] for now let it stores predefined amount of memory items cutting the oldest ones
  - [ ] later it should be able to summarize old memories
- [ ] develop new character data structure
- [ ] implement new character prompt builder
- [ ] integrate new prompt templates and prompt builder into the main codebase

### post implementation:
- [x] story with no history problem
- [ ] solve todos
- [ ] sanitize the code
  - [ ] remove unused imports
  - [ ] organize imports
  - [ ] look for places where similar actions are implemented in a different way and make it uniform
  - [ ] ask assistant to look for code smells
- [ ] add created and updated date to the items
- [ ] card for a user character

## Time measurement
I want somehow to measure time during the scene.


# Functional improvements

## Prompts
I want to have prepared prompts for:
- character creation
- scene creation


# Non-functional improvements

## AI instructions
I want to find a form of instructions for coding AI assistant to store general instructions.

## Keep chat history when create summary
I want to keep chat history when creating summary. To decrease the history passed to the model I can mark the messages as summarized and filter them out when passing the history to the model.

## prompts improvements
I want to improve prompts for:
- scene description (make description shorter, not dialogues in it, concentrate on positions, actions, emotions)
- chat summary (concentrate on important events)
