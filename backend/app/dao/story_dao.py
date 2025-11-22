from pathlib import Path
from typing import TypedDict
from uuid import uuid4

from app.core.config import settings, get_logger
from app.objects.meta import MetaData
from .yaml_file_handler import YamlFileHandler
from .file_system_operations import FileSystemOperations

logger = get_logger(__name__)


class StorySummary(TypedDict):
    id: str
    title: str


class StoryDAO:
    def __init__(self, stories_dir: str | None = None):
        self.stories_dir = Path(stories_dir or settings.stories_base_dir)
        self.fs_ops = FileSystemOperations()

    async def _create_story_dir(self, story_dir_path: Path) -> None:
        """Create the main story directory."""
        await self.fs_ops.create_dir(story_dir_path, parents=True, exist_ok=False)

    async def _copy_character(self, story_dir_path: Path, character_path: Path) -> int:
        """Copy character directory to the story directory."""
        new_character_dir = story_dir_path / "characters" / character_path.name
        char_files_copied = await self.fs_ops.copy_dir(
            src=character_path, 
            dest=new_character_dir, 
            create_if_not_exists=True
        )
        return char_files_copied

    async def _create_story_meta(self, story_dir_path: Path, story_meta: MetaData) -> None:
        """Create the meta.yaml file for the story."""
        meta_file = story_dir_path / "meta.yaml"
        await self.fs_ops.create_yaml_file(meta_file, story_meta.to_dict())

    async def _delete_story_dir(self, story_dir_path: Path) -> None:
        """Delete the story directory (used for rollback)."""
        if story_dir_path.exists():
            await self.fs_ops.delete_dir(story_dir_path)

    async def create_story(self, character_path: Path, story_meta: MetaData) -> str:
        """Create a new story and return its ID."""
        new_story_id = str(uuid4())
        logger.info("Creating new story with id=%s", new_story_id)

        new_story_dir = self.stories_dir / new_story_id
        
        try:
            # 1. Create story directory
            await self._create_story_dir(new_story_dir)

            # 2. Copy character directory to story
            char_files_copied = await self._copy_character(new_story_dir, character_path)
            logger.info("Copied %d character files for story %s", char_files_copied, new_story_id)

            # 3. Create meta.yaml file
            await self._create_story_meta(new_story_dir, story_meta)

            logger.info("Story %s created successfully at %s", new_story_id, new_story_dir)
            return new_story_id
            
        except Exception as e:
            logger.error("Failed to create story %s: %s", new_story_id, e)
            
            # Rollback: clean up partially created story directory
            try:
                logger.info("Rolling back: deleting partially created story directory %s", new_story_dir)
                await self._delete_story_dir(new_story_dir)
                logger.info("Successfully rolled back story directory %s", new_story_dir)
            except Exception as rollback_error:
                logger.error("Failed to rollback story directory %s: %s", new_story_dir, rollback_error)
                # Don't raise rollback error, prioritize original error
            
            raise
    
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
                metadata_file = story_dir / "meta.yaml"
                if metadata_file.exists():
                    meta_data = await yaml_handler.read_yaml_file(metadata_file)
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
