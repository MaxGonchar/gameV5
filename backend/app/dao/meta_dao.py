from app.objects.meta import MetaData
from pathlib import Path
from typing import Any, Optional
from .yaml_file_handler import YamlFileHandler
from app.exceptions import DataValidationException
from app.core.config import get_logger, settings
from app.core.constants import META_FILE_NAME

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
        meta_dir: str | None = None,
        yaml_handler: Optional[YamlFileHandler] = None,
    ):
        """
        Initialize the meta DAO.
        
        Args:
            meta_dir: Directory containing meta.yaml file (default: from settings)
            yaml_handler: YAML file handler dependency
        """
        self.meta_dir = Path(meta_dir or path_manager.get_base_data_dir())
        self.yaml_handler = yaml_handler or YamlFileHandler()

    async def get_meta(self) -> MetaData:
        """
        Load meta data from meta.yaml file.
        
        Returns:
            MetaData object
            
        Raises:
            FileOperationException, YamlException: From yaml_handler (bubbled up)
            DataValidationException: If meta data is invalid
        """
        path = Path(path_manager.get_meta_file())
        data = await self._read_yaml(path)
        return MetaData(data)

    async def _read_yaml(self, file_path: Path) -> dict[str, Any]:
        """Read and validate YAML data from file."""
        data = await self.yaml_handler.read_yaml_file(file_path)
        
        if not data:
            logger.warning(f"Meta file is empty: {file_path}")
            raise DataValidationException(
                f"Meta data file is empty: {file_path}",
                details={"file_path": str(file_path)}
            )
            
        if not isinstance(data, dict):
            logger.error(f"Invalid meta data format in {file_path}, expected dict but got {type(data).__name__}")
            raise DataValidationException(
                f"Invalid meta data format in {file_path}",
                details={
                    "file_path": str(file_path),
                    "expected_type": "dict",
                    "actual_type": type(data).__name__
                }
            )
            
        logger.debug(f"Successfully loaded meta data from {file_path}")
        return data
