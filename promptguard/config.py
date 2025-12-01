"""
Configuration settings for PromptGuard.
"""

import os
from typing import Optional
from dataclasses import dataclass

@dataclass
class ModelConfig:
    """Configuration for a specific model."""
    provider: str = "openai"
    model_name: str = "gpt-4o-mini"
    max_tokens: int = 512
    temperature: float = 0.2

class Config:
    """Configuration class for PromptGuard settings."""
    
    # OpenAI API settings
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # Evaluation settings
    DEFAULT_TEMPERATURE: float = 0.0
    DEFAULT_MAX_TOKENS: int = 1000
    
    # Logging settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

def get_openai_api_key() -> str:
    """Get OpenAI API key from environment."""
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("Please set OPENAI_API_KEY in your environment.")
    return key
