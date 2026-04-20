# First Iteration Features
1. mental state/behavior model
2. Opponent relationship model
3. Goal-oriented character behavior
4. Character creation flow

## Sandbox space for experiments with AI models
- [ ] create a separate space for experiments with AI models where I can test different prompts, configurations, and models without affecting the main project.

## UI improvements
on UI I see user message disappear after submitting it. It would be better to keep it visible until response is received.

## Goal-oriented character behavior
- [X] add current_goal to character
- [X] adjust character move prompt to include current_goal
- [X] add goal achievement validation
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
- create dock with detailed flow of the game process

### post implementation:
- [ ] during formatting fix adding extra comments in imports
- [ ] solve todos
- [ ] sanitize the code
  - [ ] remove unused imports
  - [ ] organize imports
  - [ ] look for places where similar actions are implemented in a different way and make it uniform
  - [ ] ask assistant to look for code smells
- [ ] do not allow summarize the last message
- [ ] add created and updated date to the items
- [ ] card for a user character
- [ ] review exceptions handling, consider to make it simpler, reduce number of exception types if possible. Consider refactoring custom exceptions to be more clear what is internal and wat is external so we could have less types of exceptions.

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


- similar goals
- character doing nothing to acheive the goal
- user initiatives destruct the character's plans
