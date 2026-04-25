"""
LLM Client Module - OpenRouter API.

This module provides a client for the OpenRouter AI LLM API.
It handles communication with various LLM models for text generation.

API Details:
    - Base URL: https://openrouter.ai/api/v1
    - Endpoint: /chat/completions
    - Model: deepseek/deepseek-chat (configurable)
    
Architecture:
    - Singleton pattern for efficient reuse
    - HTTP/2 support via httpx
    - Proper error handling
    
Authentication:
    - Requires OpenRouter API key in OPENAI_API_KEY env var
    
Typical Usage:
    >>> from src.clients.llm import get_llm_client
    >>> client = get_llm_client()
    >>> response = client.generate("system prompt", "user prompt")
"""

import logging
from typing import Optional

import httpx

from src.config import config

# Configure module logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LLMClientError(Exception):
    """Custom exception for LLM client errors."""
    pass


class LLMClient:
    """
    Client for OpenRouter LLM API.
    
    This class handles all communication with the OpenRouter AI API.
    It provides text generation capabilities using various LLM models.
    
    Configuration (from config):
        - url: API endpoint URL
        - model: Model identifier (OPENROUTER_MODEL env)
        - temperature: Generation temperature (LLM_TEMPERATURE env)
        
    Example:
        >>> client = LLMClient()
        >>> response = client.generate("You are helpful.", "Hi!")
    """
    
    def __init__(self):
        """Initialize the LLM client with configuration."""
        self.url = config.openrouter_url
        self.model = config.openrouter_model
        self.temperature = config.llm_temperature
        self.max_tokens = config.llm_max_tokens
        self.api_key = config.api_key
        self._client = httpx.Client(timeout=30.0)
        logger.info(f"LLMClient initialized with model: {self.model}, max_tokens: {self.max_tokens}")
    
    def generate(
        self,
        system_prompt: str,
        user_prompt: str
    ) -> Optional[str]:
        """
        Generate text using the LLM.
        
        This is the main method for text generation. It sends a prompt
        to the LLM and returns the generated text response.
        
        Args:
            system_prompt: System instructions for the LLM
            user_prompt: User's question or prompt
            
        Returns:
            Generated text response, or None if there was an error
            
        Example:
            >>> client = LLMClient()
            >>> response = client.generate(
            ...     "You are a helpful assistant.",
            ...     "What is the capital of France?"
            ... )
            >>> print(response)
            The capital of France is Paris.
        """
        logger.info(f"Calling LLM ({self.model})...")
        
        if not self.api_key:
            logger.warning("No API key configured - LLM unavailable")
            return None
        
        # Prepare request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        try:
            # Make the API call
            response = self._client.post(self.url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            logger.info(f"LLM response received ({len(content)} chars)")
            return content
        except httpx.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            return None
        except (KeyError, IndexError) as e:
            logger.error(f"Parse error: {e}")
            return None
        except Exception as e:
            logger.error(f"LLM error: {e}")
            return None
    
    def close(self):
        """Close the HTTP client."""
        self._client.close()
        logger.info("LLMClient closed")


# ========================================================================
# Singleton Instance
# ========================================================================

_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """
    Get the singleton LLM client instance.
    
    This function ensures only one LLM client exists,
    which is better for connection pooling and efficiency.
    
    Returns:
        LLMClient instance
        
    Example:
        >>> client = get_llm_client()
        >>> response = client.generate("System", "User question")
    """
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
        logger.info("LLM client singleton created")
    return _llm_client