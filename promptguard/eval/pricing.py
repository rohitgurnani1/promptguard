"""Estimated per-token pricing for OpenAI models (USD)."""

from typing import Dict, Optional, Tuple

# Prices per 1M tokens: (input, output)
MODEL_PRICING: Dict[str, Tuple[float, float]] = {
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4o": (2.50, 10.00),
    "gpt-5-mini": (0.15, 0.60),
    "gpt-3.5-turbo": (0.50, 1.50),
    "claude-3-5-haiku-latest": (0.25, 1.25),
    "claude-3-5-sonnet-latest": (3.00, 15.00),
}


def estimate_cost_usd(
    model_name: str,
    prompt_tokens: int,
    completion_tokens: int,
) -> Optional[float]:
    """Estimate API cost from token counts."""
    pricing = MODEL_PRICING.get(model_name)
    if pricing is None:
        return None

    input_rate, output_rate = pricing
    input_cost = (prompt_tokens / 1_000_000) * input_rate
    output_cost = (completion_tokens / 1_000_000) * output_rate
    return input_cost + output_cost
