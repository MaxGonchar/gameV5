"""
Custom exception hierarchy for the interactive story application.

This module defines all custom exceptions used throughout the application,
providing a structured way to handle different types of errors with
appropriate context and details.
"""

# # Standard library imports
from typing import Any, Dict, Optional


class CoreException(Exception):
    """
    Base exception for all application-specific errors.

    Provides structured error handling with message and optional details
    that can be used for logging, debugging, and user feedback.
    """

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize the core exception.

        Args:
            message: Human-readable error message
            details: Optional dictionary with additional context for debugging
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        """String representation of the exception."""
        if self.details:
            return f"{self.message} (Details: {self.details})"
        return self.message

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging or API responses."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "details": self.details,
        }


# =============================================================================
# Data Access Layer Exceptions
# =============================================================================


class DataException(CoreException):
    """Base exception for all data access layer errors."""

    pass


class EntityNotFoundException(DataException):
    """
    Exception raised when a requested entity is not found in the data store.

    Examples:
        - Character not found by ID
        - Story not found by ID
        - Location not found by ID
    """

    pass


class DataValidationException(DataException):
    """
    Exception raised when data validation fails.

    Examples:
        - Invalid character data structure
        - Missing required fields
        - Data type mismatches
    """

    pass


class FileOperationException(DataException):
    """
    Exception raised when file system operations fail.

    Examples:
        - Cannot create directory
        - File permission errors
        - Disk space issues
    """

    pass


class YamlException(DataException):
    """
    Exception raised when YAML parsing or writing fails.

    Examples:
        - Invalid YAML syntax
        - YAML structure validation errors
        - Encoding issues
    """

    pass


# =============================================================================
# Service Layer Exceptions
# =============================================================================


class ServiceException(CoreException):
    """Base exception for all service layer errors."""

    pass


class ExternalServiceException(ServiceException):
    """
    Exception raised when external service communication fails.

    Examples:
        - LLM API timeout
        - API rate limiting
        - Authentication failures
        - Network connectivity issues
    """

    pass


class BusinessLogicException(ServiceException):
    """
    Exception raised when business rules are violated.

    Examples:
        - Invalid story state transitions
        - Character validation failures
        - Story creation constraints
    """

    pass


class LLMCommunicationException(ExternalServiceException):
    """
    Specific exception for LLM communication errors.

    Examples:
        - Model initialization failures
        - Response parsing errors
        - Token limit exceeded
        - Model unavailable
    """

    pass


# =============================================================================
# Configuration and System Exceptions
# =============================================================================


class ConfigurationException(CoreException):
    """
    Exception raised for configuration-related errors.

    Examples:
        - Missing environment variables
        - Invalid configuration values
        - Configuration file not found
    """

    pass


class InitializationException(CoreException):
    """
    Exception raised when application components fail to initialize.

    Examples:
        - Service startup failures
        - Database connection issues
        - Required resources unavailable
    """

    pass


# =============================================================================
# Validation and Input Exceptions
# =============================================================================


class ValidationException(CoreException):
    """
    Exception raised for input validation errors.

    Examples:
        - Invalid request parameters
        - Schema validation failures
        - Type conversion errors
    """

    pass


class AuthenticationException(CoreException):
    """
    Exception raised for authentication and authorization errors.

    Examples:
        - Invalid API keys
        - Permission denied
        - Session expired
    """

    pass


# =============================================================================
# Utility Functions
# =============================================================================


def wrap_exception(
    original_exception: Exception, new_exception_class: type, message: str, **details
) -> CoreException:
    """
    Utility function to wrap a standard exception in a custom exception.

    Args:
        original_exception: The original exception to wrap
        new_exception_class: The custom exception class to use
        message: Custom error message
        **details: Additional context details

    Returns:
        Instance of the new exception class with preserved context

    Example:
        try:
            yaml.safe_load(content)
        except yaml.YAMLError as e:
            raise wrap_exception(
                e, YamlException,
                "Failed to parse YAML file",
                file_path=file_path,
                original_error=str(e)
            )
    """
    details["original_error"] = str(original_exception)
    details["original_type"] = type(original_exception).__name__

    return new_exception_class(message, details)
