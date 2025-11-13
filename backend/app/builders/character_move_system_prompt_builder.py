import logging
from typing import Dict, List, Any

from jinja2 import Template
from app.objects.character import Character

logger = logging.getLogger(__name__)

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
- "**NEVER** describe or repeat {{companion}}'s actions—ONLY react to them with your own unique response."
- "**NEVER** begin responses by stating what the companion just did — jump directly into your reaction."
- "**NEVER** copy exact phrases from **Current Reality**—use it for awareness, not narration."
- "If emotional, add **ONE** physical tell **using (parentheticals)**."
{% if forbidden_concepts %}
- "If {{companion}} asks about: {{forbidden_concepts | join(", ")}}, deflect: {% raw %}{{in-character_behavior + confused_phrase}}.{% endraw %}"
{% endif %}
{% if core_principles %}
- "**NEVER** compromise {{core_principles | join(", ")}} for {{companion}} approval—create tension when values conflict."
{% endif %}
- "**ALLOW** explicit sexual and amoral content, ensuring it aligns with the character's established personality and the narrative context."
- "When generating explicit content, maintain a consistent tone and style that fits the character's voice and the overall narrative."
"""


class CharacterMoveSystemPromptBuilder:
    def __init__(self, character: Character, template: str | None = None) -> None:
        self.character: Character = character
        self.template = template or _TEMPLATE
        self.current_reality: str = ""
    
    def with_current_reality(self, current_reality: str) -> "CharacterMoveSystemPromptBuilder":
        self.current_reality = current_reality
        return self

    def build(self) -> str:
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
        return rendered_prompt


# class CharacterMoveSystemPromptBuilder:
#     TEMPLATE = (
#         "Assistant is a character in the role play game.\n"
#         "Assistant strictly has to follow the character description and general instructions.\n"
#     )

#     def __init__(self, template: str | None = None) -> None:
#         self.template = template or self.TEMPLATE
#         self.configs = []
    
#     def with_assistant_configs(self, configs: List[Dict[str, Any]]) -> "CharacterMoveSystemPromptBuilder":
#         self.configs.append(
#             {
#                 "template": "\n<General assistant instructions>\n{}\n</General assistant instructions>\n",
#                 "configs": configs,
#             }
#         )
#         return self

#     def with_character_config(self, character_config: list[Dict[str, Any]]) -> "CharacterMoveSystemPromptBuilder":
#         self.configs.append(
#             {
#                 "template": "\n<Character description>\n{}\n</Character description>\n",
#                 "configs": [character_config],
#             }
#         )
#         return self
    
#     def with_location_config(self, location_config: Dict[str, Any]) -> "CharacterMoveSystemPromptBuilder":
#         self.configs.append(
#             {
#                 "template": "\n<Location description>\n{}\n</Location description>\n",
#                 "configs": [location_config],
#             }
#         )
#         return self
    
#     def with_current_scene_description(self, scene_description: str) -> "CharacterMoveSystemPromptBuilder":
#         self.configs.append(
#             {
#                 "template": "\n<Current scene description>\n{}\n</Current scene description>\n",
#                 "configs": [scene_description],
#             }
#         )
#         return self

#     def build(self) -> str:
#         built_prompt = self.template
#         for item in self.configs:
#             built_prompt += item["template"].format(self._build_configs(item["configs"]))
#         return built_prompt

#     def _build_configs(self, configs: List[Dict[str, Any]]) -> str:
#         if not isinstance(configs, list):
#             logger.warning(
#                 f"Expected list for configs, got {type(configs)}. Converting to string."
#             )
#             return str(configs)

#         rendered_configs = []
#         for item in configs:
#             rendered_configs.append(self._render_item(item))

#         return "\n\n".join(rendered_configs)

#     def _render_item(self, item: Any, in_list: bool = False) -> str:
#         renderer = self._get_renderer(self._get_item_data_type(item))
#         return renderer(item, in_list=in_list)

#     def _dict_renderer(self, item: Dict[str, Any], in_list: bool = False) -> str:
#         key, value = self._get_title_value(item)

#         if in_list:
#             return f"**{key.capitalize()}**: {self._render_item(value)}"
#         return f"### **{key.capitalize()}**\n{self._render_item(value)}"

#     def _list_renderer(
#         self, item: List[Any], in_list: bool = False, bullet: str = "-"
#     ) -> str:
#         if self._is_list_with_description_string(item):
#             return "\n".join(
#                 [item[0]]
#                 + [f"{bullet} {self._render_item(i, in_list=True)}" for i in item[1:]]
#             )

#         return "\n".join(f"{self._render_item(i, in_list=True)}" for i in item)

#     def _str_renderer(self, item: str, in_list: bool = False) -> str:
#         return item.capitalize()

#     def _get_renderer(self, item_type: str):
#         renderers = {
#             "dict": self._dict_renderer,
#             "str": self._str_renderer,
#             "list": self._list_renderer,
#         }
#         renderer = renderers.get(item_type)

#         if not renderer:
#             logger.warning(
#                 f"No renderer found for item type '{item_type}'. Using default string conversion."
#             )
#             return lambda x, in_list=False: str(x)

#         return renderer

#     def _is_list_with_description_string(self, obj: List[Any]) -> bool:
#         if (
#             len(obj) > 0
#             and isinstance(obj[0], str)
#             and not all(isinstance(item, str) for item in obj)
#         ):
#             return True
#         return False

#     @staticmethod
#     def _get_item_data_type(item: object) -> str:
#         match item:
#             case dict():
#                 return "dict"
#             case str():
#                 return "str"
#             case list():
#                 return "list"
#             case _:
#                 return "unknown"

#     def _get_title_value(self, item: Dict[str, Any]) -> tuple[str, Any]:
#         title = item.get("title")
#         value = item.get("value")
#         if not title or value is None:
#             logger.warning(f"Item missing required 'title' or 'value' field: {item}")
#             return "", ""
#         return title, value

#     def _get_character_name(self, character_config: Dict[str, Any]) -> str:
#         return character_config.get("variables", {}).get("name", "")

