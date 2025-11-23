"""
Shared YAML utilities for DAO classes.

This module provides common YAML file operations that can be reused
across different DAO implementations.
"""

import yaml
import aiofiles
from typing import Dict, List, Any, Union
from pathlib import Path

from app.exceptions import YamlException, FileOperationException


class YamlFileHandler:
    """
    Utility class for common YAML file operations.
    
    Provides consistent error handling and file operations
    for all DAO classes that work with YAML files.
    """
    
    @staticmethod
    async def read_yaml_file(file_path: Path) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Read a YAML file and return its contents.
        
        Args:
            file_path: Path to the YAML file
            
        Returns:
            Contents of the YAML file as dict or list
            
        Raises:
            FileOperationException: If file doesn't exist or cannot be read
            YamlException: If YAML parsing fails
        """
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
                content = await file.read()
                data = yaml.safe_load(content)
                
                # Return None as empty dict for consistency
                if data is None:
                    return {}
                    
                return data
                    
        except FileNotFoundError as e:
            raise FileOperationException(
                f"YAML file not found: {file_path}",
                details={"file_path": str(file_path), "original_error": str(e)}
            )
        except yaml.YAMLError as e:
            raise YamlException(
                f"Failed to parse YAML file: {file_path}",
                details={"file_path": str(file_path), "yaml_error": str(e)}
            )
        except Exception as e:
            raise FileOperationException(
                f"Unexpected error reading YAML file: {file_path}",
                details={"file_path": str(file_path), "original_error": str(e)}
            )
    
    @staticmethod
    async def write_yaml_file(file_path: Path, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> None:
        """
        Write data to a YAML file.
        
        Args:
            file_path: Path to the YAML file
            data: Data to write to the file
            
        Raises:
            YamlException: If YAML serialization fails
            FileOperationException: If file writing fails
        """
        try:
            yaml_content = yaml.safe_dump(
                data,
                default_flow_style=False,
                sort_keys=False,
                indent=2
            )
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as file:
                await file.write(yaml_content)
        except yaml.YAMLError as e:
            raise YamlException(
                f"Failed to serialize data to YAML: {file_path}",
                details={"file_path": str(file_path), "yaml_error": str(e)}
            )
        except OSError as e:
            raise FileOperationException(
                f"Failed to write YAML file: {file_path}",
                details={"file_path": str(file_path), "os_error": str(e)}
            )
    
    async def read_raw_string(self, file_path: Path) -> str:
        """
        Read the raw string content of a YAML file without parsing.
        
        Args:
            file_path: Path to the YAML file
            
        Returns:
            Raw string content of the file
            
        Raises:
            FileOperationException: If file doesn't exist or cannot be read
        """
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
                content = await file.read()
                return content
        except FileNotFoundError as e:
            raise FileOperationException(
                f"File not found: {file_path}",
                details={"file_path": str(file_path), "original_error": str(e)}
            )
        except Exception as e:
            raise FileOperationException(
                f"Failed to read file: {file_path}",
                details={"file_path": str(file_path), "original_error": str(e)}
            )

