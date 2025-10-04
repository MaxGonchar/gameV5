"""
Shared YAML utilities for DAO classes.

This module provides common YAML file operations that can be reused
across different DAO implementations.
"""

import yaml
import aiofiles
from typing import Dict, List, Any, Union
from pathlib import Path


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
            FileNotFoundError: If file doesn't exist
            yaml.YAMLError: If YAML parsing fails
            Exception: For other unexpected errors
        """
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
                content = await file.read()
                data = yaml.safe_load(content)
                
                # Return None as empty dict for consistency
                if data is None:
                    return {}
                    
                return data
                    
        except FileNotFoundError:
            raise FileNotFoundError(f"The file {file_path} does not exist.")
        except yaml.YAMLError as exc:
            raise yaml.YAMLError(f"Error parsing YAML file {file_path}: {exc}")
        except Exception as exc:
            raise Exception(f"An unexpected error occurred while reading {file_path}: {exc}")
    
    @staticmethod
    async def write_yaml_file(file_path: Path, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> None:
        """
        Write data to a YAML file.
        
        Args:
            file_path: Path to the YAML file
            data: Data to write to the file
            
        Raises:
            yaml.YAMLError: If YAML serialization fails
            OSError: If file writing fails
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
        except yaml.YAMLError as exc:
            raise yaml.YAMLError(f"Error writing YAML to file {file_path}: {exc}")
        except OSError as exc:
            raise OSError(f"Error writing file {file_path}: {exc}")
    
    async def read_raw_string(self, file_path: Path) -> str:
        """
        Read the raw string content of a YAML file without parsing.
        
        Args:
            file_path: Path to the YAML file
            
        Returns:
            Raw string content of the file
            
        Raises:
            FileNotFoundError: If file doesn't exist
            Exception: For other unexpected errors
        """
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
                content = await file.read()
                return content
        except FileNotFoundError:
            raise FileNotFoundError(f"The file {file_path} does not exist.")
        except Exception as exc:
            raise Exception(f"An unexpected error occurred while reading {file_path}: {exc}")

