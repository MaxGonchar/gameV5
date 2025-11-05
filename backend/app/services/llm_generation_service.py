"""
General LLM Generation Service for various AI generation tasks.

This service provides a reusable interface for LLM operations across the application.
It handles prompt construction, LLM invocation, and response parsing using LangChain chains.
"""

import logging
from typing import TypeVar, Type, Any, Dict, Optional
from pydantic import BaseModel, ValidationError
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

logger = logging.getLogger(__name__)

# Generic type for Pydantic response models
T = TypeVar('T', bound=BaseModel)


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
        additional_context: Optional[Dict[str, Any]] = None
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
            ValueError: If LLM response cannot be parsed after max retries
            Exception: For other LLM-related errors
        """
        logger.info(f"Generating structured response using model: {response_model.__name__}")
        
        # Create output parser for the response model
        parser = PydanticOutputParser(pydantic_object=response_model)
        
        # Create chat prompt template with format instructions
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"{system_prompt}\n\n{parser.get_format_instructions()}"),
            ("user", "{user_input}")
        ])
        
        # Create the chain: prompt | llm | parser
        chain = prompt | self.llm_model | parser
        
        # Attempt generation with retries
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"LLM generation attempt {attempt + 1}/{self.max_retries}")
                
                # Execute the chain
                result = await chain.ainvoke({"user_input": user_prompt})
                
                logger.info(f"Successfully generated and parsed {response_model.__name__}")
                return result
                
            except ValidationError as e:
                last_error = e
                logger.warning(f"Validation error on attempt {attempt + 1}: {e}")
                
            except Exception as e:
                last_error = e
                logger.warning(f"LLM generation error on attempt {attempt + 1}: {e}")
        
        # All attempts failed
        context_info = f" (Context: {additional_context})" if additional_context else ""
        error_msg = (
            f"Failed to generate valid {response_model.__name__} after {self.max_retries} attempts. "
            f"Last error: {last_error}{context_info}"
        )
        logger.error(error_msg)
        raise ValueError(error_msg)