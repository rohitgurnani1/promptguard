from promptguard.eval.pricing import estimate_cost_usd


def test_estimate_cost_known_model():
    cost = estimate_cost_usd("gpt-4o-mini", prompt_tokens=1_000_000, completion_tokens=1_000_000)
    assert cost is not None
    assert abs(cost - 0.75) < 0.001


def test_estimate_cost_unknown_model():
    assert estimate_cost_usd("unknown-model", 100, 100) is None
