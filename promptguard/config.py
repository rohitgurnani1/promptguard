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

    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    DEFAULT_TEMPERATURE: float = 0.0
    DEFAULT_MAX_TOKENS: int = 1000
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    _history_db_env = os.getenv("PROMPTGUARD_HISTORY_DB")
    HISTORY_DB_PATH: str = (
        _history_db_env
        if _history_db_env
        else os.path.join(os.path.expanduser("~"), ".promptguard", "history.db")
    )


def get_openai_api_key() -> str:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("Please set OPENAI_API_KEY in your environment.")
    return key
