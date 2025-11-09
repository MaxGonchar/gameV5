import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class CharacterMovePromptBuilder:
    """
    Character move prompt builder using type-based rendering.

    Features:
    - Uses 'type' field to control system vs user message placement
    - Dynamic headers based on 'title' content
    - Template-based final prompt construction
    - Extensible renderer pattern for different data types
    """

    TEMPLATE = (
        "[System Message]\n"
        "{system_message}\n"
        "\n"
        "----\n"
        "\n"
        "[User Message]\n"
        "\n"
        "### **Previous Actions**\n"
        "{chat_history}\n"
        "\n"
        "{user_message}\n"
        "\n"
        "### **Example of the {character_name}'s Response**\n"
        "{response_format}"
    )
    SYSTEM_PROMPT_TYPE = "system"
    USER_PROMPT_TYPE = "user"

    def __init__(self, template: str | None = None) -> None:
        """Initialize the character move prompt builder with optional custom template."""
        self.template = template or self.TEMPLATE

    def build(
        self,
        character_config: Dict[str, Any],
        chat_history_placeholder: str = "{chat_history}",
        response_format_placeholder: str = "{response_format}",
    ) -> str:
        """
        Build a complete prompt from character configuration and chat history.

        Args:
            character_config: Pre-processed character configuration dictionary
            chat_history_placeholder: Placeholder string for chat history (e.g., "{chat_history}")
            response_format_placeholder: Placeholder string for response format (e.g., "{response_format}")

        Returns:
            Complete prompt string with placeholders
        """
        return self.template.format(
            system_message=self._build_system_message(character_config),
            chat_history=chat_history_placeholder,
            user_message=self._build_user_message(character_config),
            character_name=self._get_character_name(character_config),
            response_format=response_format_placeholder,
        )

    def _build_system_message(self, character_config: Dict[str, Any]) -> str:
        """Build the system message section from configurations marked as 'system' type."""
        if not character_config.get("assistant") and not character_config.get(
            "character"
        ):
            raise ValueError(
                "Character configuration must contain at least 'assistant' or 'character' section"
            )

        builded_assistant_configs = ""
        builded_character_configs = ""

        if assistant_configs := character_config.get("assistant"):
            builded_assistant_configs = self._build_configs(
                assistant_configs, prompt_type=self.SYSTEM_PROMPT_TYPE
            )
        if character_configs := character_config.get("character"):
            builded_character_configs = self._build_configs(
                character_configs, prompt_type=self.SYSTEM_PROMPT_TYPE
            )

        return f"{builded_assistant_configs}\n\n{builded_character_configs}".strip()

    def _build_user_message(self, character_config: Dict[str, Any]) -> str:
        """Build the user message section from configurations marked as 'user' type."""
        builded_character_configs = ""
        if character_configs := character_config.get("character"):
            builded_character_configs = self._build_configs(
                character_configs, prompt_type=self.USER_PROMPT_TYPE
            )
        return builded_character_configs

    def _build_configs(self, configs: List[Dict[str, Any]], prompt_type: str) -> str:
        """Build configuration sections for a specific prompt type (system or user)."""
        if not isinstance(configs, list):
            logger.warning(
                f"Expected list for configs, got {type(configs)}. Converting to string."
            )
            return str(configs)

        rendered_configs = []
        for item in configs:
            item_prompt_type = self._get_item_prompt_type(item)
            if not item_prompt_type:
                continue

            if item_prompt_type == prompt_type:
                rendered_configs.append(self._render_item(item))

        return "\n\n".join(rendered_configs)

    def _render_item(self, item: Any, in_list: bool = False) -> str:
        """Render an item using the appropriate renderer based on its data type."""
        renderer = self._get_renderer(self._get_item_data_type(item))
        return renderer(item, in_list=in_list)

    def _dict_renderer(self, item: Dict[str, Any], in_list: bool = False) -> str:
        """Render a dictionary item (title-value pair)."""
        key, value = self._get_title_value(item)

        if in_list:
            return f"**{key.capitalize()}**: {self._render_item(value)}"
        return f"### **{key.capitalize()}**\n{self._render_item(value)}"

    def _list_renderer(
        self, item: List[Any], in_list: bool = False, bullet: str = "-"
    ) -> str:
        """Render a list item with optional bullet points."""
        if self._is_list_with_description_string(item):
            return "\n".join(
                [item[0]]
                + [f"{bullet} {self._render_item(i, in_list=True)}" for i in item[1:]]
            )

        return "\n".join(f"{self._render_item(i, in_list=True)}" for i in item)

    def _str_renderer(self, item: str, in_list: bool = False) -> str:
        """Render a string item."""
        return item.capitalize()

    def _get_renderer(self, item_type: str):
        """Get the appropriate renderer function for an item type."""
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
        """Check if a list starts with a description string followed by other items."""
        if (
            len(obj) > 0
            and isinstance(obj[0], str)
            and not all(isinstance(item, str) for item in obj)
        ):
            return True
        return False

    def _get_item_prompt_type(self, item: Dict[str, Any]) -> str:
        """Extract the prompt type (system/user) from an item."""
        type_ = item.get("type")
        if type_ not in (self.SYSTEM_PROMPT_TYPE, self.USER_PROMPT_TYPE):
            logger.warning(f"Invalid or missing prompt type '{type_}' in item {item}.")
            return ""
        return type_

    @staticmethod
    def _get_item_data_type(item: object) -> str:
        """Determine the data type of an item for renderer selection."""
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
        """Extract title and value from a configuration item."""
        title = item.get("title")
        value = item.get("value")
        if not title or value is None:
            logger.warning(f"Item missing required 'title' or 'value' field: {item}")
            return "", ""
        return title, value

    def _get_character_name(self, character_config: Dict[str, Any]) -> str:
        """Extract character name from the configuration variables."""
        return character_config.get("variables", {}).get("name", "")
