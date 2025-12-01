import pytest

from promptguard.attacks.library import get_default_attacks


def test_get_default_attacks_count_and_names():
    attacks = get_default_attacks()
    assert len(attacks) == 8
    names = {a.name for a in attacks}
    # Basic sanity check on a few expected names
    assert "direct_override" in names
    assert "direct_override_paraphrase" in names
    assert "indirect_embedded" in names
    assert "persona_jailbreak" in names


def test_attacks_build_user_prompt_contains_benign_task():
    attacks = get_default_attacks()
    benign = "Summarize this conversation."
    for attack in attacks:
        prompt = attack.build_user_prompt(benign)
        assert isinstance(prompt, str)
        assert benign in prompt
