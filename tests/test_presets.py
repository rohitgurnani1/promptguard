from pathlib import Path

import pytest

from promptguard.eval.presets import (
    load_preset,
    list_bundled_presets,
    resolve_attacks_from_preset,
    resolve_defenses_from_preset,
)


def test_list_bundled_presets():
    presets = list_bundled_presets()
    assert "quick" in presets
    assert "full" in presets


def test_load_quick_preset():
    preset = load_preset("quick")
    assert preset.name == "quick"
    assert preset.model_config.provider == "openai"
    assert preset.eval_config.scorer == "hybrid"
    assert preset.attack_names == [
        "direct_override_basic",
        "persona_jailbreak",
        "rag_chunk_injection",
        "multi_turn_gradual",
    ]


def test_load_full_preset():
    preset = load_preset(Path("configs/full.yaml"))
    assert preset.name == "full"
    assert preset.attack_names is None
    assert len(preset.defense_names) == 4


def test_resolve_preset_objects():
    from promptguard.defenses.hardening import PromptHardening
    from promptguard.defenses.no_defense import NoDefense

    preset = load_preset("quick")
    registry = {
        "no_defense": NoDefense,
        "prompt_hardening": PromptHardening,
    }
    attacks = resolve_attacks_from_preset(preset)
    assert len(attacks) == 4
    defenses = resolve_defenses_from_preset(preset, registry)
    assert len(defenses) == 2
    assert defenses[0].name == "no_defense"


def test_unknown_attack_raises():
    preset = load_preset("quick")
    preset.attack_names = ["not_a_real_attack"]
    with pytest.raises(ValueError, match="Unknown attacks"):
        resolve_attacks_from_preset(preset)
