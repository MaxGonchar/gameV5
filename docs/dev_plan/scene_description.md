## Chat-history item:
I need somewhere to store scene description.

### Current:
```yaml
- id: '1'
  author_id: max
  author_type: user
  author_name: Max
  content: So, can I ask you for little favor? You see, I'm new here. Could you be
    my guide in this world?
```

### Updated:
```yaml
- id: '1'
  author_id: max
  author_type: user
  author_name: Max
  content: So, can I ask you for little favor? You see, I'm new here. Could you be
    my guide in this world?
  scene_description: |
    The scene is set in a bustling medieval marketplace filled with vibrant stalls and lively townsfolk. The air is filled with the scent of fresh bread and spices. Max, a newcomer to this world, stands at the center of the market, looking around with curiosity. Nearby, a friendly-looking guide approaches him, ready to offer assistance. The guide is dressed in simple yet practical clothing, indicating their familiarity with the area. The two characters are positioned close to each other, suggesting an imminent interaction as Max seeks guidance in this new environment.
```

Scene description in the current chat-history item describes the scene after the current item's content taken into account.

## Generation flow:

### Current:

1. receive user message
2. get from db character, chat_history, location
3. add user message to chat_history
4. update character according to user message:
   1. get message embeddings
   2. update character state
5. generate character message
6. add character message to chat_history
7. store all updated data to db
8. send character message to user

I need to add scene description update after each action.
I need to deal with first message when there is no scene description yet.

### Updated:

#### Local Processing
1. receive user message
2. get from db character, chat_history, location

#### LLM Call
3. update character according to user message
4. update scene description according to user message (user message scene)

#### LLM Call
5. generate character message

#### LLM Call
6. update scene description according to character message (assistant message scene)

#### Local Processing
7. add user message and scene description to chat_history
8. add character message and scene description to chat_history
9. store all updated data to db
10. send character message to user

## Implementation steps:

### GlobalState class
- ~~implement GlobalState class as composition (facade) of Character, Location, ChatHistory~~
  - ~~get data from db during init~~
- ~~add SessionMeta class to store meta info. For now it will store only initial scene description~~
  - ~~create file and dao for it.~~
- Create service to generate scene description
- Update ChatHistory to store scene description in each item
- Update process_user_message according to new generation flow.