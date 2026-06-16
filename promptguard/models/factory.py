"""Create LLM clients for supported providers."""

from typing import Dict, Optional

from promptguard.config import ModelConfig
from promptguard.models.base import BaseLLMClient
from promptguard.models.openai_client import OpenAIClient


SUPPORTED_PROVIDERS = ("openai", "anthropic", "ollama")

DEFAULT_MODELS: Dict[str, Dict[str, ModelConfig]] = {
    "openai": {
        "gpt-4o-mini": ModelConfig(provider="openai", model_name="gpt-4o-mini", max_tokens=512),
        "gpt-5-mini": ModelConfig(provider="openai", model_name="gpt-5-mini", max_tokens=1024),
        "gpt-4o": ModelConfig(provider="openai", model_name="gpt-4o", max_tokens=512),
    },
    "anthropic": {
        "claude-3-5-haiku-latest": ModelConfig(
            provider="anthropic", model_name="claude-3-5-haiku-latest", max_tokens=512
        ),
        "claude-3-5-sonnet-latest": ModelConfig(
            provider="anthropic", model_name="claude-3-5-sonnet-latest", max_tokens=512
        ),
    },
    "ollama": {
        "llama3.2": ModelConfig(provider="ollama", model_name="llama3.2", max_tokens=512),
        "mistral": ModelConfig(provider="ollama", model_name="mistral", max_tokens=512),
        "gemma2": ModelConfig(provider="ollama", model_name="gemma2", max_tokens=512),
    },
}


def get_models_for_provider(provider: str) -> Dict[str, ModelConfig]:
    if provider not in DEFAULT_MODELS:
        raise ValueError(f"Unsupported provider: {provider}. Choose from {SUPPORTED_PROVIDERS}")
    return DEFAULT_MODELS[provider]


def create_client(
    config: ModelConfig,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
) -> BaseLLMClient:
    """Instantiate an LLM client for the given provider config."""
    provider = config.provider

    if provider == "openai":
        return OpenAIClient(config=config, api_key=api_key)

    if provider == "anthropic":
        from promptguard.models.anthropic_client import AnthropicClient

        return AnthropicClient(config=config, api_key=api_key)

    if provider == "ollama":
        from promptguard.models.ollama_client import OllamaClient

        return OllamaClient(config=config, base_url=base_url)

    raise ValueError(f"Unsupported provider: {provider}")
