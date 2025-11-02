from app.objects.meta import MetaData
from pathlib import Path
from typing import Any, Optional
from .yaml_file_handler import YamlFileHandler


class MetaDAO:
    """
    Data Access Object for meta configurations.
    
    Handles loading meta data from YAML files.
    Structure: {meta_dir}/meta.yaml
    """
    
    def __init__(
        self,
        meta_dir: str = "data",
        yaml_handler: Optional[YamlFileHandler] = None,
    ):
        """
        Initialize the meta DAO.
        
        Args:
            meta_dir: Directory containing meta.yaml file (default: "data")
            yaml_handler: YAML file handler dependency
        """
        self.meta_dir = Path(meta_dir)
        self.yaml_handler = yaml_handler or YamlFileHandler()

    async def get_meta(self) -> MetaData:
        """
        Load meta data from meta.yaml file.
        
        Returns:
            MetaData object
            
        Raises:
            FileNotFoundError: If meta.yaml file doesn't exist
            ValueError: If meta data is invalid
            yaml.YAMLError: If YAML parsing fails
        """
        path = self.meta_dir / "meta.yaml"
        data = await self._read_yaml(path)
        return MetaData(data)

    async def _read_yaml(self, file_path: Path) -> dict[str, Any]:
        data = await self.yaml_handler.read_yaml_file(file_path)
        if not data or not isinstance(data, dict):
            raise ValueError(f"Invalid meta data in {file_path}")
        return data
