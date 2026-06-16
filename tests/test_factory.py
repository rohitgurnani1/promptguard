import pytest

from promptguard.config import ModelConfig
from promptguard.models.factory import (
    SUPPORTED_PROVIDERS,
    create_client,
    get_models_for_provider,
)
from promptguard.models.openai_client import OpenAIClient


def test_supported_providers():
    assert "openai" in SUPPORTED_PROVIDERS
    assert "anthropic" in SUPPORTED_PROVIDERS
    assert "ollama" in SUPPORTED_PROVIDERS


def test_get_models_for_provider():
    openai_models = get_models_for_provider("openai")
    assert "gpt-4o-mini" in openai_models
    assert openai_models["gpt-4o-mini"].provider == "openai"


def test_create_openai_client():
    client = create_client(
        ModelConfig(provider="openai", model_name="gpt-4o-mini"),
        api_key="test-key",
    )
    assert isinstance(client, OpenAIClient)


def test_create_anthropic_requires_package():
    with pytest.raises(ImportError, match="anthropic"):
        create_client(
            ModelConfig(provider="anthropic", model_name="claude-3-5-haiku-latest"),
            api_key="test-key",
        )
