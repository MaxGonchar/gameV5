# Features

## Goal-oriented character behavior
- [ ] add current_goal to character
- [ ] adjust character move prompt to include current_goal
- [ ] add goal achievement validation
- [ ] add initial goal generation
- [ ] add goal updating mechanism (summarize dialogue when goal updates)


## enhancements
- add actions to the characters' responses
- adjust current reality for character to concentrate on positions, feeling and changing in mood.
- shorten some content (characters' memory, scene descriptions) (keep in short, tag like form)
- PROBLEM: growing scene description (Not sure)
- PROBLEM: still conflicts with poses.
- PROBLEM: involving in dialogue disturbs the actions to reach the goal.
- PROBLEM: confuses with character's sex.
- consider moving speech pattern to RESPONSE RULES
- restrict amount of characters' active memory (memory items going to prompt)

### post implementation:
- [ ] delete story functionality
- [ ] solve todos
- [ ] sanitize the code
  - [ ] remove unused imports
  - [ ] organize imports
  - [ ] look for places where similar actions are implemented in a different way and make it uniform
  - [ ] ask assistant to look for code smells
- [ ] do not allow summarize the last message
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
