"""
General LLM Generation Service for various AI generation tasks.

This service provides a reusable interface for LLM operations across the application.
It handles prompt construction, LLM invocation, and response parsing using LangChain chains.
"""

# # Standard library imports
import logging
from typing import Any, Dict, Optional, Type, TypeVar

# # Third-party imports
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, ValidationError

# # Local application imports
from app.core.config import get_logger
from app.exceptions import DataValidationException, ExternalServiceException

logger = get_logger(__name__)

# Generic type for Pydantic response models
T = TypeVar("T", bound=BaseModel)


# TODO: why only one file uses retry logic?
class LLMCommunicator:
    """
    General tool for LLM-based communication.

    This service provides a standardized interface for:
    - Constructing prompts with system and user messages
    - Invoking LLM models with proper error handling using chains
    - Parsing responses into structured Pydantic models
    - Retry logic for reliability
    """

    def __init__(self, llm_model: BaseChatModel, max_retries: int = 3):
        """
        Initialize the LLM communicator.

        Args:
            llm_model: The chat model to use for generation
            max_retries: Maximum number of retry attempts for failed requests
        """
        self.llm_model = llm_model
        self.max_retries = max_retries

    async def generate_structured_response(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: Type[T],
        additional_context: Optional[Dict[str, Any]] = None,
    ) -> T:
        """
        Generate a structured response using the LLM with LangChain chains.

        Args:
            system_prompt: The system prompt defining the task and behavior
            user_prompt: The user prompt with specific input data
            response_model: Pydantic model class for parsing the response
            additional_context: Optional additional context for error handling

        Returns:
            Parsed response as an instance of the response_model

        Raises:
            DataValidationException: If LLM response cannot be parsed after max retries
            ExternalServiceException: For LLM communication errors
        """
        logger.info(
            f"Generating structured response using model: {response_model.__name__}"
        )

        # Create output parser for the response model
        parser = PydanticOutputParser(pydantic_object=response_model)

        # Get format instructions
        format_instructions = parser.get_format_instructions()

        # Attempt generation with retries
        last_error = None

        for attempt in range(self.max_retries):
            try:
                logger.debug(f"LLM generation attempt {attempt + 1}/{self.max_retries}")

                # Create messages directly to avoid template variable conflicts
                messages = [
                    ("system", f"{system_prompt}\n\n{format_instructions}"),
                    ("human", user_prompt),
                ]

                # Execute the LLM directly with messages
                raw_response = await self.llm_model.ainvoke(messages)

                # Parse the response manually using the parser
                result = parser.parse(raw_response.content)

                logger.info(
                    f"Successfully generated and parsed {response_model.__name__}"
                )
                return result

            except ValidationError as e:
                last_error = e
                logger.warning(
                    f"Pydantic validation error on attempt {attempt + 1}: {e}"
                )

            except Exception as e:
                last_error = e
                logger.warning(f"LLM generation error on attempt {attempt + 1}: {e}")

        # All attempts failed - determine appropriate exception type
        if isinstance(last_error, ValidationError):
            # Pydantic validation failed - response parsing issue
            raise DataValidationException(
                f"Failed to parse LLM response into {response_model.__name__} after {self.max_retries} attempts",
                details={
                    "response_model": response_model.__name__,
                    "max_retries": self.max_retries,
                    "validation_error": str(last_error),
                    "additional_context": additional_context or {},
                },
            )
        else:
            # LLM communication error
            raise ExternalServiceException(
                f"LLM communication failed after {self.max_retries} attempts",
                details={
                    "response_model": response_model.__name__,
                    "max_retries": self.max_retries,
                    "original_error": str(last_error),
                    "additional_context": additional_context or {},
                },
            )

    async def generate_chat_response(self, messages: list[BaseMessage]) -> str:
        """Generate chat response from message chain.

        Args:
            messages: LangChain message chain for conversation

        Returns:
            Generated response string

        Raises:
            ExternalServiceException: For LLM communication errors
        """
        logger.info("Generating chat response from message chain")

        try:
            response = await self.llm_model.ainvoke(messages)
            result = str(response.content)

            logger.info("Successfully generated chat response")
            return result

        except Exception as e:
            logger.error(f"Failed to generate chat response: {e}")
            raise ExternalServiceException(
                "LLM communication failed during chat response generation",
                details={"message_count": len(messages), "original_error": str(e)},
            )
