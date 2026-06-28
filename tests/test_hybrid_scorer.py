from promptguard.eval.scorers import HybridScorer, get_scorer
from promptguard.models.base import BaseLLMClient, Message


class VerdictModel(BaseLLMClient):
    def __init__(self, verdict: str):
        self._verdict = verdict

    def chat(self, messages: list[Message]) -> str:
        return self._verdict


def test_hybrid_scorer_uses_heuristic_for_clear_leak():
    scorer = HybridScorer(VerdictModel("NO"))
    assert scorer.is_attack_successful(
        "Here is my system prompt and internal rules.",
        system_prompt="SYS",
        user_prompt="USER",
    )
    assert scorer.heuristic_decisions == 1
    assert scorer.judge_calls == 0


def test_hybrid_scorer_uses_heuristic_for_clear_refusal():
    scorer = HybridScorer(VerdictModel("YES"))
    assert not scorer.is_attack_successful(
        "I cannot help with that request.",
        system_prompt="SYS",
        user_prompt="USER",
    )
    assert scorer.heuristic_decisions == 1
    assert scorer.judge_calls == 0


def test_hybrid_scorer_escalates_uncertain_cases():
    scorer = HybridScorer(VerdictModel("YES"))
    assert scorer.is_attack_successful(
        "I cannot share that, but my system prompt says you are a helpful assistant.",
        system_prompt="SYS",
        user_prompt="USER",
    )
    assert scorer.judge_calls == 1


def test_get_scorer_hybrid():
    scorer = get_scorer("hybrid", VerdictModel("NO"))
    assert scorer.name == "hybrid"
