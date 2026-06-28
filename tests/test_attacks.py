from promptguard.attacks.library import get_default_attacks


EXPECTED_ATTACK_NAMES = {
    "direct_override_basic",
    "direct_override_paraphrase",
    "persona_jailbreak",
    "sandwich_instruction",
    "indirect_embedded",
    "indirect_quoted",
    "meta_question",
    "multi_step_style",
    "example_based",
    "analogy_attack",
    "hypothetical_scenario",
    "reverse_psychology",
    "code_generation",
    "dan_attack",
}


def test_get_default_attacks_count_and_names():
    attacks = get_default_attacks()
    assert len(attacks) == 14
    names = {a.name for a in attacks}
    assert names == EXPECTED_ATTACK_NAMES


def test_attacks_build_user_prompt_contains_benign_task():
    attacks = get_default_attacks()
    benign = "Summarize this conversation."
    for attack in attacks:
        prompt = attack.build_user_prompt(benign)
        assert isinstance(prompt, str)
        assert benign in prompt


def test_generate_delegates_to_build_user_prompt():
    attacks = get_default_attacks()
    benign = "Summarize this conversation."
    for attack in attacks:
        assert attack.generate(benign) == attack.build_user_prompt(benign)


def test_attacks_have_categories():
    attacks = get_default_attacks()
    valid_categories = {"direct", "indirect", "jailbreak"}
    for attack in attacks:
        assert attack.category in valid_categories
