# # Standard library imports
from pathlib import Path
from typing import Any, Optional

# # Local application imports
from app.core.config import get_logger, settings
from app.core.constants import META_FILE_NAME
from app.exceptions import DataValidationException
from app.objects.meta import MetaData

# # Relative imports
from .path_manager import PathManager
from .yaml_file_handler import YamlFileHandler

logger = get_logger(__name__)


# TODO: refactor:
# make methods smaller, focused on single tasks
# consider reusing "FileSystemOperations" where applicable
class MetaDAO:
    """
    Data Access Object for meta configurations.

    Handles loading meta data from YAML files.
    Structure: {meta_dir}/meta.yaml
    """

    def __init__(
        self,
        story_id: str,
        yaml_handler: YamlFileHandler | None = None,
        path_manager: PathManager | None = None,
    ):
        """
        Initialize the meta DAO.

        Args:
            meta_dir: Directory containing meta.yaml file (default: from settings)
            yaml_handler: YAML file handler dependency
        """
        self.yaml_handler = yaml_handler or YamlFileHandler()
        self.path_manager = path_manager or PathManager()
        self.meta_file = Path(self.path_manager.get_story_meta_file(story_id))

    async def get_meta(self) -> MetaData:
        """
        Load meta data from meta.yaml file.

        Returns:
            MetaData object

        Raises:
            FileOperationException, YamlException: From yaml_handler (bubbled up)
            DataValidationException: If meta data is invalid
        """
        data = await self._read_yaml(self.meta_file)
        return MetaData(data)

    async def _read_yaml(self, file_path: Path) -> dict[str, Any]:
        """Read and validate YAML data from file."""
        data = await self.yaml_handler.read_yaml_file(file_path)

        if not data:
            logger.warning(f"Meta file is empty: {file_path}")
            raise DataValidationException(
                f"Meta data file is empty: {file_path}",
                details={"file_path": str(file_path)},
            )

        if not isinstance(data, dict):
            logger.error(
                f"Invalid meta data format in {file_path}, expected dict but got {type(data).__name__}"
            )
            raise DataValidationException(
                f"Invalid meta data format in {file_path}",
                details={
                    "file_path": str(file_path),
                    "expected_type": "dict",
                    "actual_type": type(data).__name__,
                },
            )

        logger.debug(f"Successfully loaded meta data from {file_path}")
        return data
    
    async def save_meta(self, meta: MetaData) -> None:
        """Save meta data to YAML file."""
        data = meta.to_dict()
        await self.yaml_handler.write_yaml_file(self.meta_file, data)
        logger.debug(f"Successfully saved meta data to {self.meta_file}")
