"""
VeniceAI LangChain integration.

Custom implementation of VeniceAI API for LangChain, since there's no official integration.
VeniceAI is OpenAI-compatible but has Venice-specific parameters and features.
"""

from typing import Any, Dict, List, Optional
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.callbacks.manager import CallbackManagerForLLMRun, AsyncCallbackManagerForLLMRun
from pydantic import Field

from .venice_client import VeniceClient


class VeniceAIChatModel(BaseChatModel):
    """
    Custom LangChain integration for VeniceAI API.
    
    Since VeniceAI is OpenAI-compatible, we implement the chat interface
    using their chat/completions endpoint with Venice-specific features.
    """
    
    model: str = Field(alias="model")
    temperature: float = 0
    max_tokens: Optional[int] = None
    timeout: Optional[int] = None
    stop: Optional[List[str]] = None
    max_retries: int = 2
    api_key: str
    llm_client: VeniceClient = None  # Will be set in __post_init__

    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        # Initialize VeniceClient with the provided api_key
        self.llm_client = VeniceClient(self.api_key)

    @property
    def _llm_type(self) -> str:
        """Return identifier for this LLM type."""
        return "venice_ai"
    
    def _convert_message_to_dict(self, message: BaseMessage) -> Dict[str, str]:
        """Convert LangChain message to VeniceAI API format."""
        content = str(message.content) if message.content else ""
        
        if isinstance(message, HumanMessage):
            return {"role": "user", "content": content}
        elif isinstance(message, SystemMessage):
            return {"role": "system", "content": content}
        elif isinstance(message, AIMessage):
            return {"role": "assistant", "content": content}
        else:
            # Fallback for other message types
            return {"role": "user", "content": content}
    
    def _prepare_request_payload(self, messages: List[BaseMessage]) -> Dict[str, Any]:
        """Prepare the request payload for VeniceAI API."""
        venice_messages = [self._convert_message_to_dict(msg) for msg in messages]
        
        payload = {
            "messages": venice_messages,
            "model": self.model,
            "stream": False,
            "temperature": self.temperature,
            "venice_parameters": {
                "include_venice_system_prompt": False
            }
        }
        
        if self.max_tokens is not None:
            payload["max_tokens"] = self.max_tokens
        
        return payload
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """
        Generate chat completion using VeniceAI API.
        
        Args:
            messages: List of messages in the conversation
            stop: List of stop sequences
            run_manager: Callback manager
            **kwargs: Additional arguments
            
        Returns:
            ChatResult with the generated response
        """
        payload = self._prepare_request_payload(messages)
        
        if stop:
            payload["stop"] = stop
        
        # Override any parameters from kwargs
        payload.update(kwargs)

        # For backward compatibility, we'll make this async too
        # Since LangChain expects both sync and async versions
        import asyncio
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If we're already in an async context, we can't use run_until_complete
            # This is a fallback that shouldn't be used in production
            raise RuntimeError("Sync _generate called from async context. Use _agenerate instead.")
        else:
            message_content = loop.run_until_complete(self.llm_client.chat_complete(payload))
        
        message = AIMessage(message_content)
        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])
    
    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """
        Async version of generate method.
        
        Args:
            messages: List of messages in the conversation
            stop: List of stop sequences
            run_manager: Callback manager
            **kwargs: Additional arguments
            
        Returns:
            ChatResult with the generated response
        """
        payload = self._prepare_request_payload(messages)
        
        if stop:
            payload["stop"] = stop
        
        payload.update(kwargs)
        message_content = await self.llm_client.chat_complete(payload)
        message = AIMessage(message_content)
        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])
