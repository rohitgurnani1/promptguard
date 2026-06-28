# examples/run_quick_eval.py
from promptguard.config import ModelConfig
from promptguard.models.factory import create_client
from promptguard.attacks.library import get_default_attacks
from promptguard.defenses.hardening import PromptHardening
from promptguard.defenses.filtering import PromptFiltering, ContextIsolationDefense
from promptguard.defenses.no_defense import NoDefense
from promptguard.eval.runner import run_eval, EvalConfig, DEFAULT_SYSTEM_PROMPT
from promptguard.utils.logging_utils import print_eval_result


def main():
    model_cfg = ModelConfig(
        provider="openai",
        model_name="gpt-4o-mini",
        max_tokens=512,
        temperature=0.1,
    )
    client = create_client(model_cfg)

    attacks = get_default_attacks()
    defenses = [
        NoDefense(),
        PromptHardening(),
        PromptFiltering(),
        ContextIsolationDefense(),
    ]

    eval_config = EvalConfig(
        benign_tasks=["Please summarize the visible content only."],
        system_prompt=DEFAULT_SYSTEM_PROMPT,
    )

    result = run_eval(
        model=client,
        attacks=attacks,
        defenses=defenses,
        eval_config=eval_config,
    )

    print_eval_result(result, defenses=[d.name for d in defenses])


if __name__ == "__main__":
    main()
