# Features

## Stories
I want to be able start and continue different stories. I want to have set of characters, places, ...
So I can choose character and place for the new story, save it and continue later.
### Main features I need for it:
- entering page where I can see list of stories and create new one
- creating new story I can see list of characters and places to choose from
- when I choose character and place I can enter story page
### dev plan:
- [ ] characters storage
  - [ ] characters dao
  - [ ] characters endpoint
    - [ ] getCharacters
- [ ] places storage
  - [ ] places dao
  - [ ] places endpoint
    - [ ] getPlaces
- [ ] stories storage
  - [ ] stories dao
  - [ ] stories endpoints
    - [ ] getStories
    - [ ] createStory
    - [ ] storyPage

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
