## Correct current character

### ✅ 1. correct current system prompt
- remove less relevant information
  - remove memory generated during session creation for sake of second level memory
  - review items like:
    - sensory_origin_memory
    - character_native_deflection
- add more specific
  - appearance self description

### ✅ 2. correct character data structure taking into account new system prompt
- update fields explanations so they will reflect the meaning clearly

### 3. add second level memory
- develop data structure for second level memory
- inject second level memory into system prompt
- remove memory generation during session creation
- use second level memory for initial memory population

### ✅ 4. correct character data structure according to new approaches

### ✅ 5. extend character data with general data
- consider creation sets of speech patterns and body language patterns for wide variety of characters' mental states so it can be used for dynamically adjusting character behavior during the game play
- add these sets to character data structure

### 6. ✅ Adjust character creation flow

### 7. Test:
- ✅ second level memory appears in system prompt
- first level memory appears in prompt when exists
- ✅ memories are not generated during session creation

## Migrate to semantic based mental states.

### 1. define new mental states structure
- define new mental states structure based on semantic model
  - update character data structure accordingly
  - update character creation flow accordingly
- create tracking logic for new mental states
  - new LLM call
  - new update logic
- test


## Migrate to semantic based behavior model.

### 1. define new behavior model structure
- define new behavior model structure based on semantic model and general guiding instead of specific rules
- create logic to check that all behavior models covers all possible mental states and there's no potentially situations when character will have no behavior model to follow or multiple conflicting behavior models
- review current model matching logic and update it according to new behavior model structure
- create assistant to generate instructions for behavior model based on character mental states, environment, personality, last mental trajectory, last actions, etc.
- test


## Final test and adjustments
- character knows past due to second level memory
- character mental states are tracked according to semantic model
- character behavior is generated according to semantic based behavior model
  - no mental state combinations where character has no behavior model to follow
  - speech patterns and body language patterns are created for particular behavioral model according to character personality and current situation.
- during behavioral mode change the first level memory item is created
