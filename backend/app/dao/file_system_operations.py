"""
File system operations utilities.

Provides a centralized set of file and directory operations with
consistent error handling and logging.
"""

from pathlib import Path
from typing import Any, Dict, Union, List
import aiofiles.os
import aioshutil

from app.core.config import get_logger
from .yaml_file_handler import YamlFileHandler

logger = get_logger(__name__)


class FileSystemOperations:
    """
    Centralized file system operations with consistent error handling and logging.
    
    Provides atomic file operations with proper error handling for:
    - Directory creation and deletion
    - Directory copying
    - YAML file operations
    """
    
    async def create_dir(self, path: Path, parents: bool = True, exist_ok: bool = False) -> None:
        """
        Create a directory using async operations.
        
        Args:
            path: Directory path to create
            parents: If True, create parent directories if they don't exist
            exist_ok: If True, don't raise error if directory already exists
            
        Raises:
            OSError: If directory creation fails
        """
        try:
            logger.info("Creating directory: %s", path)
            if parents:
                await aiofiles.os.makedirs(str(path), exist_ok=exist_ok)
            else:
                await aiofiles.os.mkdir(str(path))
            logger.debug("Successfully created directory: %s", path)
        except FileExistsError as e:
            if not exist_ok:
                logger.error("Directory %s already exists: %s", path, e)
                raise OSError(f"Directory {path} already exists: {e}")
        except OSError as e:
            logger.error("Failed to create directory %s: %s", path, e)
            raise OSError(f"Failed to create directory {path}: {e}")
    
    async def copy_dir(self, src: Path, dest: Path, create_if_not_exists: bool = True) -> int:
        """
        Copy directory contents from source to destination using async operations.
        
        Args:
            src: Source directory path
            dest: Destination directory path
            create_if_not_exists: If True, create destination directory if it doesn't exist
            
        Returns:
            Number of files copied (estimated from aioshutil.copytree)
            
        Raises:
            FileNotFoundError: If source directory doesn't exist
            OSError: If copy operation fails
        """
        if not src.exists():
            raise FileNotFoundError(f"Source directory {src} does not exist")
        
        if not src.is_dir():
            raise OSError(f"Source {src} is not a directory")
        
        logger.info("Copying directory from %s to %s", src, dest)
        
        try:
            # Create destination parent directory if needed
            if create_if_not_exists and dest.parent != dest:
                await self.create_dir(dest.parent, parents=True, exist_ok=True)
            
            # Use aioshutil.copytree for efficient async directory copying
            await aioshutil.copytree(str(src), str(dest), dirs_exist_ok=True)
            
            # Count files for feedback (simple approximation)
            files_copied = sum(1 for item in src.rglob('*') if item.is_file())
            
            logger.info("Successfully copied %d files from %s to %s", files_copied, src, dest)
            return files_copied
            
        except Exception as e:
            logger.error("Failed to copy directory from %s to %s: %s", src, dest, e)
            raise OSError(f"Failed to copy directory from {src} to {dest}: {e}")
    
    async def create_yaml_file(
        self, 
        path: Path, 
        content: Union[Dict[str, Any], List[Dict[str, Any]]]
    ) -> None:
        """
        Create a YAML file with the given content using YamlFileHandler.
        
        Args:
            path: File path where YAML will be written
            content: Data to write to YAML file
            
        Raises:
            yaml.YAMLError: If YAML serialization fails
            OSError: If file writing fails
        """
        try:
            logger.info("Creating YAML file: %s", path)
            
            # Ensure parent directory exists
            if path.parent != path:
                await self.create_dir(path.parent, parents=True, exist_ok=True)
            
            # Use existing YamlFileHandler for consistent YAML operations
            yaml_handler = YamlFileHandler()
            await yaml_handler.write_yaml_file(path, content)
                
            logger.debug("Successfully created YAML file: %s", path)
            
        except Exception as e:
            logger.error("Failed to create YAML file %s: %s", path, e)
            raise
    
    async def delete_dir(self, path: Path) -> None:
        """
        Delete a directory and all its contents using async operations.
        
        Args:
            path: Directory path to delete
            
        Raises:
            OSError: If directory deletion fails
            FileNotFoundError: If directory doesn't exist
        """
        try:
            if not path.exists():
                raise FileNotFoundError(f"Directory {path} does not exist")
            
            if not path.is_dir():
                raise OSError(f"Path {path} is not a directory")
            
            logger.info("Deleting directory: %s", path)
            
            # Use aioshutil.rmtree for truly async directory deletion
            await aioshutil.rmtree(str(path))
            logger.debug("Successfully deleted directory: %s", path)
            
        except FileNotFoundError:
            raise
        except Exception as e:
            logger.error("Failed to delete directory %s: %s", path, e)
            raise OSError(f"Failed to delete directory {path}: {e}")