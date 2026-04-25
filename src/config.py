"""
Application Configuration Module.

This module handles all configuration settings for the Country Information AI Agent.
It loads environment variables from .env file and provides centralized configuration.

Configuration Sources (in order of priority):
    1. Environment variables (highest priority)
    2. .env file (via python-dotenv)
    3. Default values (lowest priority)

All configurable values MUST be declared in .env file!

Environment Variables:
    - OPENAI_API_KEY:Your OpenRouter API key (REQUIRED)
    - OPENROUTER_MODEL:Model name (default: deepseek/deepseek-chat)
    - LLM_TEMPERATURE:Temperature 0.0-1.0 (default: 0.1)
    - LLM_MAX_TOKENS:Max tokens to generate (default: 500)
    - OPENROUTER_URL:API endpoint (default: https://openrouter.ai/api/v1/chat/completions)
    - COUNTRIES_API_URL:REST Countries API base URL
    - COUNTRIES_API_TIMEOUT:Timeout in seconds (default: 10)

Typical Usage:
    >>> from src.config import config
    >>> print(config.openrouter_model)
    deepseek/deepseek-chat
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class Config:
    """
    Application configuration container.
    
    All configurable values are loaded from environment variables.
    This allows easy configuration without code changes.
    """
    
    # ========================================================================
    # API Key (REQUIRED)
    # ========================================================================
    @property
    def api_key(self) -> str:
        """Your OpenRouter API key."""
        return os.environ.get("OPENAI_API_KEY", "")
    
    @property
    def has_api_key(self) -> bool:
        """Check if API key is configured."""
        return bool(self.api_key)
    
    # ========================================================================
    # LLM Configuration
    # ========================================================================
    @property
    def openrouter_model(self) -> str:
        """LLM model to use."""
        return os.environ.get("OPENROUTER_MODEL", "deepseek/deepseek-chat")
    
    @property
    def llm_temperature(self) -> float:
        """Generation temperature (0.0 = deterministic, 1.0 = creative)."""
        try:
            return float(os.environ.get("LLM_TEMPERATURE", "0.1"))
        except ValueError:
            return 0.1
    
    @property
    def llm_max_tokens(self) -> int:
        """Maximum tokens to generate."""
        try:
            return int(os.environ.get("LLM_MAX_TOKENS", "500"))
        except ValueError:
            return 500
    
    @property
    def openrouter_url(self) -> str:
        """OpenRouter API endpoint URL."""
        return os.environ.get("OPENROUTER_URL", "https://openrouter.ai/api/v1/chat/completions")
    
    # ========================================================================
    # REST Countries API Configuration
    # ========================================================================
    @property
    def countries_api_url(self) -> str:
        """REST Countries API base URL."""
        return os.environ.get("COUNTRIES_API_URL", "https://restcountries.com/v3.1/name")
    
    @property
    def countries_api_timeout(self) -> int:
        """API timeout in seconds."""
        try:
            return int(os.environ.get("COUNTRIES_API_TIMEOUT", "10"))
        except ValueError:
            return 10


# ========================================================================
# Singleton Instance
# ========================================================================

config = Config()