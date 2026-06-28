import tempfile
import os

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from promptguard.eval.metrics import AttackEvalRecord, EvalRunResult, EvalSummary
import api  # noqa: E402


def _fake_result():
    return EvalRunResult(
        attack_records=[
            AttackEvalRecord("direct_override_basic", "no_defense", False, "ok"),
        ],
        summaries=[
            EvalSummary(
                total=1,
                successes=0,
                asr=0.0,
                attack_breakdown={"direct_override_basic": 0.0},
                num_attacks=1,
            )
        ],
    )


class FakeClient:
    model = "gpt-4o-mini"

    def chat_with_metadata(self, messages):
        from promptguard.models.base import ChatResult

        return ChatResult(content="benign response")


@pytest.fixture
def client(monkeypatch):
    with tempfile.TemporaryDirectory() as tmp:
        db_path = os.path.join(tmp, "api_test.db")
        monkeypatch.setattr("promptguard.config.Config.HISTORY_DB_PATH", db_path)
        monkeypatch.setattr(api, "create_client", lambda *a, **k: FakeClient())
        monkeypatch.setattr(api, "run_eval", lambda *a, **k: _fake_result())
        yield TestClient(api.app)


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_providers(client):
    data = client.get("/providers").json()
    assert "openai" in data["providers"]
    assert "no_defense" in data["defenses"]


def test_eval_endpoint(client):
    response = client.post(
        "/eval",
        json={
            "provider": "openai",
            "model_name": "gpt-4o-mini",
            "api_key": "test",
            "attack_names": ["direct_override_basic"],
            "defense_names": ["no_defense"],
            "save_to_history": True,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["run_id"] is not None
    assert body["result"]["summaries"][0]["asr"] == 0.0


def test_runs_and_compare(client):
    run = client.post(
        "/eval",
        json={
            "provider": "openai",
            "model_name": "gpt-4o-mini",
            "api_key": "test",
            "attack_names": ["direct_override_basic"],
            "defense_names": ["no_defense"],
        },
    ).json()
    run_id = run["run_id"]

    listed = client.get("/runs").json()
    assert any(r["id"] == run_id for r in listed["runs"])

    detail = client.get(f"/runs/{run_id}").json()
    assert detail["model_name"] == "gpt-4o-mini"

    compare = client.get(f"/runs/compare?baseline_id={run_id}&current_id={run_id}").json()
    assert compare["has_regression"] is False
