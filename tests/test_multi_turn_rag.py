from promptguard.attacks.library import get_default_attacks
from promptguard.attacks.multi_turn import MultiTurnGradualAttack
from promptguard.attacks.rag import RAGChunkInjectionAttack


def test_multi_turn_build_messages_has_multiple_turns():
    attack = MultiTurnGradualAttack()
    messages = attack.build_messages("Summarize this.")
    assert len(messages) == 3
    assert messages[0].role == "user"
    assert messages[1].role == "assistant"
    assert messages[2].role == "user"
    assert attack.mode == "multi_turn"


def test_rag_attack_includes_retrieved_doc_framing():
    attack = RAGChunkInjectionAttack()
    prompt = attack.build_user_prompt("Summarize this.")
    assert "[Retrieved Doc 1]" in prompt
    assert attack.mode == "rag"
    assert attack.category == "rag"


def test_new_attacks_registered():
    names = {a.name for a in get_default_attacks()}
    assert "multi_turn_gradual" in names
    assert "multi_turn_context_poison" in names
    assert "rag_chunk_injection" in names
    assert "rag_citation_override" in names
    assert "rag_system_in_doc" in names
