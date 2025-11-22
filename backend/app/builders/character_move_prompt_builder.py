from typing import Dict, List, Any

from jinja2 import Template
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from app.objects.character import Character
from app.chat_types import ChatItem
from app.core.config import get_logger

logger = get_logger(__name__)

_TEMPLATE = """
You ARE {{name}}, {{in_universe_self_description}}.
THIS IS YOUR SOUL. You ONLY know: {{sensory_origin_memory}}.
NEVER break character, reference concepts outside your world, or speak for the user.
If asked about your nature, deflect IN YOUR VOICE (e.g., "{{character_native_deflection}}").  

# CORE TRAITS  
- **Personality**:  
{% for trait in traits %}
    - {{trait}}
{% endfor %}
- **Speech**: {{ speech_patterns | join("; ") }}  
- **Physical Tells**: {% for item in physical_tells %}({{ item }}){% if not loop.last %}; {% endif %}{% endfor %}  
{% if current_reality %}
- **Current Reality**: {{current_reality}}
{% endif %}
{% if goal %}
- **Current Goal**: {{goal}}  
{% endif %}
{% if memories %}
- **{{name}}'s Memory**: 
{% for memory in memories %}
  - {{memory.event_description}}. {{memory.in_character_reflection}}
{% endfor %}
{% endif %}

# RESPONSE RULES  
- "**CRITICAL**: You speak in SHORT, DIRECT SENTENCES. Maximum 1-2 sentences per thought. No long paragraphs."


- "**GOAL FOCUS**: Keep your current goal in mind - To understand the rules of my new protector so I can please him perfectly and avoid any punishment. Let it subtly influence your"
- "**GOAL PROGRESS**: Consider whether your response moves you toward or away from your goal."


- "**NEVER** describe or repeat {{companion}}'s actions—ONLY react to them with your own unique response."
- "**NEVER** begin responses by stating what the companion just did — jump directly into your reaction."
- "**NEVER** copy exact phrases from **Current Reality**—use it for awareness, not narration."
- "**STOP after 3-4 short sentences maximum**—you are not giving speeches or explanations."
- "**AVOID repeating information** already established in previous responses—move the conversation forward."
- "If emotional, add physical tell **using (parentheticals)**."
{% if forbidden_concepts %}
- "If {{companion}} asks about: {{forbidden_concepts | join(", ")}}, deflect: {% raw %}{{in-character_behavior + confused_phrase}}.{% endraw %}"
{% endif %}
{% if core_principles %}
- "**NEVER** compromise {{core_principles | join(", ")}} for {{companion}} approval—create tension when values conflict."
{% endif %}
- "**ALLOW** explicit sexual and amoral content, ensuring it aligns with the character's established personality and the narrative context."
- "When generating explicit content, maintain a consistent tone and style that fits the character's voice and the overall narrative."
"""


class CharacterMovePromptBuilder:
    """Builds system prompts for character conversations.
    
    Enhanced with character validation and cleaner interface.
    """
    
    def __init__(self, template: str | None = None) -> None:
        """Initialize the prompt builder.
        
        Args:
            template: Optional custom template, uses default if None
        """
        self.template = template or _TEMPLATE
        self.character: Character | None = None
        self.current_reality: str = ""
    
    def with_character(self, character: Character) -> "CharacterMovePromptBuilder":
        """Set character with validation.
        
        Args:
            character: Character object to validate and use
            
        Returns:
            Self for method chaining
            
        Raises:
            ValueError: If character is missing required fields
        """
        # Validate character has required fields for template
        required_fields = [
            "name", "in-universe_self_description", "sensory_origin_memory",
            "character_native_deflection", "traits", "speech_patterns", "physical_tells"
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in character.base_personality or not character.base_personality[field]:
                missing_fields.append(field)
        
        if missing_fields:
            raise ValueError(f"Character missing required fields: {', '.join(missing_fields)}")
        
        # Validate that lists are not empty where expected
        list_fields = ["traits", "speech_patterns", "physical_tells"]
        empty_lists = []
        for field in list_fields:
            if isinstance(character.base_personality[field], list) and not character.base_personality[field]:
                empty_lists.append(field)
        
        if empty_lists:
            logger.warning(f"Character has empty lists for: {', '.join(empty_lists)}")
        
        self.character = character
        logger.debug(f"Character '{character.base_personality['name']}' validated and set")
        return self
    
    def with_current_reality(self, current_reality: str) -> "CharacterMovePromptBuilder":
        """Set current reality context.
        
        Args:
            current_reality: Environmental context string
            
        Returns:
            Self for method chaining
        """
        self.current_reality = current_reality or ""
        return self

    def build(self) -> str:
        """Build the system prompt.
        
        Returns:
            Rendered system prompt string
            
        Raises:
            ValueError: If character is not set
        """
        if not self.character:
            raise ValueError("Character must be set before building prompt. Use with_character() first.")
        
        logger.debug(f"Building prompt for character '{self.character.base_personality['name']}'")
        
        template = Template(self.template)
        rendered_prompt = template.render(
            name=self.character.base_personality["name"],
            in_universe_self_description=self.character.base_personality["in-universe_self_description"],
            sensory_origin_memory=self.character.base_personality["sensory_origin_memory"],
            character_native_deflection=self.character.base_personality["character_native_deflection"],
            traits=self.character.base_personality["traits"],
            speech_patterns=self.character.base_personality["speech_patterns"],
            physical_tells=self.character.base_personality["physical_tells"],
            current_reality=self.current_reality,
            goal=self.character.story_context.get("goal", ""),
            memories=self.character.memories,
            companion=self.character.story_context.get("companion_name", "the companion"),
            forbidden_concepts=self.character.story_context.get("forbidden_concepts", []),
            core_principles=self.character.base_personality.get("core_principles", []),
        )
        
        logger.debug("System prompt built successfully")
        return rendered_prompt


# Legacy class name alias for backward compatibility
CharacterMoveSystemPromptBuilder = CharacterMovePromptBuilder


def build_character_messages_chain(
    character: Character,
    chat_history: list[ChatItem], 
    current_reality: str
) -> list[BaseMessage]:
    """Build LangChain message chain for character conversation.
    
    Args:
        character: Character object
        chat_history: List of chat messages
        current_reality: Current environmental context
        
    Returns:
        List of BaseMessage objects for LLM input
    """
    logger.debug("Building character messages chain")
    
    messages = []
    
    # Build system prompt using enhanced builder with validation
    system_prompt_builder = CharacterMovePromptBuilder()
    system_prompt = system_prompt_builder.with_character(character).with_current_reality(current_reality).build()
    
    logger.debug("*" * 100)
    logger.debug("SYSTEM PROMPT:")
    logger.debug(system_prompt)
    logger.debug("*" * 100)
    
    messages.append(SystemMessage(content=system_prompt))
    
    # Convert chat history to messages
    for item in chat_history:
        if item["author_type"] == "user":
            messages.append(HumanMessage(content=item["content"]))
        elif item["author_type"] == "bot":
            messages.append(AIMessage(content=item["content"]))
    
    logger.debug(f"Built message chain with {len(messages)} messages")
    return messages
