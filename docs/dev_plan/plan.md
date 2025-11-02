# Features

## new character prompt template
- [x] develop new character prompt template
- [x] develop a prompts helping user to create a character

- [x] develop new character data structure

- [ ] update story creation logic to generate story related data
  - [ ] correct prompt to:
    - generate memory in form of event description + in-character reflection

- [ ] implement new character prompt builder
  - consider jinja template handling
  - for now stop embedding and related logic

- [ ] integrate new prompt templates and prompt builder into the main codebase

- [ ] develop new scene description prompt template
  - [ ] it should generate scene description for user and for character separately

- [ ] develop new memory generation prompt template
  - [ ] store memory in general description and in character-specific description
  - [ ] for character create a field for active memory to store 10 recent events


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
