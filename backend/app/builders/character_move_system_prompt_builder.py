import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class CharacterMoveSystemPromptBuilder:
    TEMPLATE = (
        "Assistant is a character in the role play game.\n"
        "Assistant strictly has to follow the character description and general instructions.\n"
        "\n"
        "<Character description>\n"
        "{character_description}"
        "</Character description>\n"
        "\n"
        "<General assistant instructions>\n"
        "{general_instructions}"
        "</General assistant instructions>\n"
    )

    def __init__(self, template: str | None = None) -> None:
        self.template = template or self.TEMPLATE

    def build(
        self,
        character_config: Dict[str, Any],
    ) -> str:
        return self.template.format(
            character_description=self._build_configs(character_config["character"]),
            general_instructions=self._build_configs(character_config["assistant"]),
        )

    def _build_configs(self, configs: List[Dict[str, Any]]) -> str:
        if not isinstance(configs, list):
            logger.warning(
                f"Expected list for configs, got {type(configs)}. Converting to string."
            )
            return str(configs)

        rendered_configs = []
        for item in configs:
            rendered_configs.append(self._render_item(item))

        return "\n\n".join(rendered_configs)

    def _render_item(self, item: Any, in_list: bool = False) -> str:
        renderer = self._get_renderer(self._get_item_data_type(item))
        return renderer(item, in_list=in_list)

    def _dict_renderer(self, item: Dict[str, Any], in_list: bool = False) -> str:
        key, value = self._get_title_value(item)

        if in_list:
            return f"**{key.capitalize()}**: {self._render_item(value)}"
        return f"### **{key.capitalize()}**\n{self._render_item(value)}"

    def _list_renderer(
        self, item: List[Any], in_list: bool = False, bullet: str = "-"
    ) -> str:
        if self._is_list_with_description_string(item):
            return "\n".join(
                [item[0]]
                + [f"{bullet} {self._render_item(i, in_list=True)}" for i in item[1:]]
            )

        return "\n".join(f"{self._render_item(i, in_list=True)}" for i in item)

    def _str_renderer(self, item: str, in_list: bool = False) -> str:
        return item.capitalize()

    def _get_renderer(self, item_type: str):
        renderers = {
            "dict": self._dict_renderer,
            "str": self._str_renderer,
            "list": self._list_renderer,
        }
        renderer = renderers.get(item_type)

        if not renderer:
            logger.warning(
                f"No renderer found for item type '{item_type}'. Using default string conversion."
            )
            return lambda x, in_list=False: str(x)

        return renderer

    def _is_list_with_description_string(self, obj: List[Any]) -> bool:
        if (
            len(obj) > 0
            and isinstance(obj[0], str)
            and not all(isinstance(item, str) for item in obj)
        ):
            return True
        return False

    @staticmethod
    def _get_item_data_type(item: object) -> str:
        match item:
            case dict():
                return "dict"
            case str():
                return "str"
            case list():
                return "list"
            case _:
                return "unknown"

    def _get_title_value(self, item: Dict[str, Any]) -> tuple[str, Any]:
        title = item.get("title")
        value = item.get("value")
        if not title or value is None:
            logger.warning(f"Item missing required 'title' or 'value' field: {item}")
            return "", ""
        return title, value

    def _get_character_name(self, character_config: Dict[str, Any]) -> str:
        return character_config.get("variables", {}).get("name", "")

