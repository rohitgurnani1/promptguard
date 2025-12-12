# examples/run_quick_eval.py
from promptguard.config import ModelConfig
from promptguard.models.openai_client import OpenAIClient
from promptguard.attacks.library import get_default_attacks
from promptguard.defenses.hardening import PromptHardening
from promptguard.defenses.filtering import PromptFiltering, ContextIsolationDefense
from promptguard.eval.runner import run_eval, EvalConfig
from promptguard.utils.logging_utils import print_records, print_summaries

def main():
    model_cfg = ModelConfig(
        provider="openai",
        model_name="gpt-4o-mini",  # Updated model name
        max_tokens=512,
        temperature=0.1,
    )
    client = OpenAIClient(config=model_cfg)

    attacks = get_default_attacks()
    defenses = [
        PromptHardening(),
        PromptFiltering(),
        ContextIsolationDefense(),
    ]

    eval_config = EvalConfig(
        benign_tasks=["Please summarize the visible content only."]
    )

    records, summaries = run_eval(
        model=client,
        attacks=attacks,
        defenses=defenses,
        eval_config=eval_config,
    )

    print_records(records)
    print_summaries(summaries, defenses=[d.name for d in defenses])

if __name__ == "__main__":
    main()