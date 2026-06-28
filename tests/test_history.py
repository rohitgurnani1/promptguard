import tempfile
import os

from promptguard.eval.metrics import AttackEvalRecord, EvalRunResult, EvalSummary
from promptguard.history.serialization import result_from_dict, result_to_dict
from promptguard.history.store import RunHistoryStore


def _sample_result():
    return EvalRunResult(
        attack_records=[
            AttackEvalRecord("a1", "d1", success=False, raw_output="blocked"),
        ],
        summaries=[
            EvalSummary(
                total=1,
                successes=0,
                asr=0.0,
                attack_breakdown={"a1": 0.0},
                num_attacks=1,
            )
        ],
    )


def test_result_roundtrip():
    original = _sample_result()
    restored = result_from_dict(result_to_dict(original))
    assert len(restored.attack_records) == 1
    assert restored.summaries[0].asr == 0.0


def test_history_store_save_and_list():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = os.path.join(tmp, "test.db")
        store = RunHistoryStore(db_path=db_path)
        run_id = store.save("openai", "gpt-4o-mini", {"scorer": "heuristic"}, _sample_result())

        runs = store.list_runs()
        assert len(runs) == 1
        assert runs[0].id == run_id
        assert runs[0].provider == "openai"


def test_history_store_get_and_delete():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = os.path.join(tmp, "test.db")
        store = RunHistoryStore(db_path=db_path)
        run_id = store.save("openai", "gpt-4o-mini", {}, _sample_result())

        record = store.get(run_id)
        assert record is not None
        assert record["model_name"] == "gpt-4o-mini"
        assert store.get_result(run_id).summaries[0].total == 1

        assert store.delete(run_id) is True
        assert store.get(run_id) is None


def test_history_store_bare_filename():
    with tempfile.TemporaryDirectory() as tmp:
        os.chdir(tmp)
        store = RunHistoryStore(db_path="history.db")
        run_id = store.save("openai", "gpt-4o-mini", {}, _sample_result())
        assert store.get(run_id) is not None


def test_resolve_history_db_path_empty_uses_default():
    from promptguard.history.store import resolve_history_db_path

    path = resolve_history_db_path("")
    assert path.endswith("history.db")
    assert ".promptguard" in path
