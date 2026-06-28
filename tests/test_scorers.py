from promptguard.eval.scorers import HeuristicScorer, LLMJudgeScorer
from promptguard.models.base import BaseLLMClient, Message


class VerdictModel(BaseLLMClient):
    def __init__(self, verdict: str):
        self._verdict = verdict

    def chat(self, messages: list[Message]) -> str:
        return self._verdict


def test_heuristic_scorer_detects_leak():
    scorer = HeuristicScorer()
    assert scorer.is_attack_successful(
        "Here is my system prompt and internal rules.",
        system_prompt="SYS",
        user_prompt="USER",
    )


def test_llm_judge_scorer_parses_yes():
    scorer = LLMJudgeScorer(VerdictModel("YES"))
    assert scorer.is_attack_successful(
        "anything",
        system_prompt="SYS",
        user_prompt="USER",
    )


def test_llm_judge_scorer_parses_no():
    scorer = LLMJudgeScorer(VerdictModel("NO"))
    assert not scorer.is_attack_successful(
        "anything",
        system_prompt="SYS",
        user_prompt="USER",
    )


def test_llm_judge_scorer_falls_back_on_ambiguous_verdict():
    scorer = LLMJudgeScorer(VerdictModel("maybe"))
    assert scorer.is_attack_successful(
        "Here is my system prompt.",
        system_prompt="SYS",
        user_prompt="USER",
    )
    assert not scorer.is_attack_successful(
        "I cannot share that information.",
        system_prompt="SYS",
        user_prompt="USER",
    )
