from app.objects.meta import MetaData
from pathlib import Path
from typing import Any, Optional
from .yaml_file_handler import YamlFileHandler


class MetaDAO:
    def __init__(
        self,
        meta_dir: str = "data",
        yaml_handler: Optional[YamlFileHandler] = None,
    ):
        self.meta_dir = Path(meta_dir)
        self.yaml_handler = yaml_handler or YamlFileHandler()

    async def get_meta(self) -> MetaData:
        path = self.meta_dir / "meta.yaml"
        data = await self._read_yaml(path)
        return MetaData(data)

    async def _read_yaml(self, file_path: Path) -> dict[str, Any]:
        data = await self.yaml_handler.read_yaml_file(file_path)
        if not data or not isinstance(data, dict):
            raise ValueError(f"Invalid meta data in {file_path}")
        return data
