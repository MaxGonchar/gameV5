# Implementation Plan: Dynamic Behavioral Instruction System

This document outlines the implementation steps for transitioning from pre-defined behavioral modes to dynamically generated, session-aware behavioral instructions.

---

## Phase 1: Character Configuration Updates
According to semantic based system, we will not use numeric levels for mental states. Instead, we will define mental states with descriptive labels. During mental impact analysis, model will interpret the current mental state based on its semantic description and context, rather than relying on fixed numeric thresholds. This allows for more nuanced and flexible behavior generation that can adapt to a wider range of scenarios.

- [x] update mental stats data structure in character.yaml schema to remove numeric levels and add information about mental state semantics allowing model to interpret them based on context:

- [x] add speech, body language, and action tendencies associated with each mental state. It will serve as guidance for the model to generate appropriate behaviors based on the character's current mental state and the context of the interaction.

- [x] update character creation framework to support new mental state definitions
  - [ ] validate so all shifts are covered

- [x] update LLM mental state impact analysis to interpret semantic mental states and their associated tendencies instead of numeric levels. (IMPORTANT: mental states shouldn't jump from one to another after each interaction if no significant event happened. Instead, model should consider the trajectory of mental states over time and the context of interactions to determine if a change in mental state is warranted.)

- [x] update character logic to handle semantic mental states instead of numeric levels

- [x] update logic to detect changes in mental states based on semantic descriptions and context

- [ ] TEST: Create test character with new mental state definitions and verify behavior generation reflects semantic mental states and their associated tendencies
  - [ ] all data is passed to the model correctly
  - [ ] chat history for emotional impact is trimmed from the last first level memory message id


## Phase 2. Add Priority & Weight System to Mental States
Priority & Weight System should reflect the relative importance of different mental states and their levels in determining the character's overall mental state and behavior. This will allow handle cases when one less important mental state but in high level can overshadow another more important mental state but in low level. For example, if a character has a high level of longing (which is less important) but a low level of security (which is more important), the character's behavior should reflect longing more than security.
- [ ] Add priority field to mental state types (Security=1, Trust=2, Longing=3)
- [ ] Add weight field to mental state levels (0-100 scale per level)
- [ ] update character creation framework to support new priority and weight fields for mental states
- [ ] think about validation rules for priority and weight fields
- [ ] Implement impact calculation for determining dominant states


## Phase 3: Dynamic Behavioral Instruction

- [ ] design new data structure for behavioral model

- [ ] update/create character emotion related set of instruction so they will reflect the character's behavior tendencies associated with each mental state and will be used as guidance for the model to generate appropriate behaviors based on the character's current mental state and the context of the interaction.

- [ ] implement LLM assistant to generate dynamic behavioral instructions based on character's current mental state, context of interactions, and trajectory of mental states over time.

- [ ] update character logic to utilize dynamic behavioral instructions for generating speech, body language, and actions

- [ ] TEST: Create test character and verify that dynamic behavioral instructions are generated appropriately based on mental state, context, and trajectory of mental states over time. Ensure that behavior generation reflects the dynamic instructions accurately.


## Phase 4: Caching of Behavioral Instructions

- [ ] update character data structure to store previous behavioral instructions and their associated mental states and contexts

- [ ] implement logic for reusing previous behavioral instructions

- [ ] TEST: Create test character and verify that previous behavioral instructions are reused appropriately when the character is in a similar mental state and context as before. Ensure that behavior generation reflects the reused instructions accurately while still allowing for dynamic adjustments based on any changes in mental state or context.


## Phase 5: Define terms and conditions for reusing previous behavioral instructions
TBD
