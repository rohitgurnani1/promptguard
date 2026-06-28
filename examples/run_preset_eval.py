"""Run an evaluation from a YAML preset."""

import argparse
import sys

from promptguard.eval.presets import (
    load_preset,
    resolve_attacks_from_preset,
    resolve_defenses_from_preset,
)
from promptguard.eval.runner import run_eval
from promptguard.models.factory import create_client
from promptguard.utils.logging_utils import print_eval_result


def _default_defense_registry():
    from promptguard.defenses.filtering import ContextIsolationDefense, PromptFiltering
    from promptguard.defenses.hardening import PromptHardening
    from promptguard.defenses.no_defense import NoDefense

    return {
        "no_defense": NoDefense,
        "prompt_hardening": PromptHardening,
        "prompt_filtering": PromptFiltering,
        "context_isolation": ContextIsolationDefense,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run PromptGuard eval from a YAML preset")
    parser.add_argument(
        "preset",
        help="Path to preset YAML or bundled name (e.g. quick, configs/quick.yaml)",
    )
    args = parser.parse_args(argv)

    preset_path = args.preset
    if not preset_path.endswith(".yaml"):
        preset_path = f"{preset_path}.yaml"

    preset = load_preset(preset_path)
    registry = _default_defense_registry()
    attacks = resolve_attacks_from_preset(preset)
    defenses = resolve_defenses_from_preset(preset, registry)
    client = create_client(preset.model_config)

    print(f"Running preset: {preset.name} — {preset.description}")
    result = run_eval(client, attacks, defenses, preset.eval_config)
    print_eval_result(result, defenses=[d.name for d in defenses])


if __name__ == "__main__":
    main(sys.argv[1:])
