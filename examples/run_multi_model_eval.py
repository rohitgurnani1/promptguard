# examples/run_multi_model_eval.py
from promptguard.config import ModelConfig
from promptguard.models.factory import create_client
from promptguard.attacks.library import get_default_attacks
from promptguard.defenses.hardening import PromptHardening
from promptguard.defenses.filtering import PromptFiltering
from promptguard.defenses.no_defense import NoDefense
from promptguard.eval.runner import run_eval, EvalConfig
from promptguard.utils.logging_utils import print_eval_result


def build_model_clients():
    """Build a list of model clients for evaluation."""
    configs = [
        ModelConfig(model_name="gpt-4o-mini", max_tokens=512),
        ModelConfig(model_name="gpt-5-mini", max_tokens=1024),
    ]
    clients = []
    for cfg in configs:
        clients.append((cfg.model_name, create_client(cfg)))
    return clients


def main():
    """Run multi-model evaluation."""
    print("=" * 70)
    print("Multi-Model Evaluation")
    print("=" * 70)

    attacks = get_default_attacks()
    defenses = [
        NoDefense(),
        PromptHardening(),
        PromptFiltering(),
    ]
    eval_config = EvalConfig()

    model_clients = build_model_clients()

    for model_name, client in model_clients:
        print("\n" + "=" * 70)
        print(f"Evaluating model: {model_name}")
        print("=" * 70)

        result = run_eval(
            model=client,
            attacks=attacks,
            defenses=defenses,
            eval_config=eval_config,
        )

        print_eval_result(result, defenses=[d.name for d in defenses])


if __name__ == "__main__":
    main()
