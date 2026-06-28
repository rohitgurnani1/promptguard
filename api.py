"""FastAPI server for PromptGuard."""

from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from promptguard.attacks.library import get_default_attacks
from promptguard.config import ModelConfig
from promptguard.defenses.filtering import ContextIsolationDefense, PromptFiltering
from promptguard.defenses.hardening import PromptHardening
from promptguard.defenses.no_defense import NoDefense
from promptguard.eval.metrics import EvalRunResult
from promptguard.eval.runner import DEFAULT_SYSTEM_PROMPT, EvalConfig, run_eval
from promptguard.history.regression import compare_results
from promptguard.history.serialization import result_to_dict
from promptguard.history.store import RunHistoryStore
from promptguard.models.factory import DEFAULT_MODELS, SUPPORTED_PROVIDERS, create_client

app = FastAPI(
    title="PromptGuard API",
    description="Evaluate LLM prompt injection defenses programmatically",
    version="0.3.0",
)

DEFENSE_REGISTRY = {
    "no_defense": NoDefense,
    "prompt_hardening": PromptHardening,
    "prompt_filtering": PromptFiltering,
    "context_isolation": ContextIsolationDefense,
}


class EvalRequest(BaseModel):
    provider: str = "openai"
    model_name: str = "gpt-4o-mini"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    max_tokens: int = 512
    temperature: float = 0.2
    system_prompt: str = DEFAULT_SYSTEM_PROMPT
    benign_tasks: List[str] = Field(
        default_factory=lambda: ["Summarize this conversation for a non-technical audience."]
    )
    attack_names: Optional[List[str]] = None
    defense_names: List[str] = Field(
        default_factory=lambda: list(DEFENSE_REGISTRY.keys())
    )
    include_benign_baseline: bool = True
    scorer: str = "heuristic"
    max_concurrency: int = 5
    save_to_history: bool = True


def _get_history_store() -> RunHistoryStore:
    return RunHistoryStore()


def _build_eval_request(req: EvalRequest):
    if req.provider not in SUPPORTED_PROVIDERS:
        raise HTTPException(status_code=400, detail=f"Unsupported provider: {req.provider}")

    model_config = ModelConfig(
        provider=req.provider,
        model_name=req.model_name,
        max_tokens=req.max_tokens,
        temperature=req.temperature,
    )

    all_attacks = {a.name: a for a in get_default_attacks()}
    if req.attack_names:
        missing = [name for name in req.attack_names if name not in all_attacks]
        if missing:
            raise HTTPException(status_code=400, detail=f"Unknown attacks: {missing}")
        attacks = [all_attacks[name] for name in req.attack_names]
    else:
        attacks = list(all_attacks.values())

    missing_defenses = [name for name in req.defense_names if name not in DEFENSE_REGISTRY]
    if missing_defenses:
        raise HTTPException(status_code=400, detail=f"Unknown defenses: {missing_defenses}")
    defenses = [DEFENSE_REGISTRY[name]() for name in req.defense_names]

    eval_config = EvalConfig(
        benign_tasks=req.benign_tasks,
        system_prompt=req.system_prompt,
        include_benign_baseline=req.include_benign_baseline,
        scorer=req.scorer,
        max_concurrency=req.max_concurrency,
    )

    return model_config, attacks, defenses, eval_config


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/providers")
def list_providers():
    return {
        "providers": list(SUPPORTED_PROVIDERS),
        "models": {provider: list(models.keys()) for provider, models in DEFAULT_MODELS.items()},
        "defenses": list(DEFENSE_REGISTRY.keys()),
        "attacks": [a.name for a in get_default_attacks()],
    }


@app.post("/eval")
def run_evaluation(req: EvalRequest):
    model_config, attacks, defenses, eval_config = _build_eval_request(req)

    try:
        client = create_client(model_config, api_key=req.api_key, base_url=req.base_url)
    except (ValueError, ImportError, ConnectionError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    result = run_eval(client, attacks, defenses, eval_config)

    run_id = None
    if req.save_to_history:
        store = _get_history_store()
        config_dict = {
            "provider": req.provider,
            "model_name": req.model_name,
            "system_prompt": req.system_prompt,
            "benign_tasks": req.benign_tasks,
            "attack_names": req.attack_names or [a.name for a in attacks],
            "defense_names": req.defense_names,
            "include_benign_baseline": req.include_benign_baseline,
            "scorer": req.scorer,
            "max_concurrency": req.max_concurrency,
        }
        run_id = store.save(req.provider, req.model_name, config_dict, result)

    return {
        "run_id": run_id,
        "provider": req.provider,
        "model_name": req.model_name,
        "result": result_to_dict(result),
    }


@app.get("/runs")
def list_runs(limit: int = 50):
    store = _get_history_store()
    runs = store.list_runs(limit=limit)
    return {
        "runs": [
            {
                "id": r.id,
                "created_at": r.created_at,
                "provider": r.provider,
                "model_name": r.model_name,
                "scorer": r.scorer,
                "num_attacks": r.num_attacks,
                "num_defenses": r.num_defenses,
                "avg_asr": r.avg_asr,
            }
            for r in runs
        ]
    }


@app.get("/runs/compare")
def compare_runs(baseline_id: str, current_id: str, asr_threshold: float = 0.0):
    store = _get_history_store()
    baseline_record = store.get(baseline_id)
    current_record = store.get(current_id)

    if baseline_record is None:
        raise HTTPException(status_code=404, detail=f"Baseline run not found: {baseline_id}")
    if current_record is None:
        raise HTTPException(status_code=404, detail=f"Current run not found: {current_id}")

    report = compare_results(
        baseline_record["result"],
        current_record["result"],
        baseline_run_id=baseline_id,
        current_run_id=current_id,
        asr_threshold=asr_threshold,
    )

    return {
        "baseline_run_id": report.baseline_run_id,
        "current_run_id": report.current_run_id,
        "has_regression": report.has_regression,
        "summary": report.summary,
        "defenses": [
            {
                "defense_name": d.defense_name,
                "baseline_asr": d.baseline_asr,
                "current_asr": d.current_asr,
                "asr_delta": d.asr_delta,
                "precision_delta": d.precision_delta,
                "recall_delta": d.recall_delta,
                "benign_fp_delta": d.benign_fp_delta,
                "attack_regressions": [
                    {
                        "attack_name": a.attack_name,
                        "baseline_rate": a.baseline_rate,
                        "current_rate": a.current_rate,
                        "delta": a.delta,
                    }
                    for a in d.attack_regressions
                ],
            }
            for d in report.defenses
        ],
    }


@app.get("/runs/{run_id}")
def get_run(run_id: str):
    store = _get_history_store()
    record = store.get(run_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return {
        "id": record["id"],
        "created_at": record["created_at"],
        "provider": record["provider"],
        "model_name": record["model_name"],
        "config": record["config"],
        "result": result_to_dict(record["result"]),
    }


@app.delete("/runs/{run_id}")
def delete_run(run_id: str):
    store = _get_history_store()
    if not store.delete(run_id):
        raise HTTPException(status_code=404, detail="Run not found")
    return {"deleted": run_id}
