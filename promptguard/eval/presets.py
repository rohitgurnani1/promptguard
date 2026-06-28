"""YAML preset loading for PromptGuard evaluations."""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union

import yaml

from promptguard.attacks.base import BaseAttack
from promptguard.attacks.library import get_default_attacks
from promptguard.config import ModelConfig
from promptguard.defenses.base import BaseDefense
from promptguard.eval.runner import DEFAULT_SYSTEM_PROMPT, EvalConfig

DEFAULT_DEFENSE_NAMES = [
    "no_defense",
    "prompt_hardening",
    "prompt_filtering",
    "context_isolation",
]

BUNDLED_PRESETS_DIR = Path(__file__).resolve().parents[2] / "configs"


@dataclass
class EvalPreset:
    name: str
    description: str
    model_config: ModelConfig
    eval_config: EvalConfig
    attack_names: Optional[List[str]]
    defense_names: List[str]


def _resolve_preset_path(path: Union[str, Path]) -> Path:
    preset_path = Path(path)
    if preset_path.suffix != ".yaml":
        preset_path = Path(f"{path}.yaml")
    if preset_path.exists():
        return preset_path
    bundled = BUNDLED_PRESETS_DIR / preset_path.name
    if bundled.exists():
        return bundled
    raise FileNotFoundError(f"Preset not found: {path}")


def list_bundled_presets() -> List[str]:
    if not BUNDLED_PRESETS_DIR.exists():
        return []
    return sorted(p.stem for p in BUNDLED_PRESETS_DIR.glob("*.yaml"))


def load_preset(path: Union[str, Path]) -> EvalPreset:
    """Load an evaluation preset from a YAML file."""
    preset_path = _resolve_preset_path(path)
    with preset_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}

    name = data.get("name", preset_path.stem)
    description = data.get("description", "")

    model_data = data.get("model", {})
    model_config = ModelConfig(
        provider=model_data.get("provider", "openai"),
        model_name=model_data.get("model_name", "gpt-4o-mini"),
        max_tokens=int(model_data.get("max_tokens", 512)),
        temperature=float(model_data.get("temperature", 0.2)),
    )

    eval_data = data.get("eval", {})
    system_prompt = eval_data.get("system_prompt") or DEFAULT_SYSTEM_PROMPT
    eval_config = EvalConfig(
        benign_tasks=eval_data.get("benign_tasks"),
        system_prompt=system_prompt,
        include_benign_baseline=eval_data.get("include_benign_baseline", True),
        max_concurrency=int(eval_data.get("max_concurrency", 5)),
        scorer=eval_data.get("scorer", "heuristic"),
    )

    attacks_value = data.get("attacks", "all")
    attack_names: Optional[List[str]]
    if attacks_value == "all" or attacks_value is None:
        attack_names = None
    else:
        attack_names = list(attacks_value)

    defense_names = list(data.get("defenses", DEFAULT_DEFENSE_NAMES))

    return EvalPreset(
        name=name,
        description=description,
        model_config=model_config,
        eval_config=eval_config,
        attack_names=attack_names,
        defense_names=defense_names,
    )


def resolve_attacks_from_preset(preset: EvalPreset) -> List[BaseAttack]:
    all_attacks = {a.name: a for a in get_default_attacks()}
    if preset.attack_names:
        missing = [name for name in preset.attack_names if name not in all_attacks]
        if missing:
            raise ValueError(f"Unknown attacks: {missing}")
        return [all_attacks[name] for name in preset.attack_names]
    return list(all_attacks.values())


def resolve_defenses_from_preset(
    preset: EvalPreset,
    defense_registry,
) -> List[BaseDefense]:
    missing = [name for name in preset.defense_names if name not in defense_registry]
    if missing:
        raise ValueError(f"Unknown defenses: {missing}")
    return [defense_registry[name]() for name in preset.defense_names]
