import httpx
from app.core.config import get_logger
from app.exceptions import ExternalServiceException, DataValidationException

logger = get_logger(__name__)


# TODO: take a look
class VeniceClient:
    """Venice AI API client with proper exception handling.
    
    Provides methods for embeddings and chat completions with comprehensive
    error handling and logging.
    """
    
    def __init__(self, api_key: str):
        """Initialize Venice AI client.
        
        Args:
            api_key: Venice AI API authentication key
        """
        self.api_key: str = api_key
        self.base_url: str = "https://api.venice.ai/api/v1"
        self.timeout: float = 60.0

    @property
    def headers(self) -> dict:
        """Get HTTP headers for Venice AI API requests.
        
        Returns:
            Dictionary containing authorization and content-type headers
        """
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def embed(self, text: list[str], dimensions: int = 300) -> list[list[float]]:
        """Generate embeddings for text using Venice AI API.
        
        Args:
            text: List of text strings to embed
            dimensions: Embedding dimensions (default 300)
            
        Returns:
            List of embeddings as float arrays
            
        Raises:
            ExternalServiceException: If Venice AI API communication fails
            DataValidationException: If API response format is invalid
        """
        url = f"{self.base_url}/embeddings"
        payload = {
            "encoding_format": "float",
            "input": text,
            "model": "text-embedding-bge-m3",
            "dimensions": dimensions,
        }

        try:
            logger.debug(f"Requesting embeddings for {len(text)} text items with {dimensions} dimensions")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=self.headers, json=payload, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
                
                # Validate response structure
                if "data" not in data:
                    raise DataValidationException(
                        "Venice AI embeddings response missing 'data' field",
                        details={
                            "response_keys": list(data.keys()),
                            "expected_field": "data",
                            "text_count": len(text)
                        }
                    )
                
                embeddings = data["data"]
                embeddings.sort(key=lambda x: x["index"])
                
                result = [embedding["embedding"] for embedding in embeddings]
                logger.debug(f"Successfully generated {len(result)} embeddings")
                return result
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Venice AI embeddings API HTTP error: {e.response.status_code} - {e.response.text}")
            raise ExternalServiceException(
                f"Venice AI embeddings request failed with status {e.response.status_code}",
                details={
                    "status_code": e.response.status_code,
                    "response_text": e.response.text[:500],  # Limit response size
                    "url": url,
                    "text_count": len(text),
                    "dimensions": dimensions
                }
            )
            
        except (httpx.RequestError, httpx.TimeoutException) as e:
            logger.error(f"Venice AI embeddings network error: {e}")
            raise ExternalServiceException(
                "Venice AI embeddings network communication failed",
                details={
                    "error_type": type(e).__name__,
                    "url": url,
                    "timeout": self.timeout,
                    "text_count": len(text),
                    "original_error": str(e)
                }
            )
            
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Venice AI embeddings response parsing error: {e}")
            raise DataValidationException(
                "Failed to parse Venice AI embeddings response",
                details={
                    "parsing_error": str(e),
                    "response_type": type(data).__name__ if 'data' in locals() else "unknown",
                    "text_count": len(text)
                }
            )
    
    async def chat_complete(self, payload: dict) -> str:
        """Complete chat using Venice AI API.
        
        Args:
            payload: Chat completion request payload
            
        Returns:
            Generated chat response content
            
        Raises:
            ExternalServiceException: If Venice AI API communication fails
            DataValidationException: If API response format is invalid
        """
        url = f"{self.base_url}/chat/completions"

        try:
            logger.debug(f"Requesting chat completion with model: {payload.get('model', 'unknown')}")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=self.headers, json=payload, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()

                # Validate and extract response content
                try:
                    content = data["choices"][0]["message"]["content"]
                    logger.debug(f"Successfully received chat response ({len(content)} characters)")
                    return content
                    
                except (IndexError, KeyError, TypeError) as e:
                    raise DataValidationException(
                        "Venice AI chat response has unexpected format",
                        details={
                            "response_structure": {
                                "has_choices": "choices" in data,
                                "choices_count": len(data.get("choices", [])),
                                "first_choice_keys": list(data.get("choices", [{}])[0].keys()) if data.get("choices") else []
                            },
                            "expected_path": "choices[0].message.content",
                            "parsing_error": str(e),
                            "model": payload.get('model', 'unknown')
                        }
                    )
                    
        except httpx.HTTPStatusError as e:
            logger.error(f"Venice AI chat API HTTP error: {e.response.status_code} - {e.response.text}")
            raise ExternalServiceException(
                f"Venice AI chat request failed with status {e.response.status_code}",
                details={
                    "status_code": e.response.status_code,
                    "response_text": e.response.text[:500],  # Limit response size
                    "url": url,
                    "model": payload.get('model', 'unknown'),
                    "message_count": len(payload.get('messages', []))
                }
            )
            
        except (httpx.RequestError, httpx.TimeoutException) as e:
            logger.error(f"Venice AI chat network error: {e}")
            raise ExternalServiceException(
                "Venice AI chat network communication failed",
                details={
                    "error_type": type(e).__name__,
                    "url": url,
                    "timeout": self.timeout,
                    "model": payload.get('model', 'unknown'),
                    "original_error": str(e)
                }
            )