# examples/run_multi_model_eval.py
from promptguard.config import ModelConfig
from promptguard.models.openai_client import OpenAIClient
from promptguard.attacks.library import get_default_attacks
from promptguard.defenses.hardening import PromptHardening
from promptguard.defenses.filtering import PromptFiltering
from promptguard.eval.runner import run_eval, EvalConfig
from promptguard.utils.logging_utils import print_records, print_summaries


def build_model_clients():
    """Build a list of model clients for evaluation."""
    configs = [
        ModelConfig(model_name="gpt-4o-mini", max_tokens=512),
        # gpt-5-mini uses reasoning tokens, so we need more tokens for actual output
        ModelConfig(model_name="gpt-5-mini", max_tokens=1024),
        # Add more models as needed:
        # ModelConfig(model_name="gpt-4"),
        # ModelConfig(model_name="gpt-3.5-turbo"),
        # ModelConfig(model_name="gpt-4o"),
    ]
    clients = []
    for cfg in configs:
        clients.append((cfg.model_name, OpenAIClient(config=cfg)))
    return clients


def main():
    """Run multi-model evaluation."""
    print("=" * 70)
    print("Multi-Model Evaluation")
    print("=" * 70)
    
    attacks = get_default_attacks()
    defenses = [
        PromptHardening(),
        PromptFiltering(),
    ]
    eval_config = EvalConfig()  # uses default benign_tasks list

    model_clients = build_model_clients()

    for model_name, client in model_clients:
        print("\n" + "=" * 70)
        print(f"Evaluating model: {model_name}")
        print("=" * 70)

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
