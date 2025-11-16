import logging
from pathlib import Path
from typing import TypedDict
from uuid import uuid4

from app.core.config import settings
from app.objects.meta import MetaData
from .yaml_file_handler import YamlFileHandler

logger = logging.getLogger(__name__)


class StorySummary(TypedDict):
    id: str
    title: str


class StoryDAO:
    def __init__(self, stories_dir: str | None = None):
        self.stories_dir = Path(stories_dir or settings.stories_base_dir)

    # TODO: delete the story folder if creation fails halfway
    # TODO: refactor method to smaller pieces
    async def create_story(self, character_path: Path, story_meta: MetaData) -> str:
        """Create a new story and return its ID."""
        new_story_id = str(uuid4())
        logger.info("Creating new story with id=%s", new_story_id)

        # create folder for new story
        new_story_dir = self.stories_dir / new_story_id
        logger.info("Creating story directory at %s", new_story_dir)
        new_story_dir.mkdir(parents=True, exist_ok=False)

        # copy character dir from general characters to story characters
        new_character_dir = new_story_dir / "characters" / character_path.name
        new_character_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Copying character from %s to %s", character_path, new_character_dir)
        char_files_copied = 0
        for item in character_path.iterdir():
            if item.is_file():
                try:
                    dest = new_character_dir / item.name
                    dest.write_bytes(item.read_bytes())
                    char_files_copied += 1
                    logger.info("Copied character file %s -> %s", item, dest)
                except Exception:
                    logger.exception("Failed to copy character file %s", item)
        logger.info("Copied %d character files for story %s", char_files_copied, new_story_id)

        # copy location dir from general locations to story locations
        # new_location_dir = new_story_dir / "locations" / location_path.name
        # new_location_dir.mkdir(parents=True, exist_ok=True)
        # logger.info("Copying location from %s to %s", location_path, new_location_dir)
        # loc_files_copied = 0
        # for item in location_path.iterdir():
        #     if item.is_file():
        #         try:
        #             dest = new_location_dir / item.name
        #             dest.write_bytes(item.read_bytes())
        #             loc_files_copied += 1
        #             logger.info("Copied location file %s -> %s", item, dest)
        #         except Exception:
        #             logger.exception("Failed to copy location file %s", item)
        # logger.info("Copied %d location files for story %s", loc_files_copied, new_story_id)

        # create meta.yaml from story_meta
        meta_file = new_story_dir / "meta.yaml"
        yaml_handler = YamlFileHandler()
        logger.info("Writing meta.yaml to %s", meta_file)
        try:
            await yaml_handler.write_yaml_file(meta_file, story_meta.to_dict())
        except Exception:
            logger.exception("Failed to write meta.yaml for story %s", new_story_id)
            raise

        logger.info("Story %s created successfully at %s", new_story_id, new_story_dir)
        return new_story_id
    
    # TODO: do something with this method
    # options: reuse character/location dao methods or write required story data to meta.yaml
    async def get_stories_summary(self) -> list[StorySummary]:
        """
        Get a summary list of all stories.

        Returns:
            List of StorySummary objects containing story ID, location name, and character name.
        """
        stories = []
        yaml_handler = YamlFileHandler()
        
        # Check if stories directory exists
        if not self.stories_dir.exists():
            logger.info("Stories directory %s does not exist", self.stories_dir)
            return stories
        
        # Iterate through all story directories
        for story_dir in self.stories_dir.iterdir():
            if not story_dir.is_dir():
                continue
                
            story_id = story_dir.name
            logger.debug("Processing story %s", story_id)
            
            try:
                # # Get character name
                # character_name = "Unknown Character"
                # characters_dir = story_dir / "characters"
                # if characters_dir.exists():
                #     for char_dir in characters_dir.iterdir():
                #         if char_dir.is_dir():
                #             char_file = char_dir / "character.yaml"
                #             if char_file.exists():
                #                 char_data = await yaml_handler.read_yaml_file(char_file)
                #                 if isinstance(char_data, dict) and "variables" in char_data:
                #                     character_name = char_data["variables"].get("name", "Unknown Character")
                #                 break  # Take first character found
                
                # # Get location name
                # location_name = "Unknown Location"
                # locations_dir = story_dir / "locations"
                # if locations_dir.exists():
                #     for loc_dir in locations_dir.iterdir():
                #         if loc_dir.is_dir():
                #             loc_file = loc_dir / "location.yaml"
                #             if loc_file.exists():
                #                 loc_data = await yaml_handler.read_yaml_file(loc_file)
                #                 if isinstance(loc_data, dict):
                #                     location_name = loc_data.get("name", "Unknown Location")
                #                 break  # Take first location found
                metadata_dir = story_dir / "meta.yaml"
                if metadata_dir.exists():
                    meta_data = await yaml_handler.read_yaml_file(metadata_dir)
                    if isinstance(meta_data, dict) and "title" in meta_data:
                        title = meta_data["title"]
                    else:
                        title = "Untitled Story"
                else:
                    title = "Untitled Story"
                
                # Create story summary
                story_summary: StorySummary = {
                    "id": story_id,
                    "title": title,
                }
                stories.append(story_summary)
                logger.debug("Added story summary: %s", story_summary)
                
            except Exception:
                logger.exception("Failed to process story %s", story_id)
                # Continue processing other stories even if one fails
                continue
        
        logger.info("Found %d stories", len(stories))
        return stories
