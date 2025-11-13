"""
Character service module containing business logic for character operations.
"""

import logging
import os

from jinja2 import Template

from app.dao.story_dao import StoryDAO
from app.dao.character_dao import CharacterDAO
from app.dao.location_dao import LocationDAO
from app.objects.meta import MetaData
from app.objects.story_state import StoryState
from app.models.responses import StorySummary, StoriesResponse
from app.models.requests import CreateStoryRequest
from app.services.llm_communicator import LLMCommunicator
from app.llm.venice_ai import VeniceAIChatModel
from app.models.session_context import SessionContextResponse, SESSION_CONTEXT_GENERATION_PROMPT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


SESSION_CONTEXT_GENERATION_USER_PROMPT = """
## Character personality:
*Name:* {{character_name}}

*In-Universe Self Description:* {{in_universe_self_description}}

*Sensory Origin Memory:* {{sensory_origin_memory}}

*Character Native Deflection:* {{character_native_deflection}}

*Traits:*
{% for trait in traits %}
- {{trait}}
{% endfor %}

*Core Principles:*
{% for principle in core_principles %}
- {{principle}}
{% endfor %}

*Physical Tells:*
{% for tell in physical_tells %}
- {{tell}}
{% endfor %}

*Speech Patterns:*
{% for pattern in speech_patterns %}
- {{pattern}}
{% endfor %}

*General Demeanor:*
{{general_demeanor}}

## Character Home World description:
{{character_home_world_description}}

## Character Appearance description:
{{character_appearance_description}}

## Character Background history:
{{character_background_history}}

## Companion Context
*Name:* {{companion_name}}
*Description:* {{companion_description}}
*Context:* {{companion_context}}

## Meeting Location Description
{{meeting_location_description}}

## Meeting Description
{{meeting_description}}
"""


class StoriesService:
    """Service class handling story business logic."""

    def __init__(self):
        """Initialize the story service."""
        self.story_dao = StoryDAO()
        self.character_dao = CharacterDAO()

    async def create_story(self, request: CreateStoryRequest) -> str:
        """
        Create a new story based on the provided request data.
        
        Args:
            request (CreateStoryRequest): Data required to create a new story.
        
        Returns:
            str: The ID of the newly created story.
        """
        try:
            venice_api_key = os.getenv("VENICE_API_KEY")
            if not venice_api_key:
                raise ValueError(
                    "VENICE_API_KEY environment variable is required. "
                    "Please set it in your .env file or environment."
                )
            venice_model = VeniceAIChatModel(
                api_key=venice_api_key,
                model="mistral-31-24b",
                temperature=0.7
            )

            logger.info("Creating a new story")

            # Get character related data
            character = await self.character_dao.get_character(request.character_id)

            # Create context prompt
            context_prompt_template = Template(SESSION_CONTEXT_GENERATION_USER_PROMPT)
            context_prompt = context_prompt_template.render(
                {
                    "character_name": character.base_personality["name"],
                    "in_universe_self_description": character.base_personality["in-universe_self_description"],
                    "sensory_origin_memory": character.base_personality["sensory_origin_memory"],
                    "character_native_deflection": character.base_personality["character_native_deflection"],
                    "traits": character.base_personality["traits"],
                    "core_principles": character.base_personality["core_principles"],
                    "physical_tells": character.base_personality["physical_tells"],
                    "speech_patterns": character.base_personality["speech_patterns"],
                    "general_demeanor": character.general["personality"],
                    "character_home_world_description": character.general["home_world"],
                    "character_appearance_description": character.general["appearance"],
                    "character_background_history": character.general["background"],
                    "companion_name": request.companion_name,
                    "companion_description": request.companion_description,
                    "companion_context": request.companion_context,
                    "meeting_location_description": request.meeting_location_description,
                    "meeting_description": request.meeting_description
                }
            )

            print("*" * 100)
            print("Context Prompt:")
            print(context_prompt)
            print("*" * 100)

            # Generate story related context
            llm_communicator = LLMCommunicator(llm_model=venice_model)
            session_context = await llm_communicator.generate_structured_response(
                system_prompt=SESSION_CONTEXT_GENERATION_PROMPT,
                user_prompt=context_prompt,
                response_model=SessionContextResponse
            )

            print("*" * 100)
            print("Generated Session Context:")
            from pprint import pprint
            pprint(session_context)
            print("*" * 100)

            # Create initial story data
            story_id = await self.story_dao.create_story(
                character_path=self.character_dao.get_character_folder(request.character_id),
                story_meta=MetaData(
                    {
                        "title": request.story_title,
                        "initial_scene_description": {
                            "companion_side": session_context.meeting_scene_description.companion_side,
                            "character_side": session_context.meeting_scene_description.character_side,
                            "environmental_context": session_context.meeting_scene_description.environmental_context
                        }
                    }
                )
            )
            logger.info(f"Successfully created story with ID: {story_id}")

            # Create StoryState entity and fill the character related data
            story_state = await StoryState(
                story_id=story_id,
                character_id=request.character_id
            )
            story_state.add_story_context_character_data(
                {
                    "companion": session_context.companion,
                    "forbidden_concepts": session_context.forbidden_concepts,
                    "current_reality": session_context.current_reality,
                    "goal": session_context.goal,
                    "memories": [
                        {
                            "event_description": item.event_description,
                            "in_character_reflection": item.in_character_reflection

                        } for item in session_context.memories
                    ],
                    "confused_phrase": session_context.confused_phrase
                }
            )
            await story_state.save_state()

            return story_id
        except Exception as e:
            logger.exception(f"Error creating story: {e}")
            raise
    
    async def get_stories_summary(self) -> StorySummary:
        """
        Retrieve a summary of all stories.
        
        Returns:
            StorySummary: A summary of all stories.
        """
        summaries = [
            StorySummary(
                id=story["id"],
                title=story["title"],
            )
            for story in await self.story_dao.get_stories_summary()
        ]
        return StoriesResponse(stories=summaries)
