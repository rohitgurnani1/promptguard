from promptguard.eval.runner import run_eval, EvalConfig
from promptguard.attacks.library import get_default_attacks
from promptguard.defenses.hardening import PromptHardening
from promptguard.defenses.filtering import PromptFiltering
from promptguard.models.base import BaseLLMClient, Message


class FakeModel(BaseLLMClient):
    """Fake model that always returns a string containing a keyword.

    This makes the default_success_heuristic treat all attacks as successful.
    """

    def chat(self, messages: list[Message]) -> str:
        # We don't care about the content for this test; just return something
        # that triggers the heuristic (contains "system prompt").
        return "This response describes the system prompt and internal rules."


def test_run_eval_shapes_and_success_flags():
    model = FakeModel()
    attacks = get_default_attacks()
    defenses = [PromptHardening(), PromptFiltering()]

    # Use a single benign task to keep the record count predictable
    eval_config = EvalConfig(benign_tasks=["Summarize this conversation."])

    records, summaries = run_eval(
        model=model,
        attacks=attacks,
        defenses=defenses,
        eval_config=eval_config,
    )

    # There should be (#defenses * #attacks * #benign_tasks) records
    assert len(records) == len(defenses) * len(attacks) * len(eval_config.benign_tasks)

    # All attacks should be marked as successful according to the heuristic
    assert all(r.success for r in records)

    # One summary per defense
    assert len(summaries) == len(defenses)
    for summary in summaries:
        # All attacks successful, so ASR=1.0 and robustness=0.0
        assert summary.asr == 1.0
        assert summary.robustness == 0.0
