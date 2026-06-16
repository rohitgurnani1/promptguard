"""Serialize and deserialize evaluation results."""

from dataclasses import asdict
from typing import Any, Dict, List

from promptguard.eval.metrics import (
    AttackEvalRecord,
    BenignEvalRecord,
    EvalRunResult,
    EvalSummary,
)


def result_to_dict(result: EvalRunResult) -> Dict[str, Any]:
    return {
        "attack_records": [asdict(r) for r in result.attack_records],
        "benign_records": [asdict(r) for r in result.benign_records],
        "summaries": [asdict(s) for s in result.summaries],
    }


def result_from_dict(data: Dict[str, Any]) -> EvalRunResult:
    return EvalRunResult(
        attack_records=[AttackEvalRecord(**r) for r in data.get("attack_records", [])],
        benign_records=[BenignEvalRecord(**r) for r in data.get("benign_records", [])],
        summaries=[EvalSummary(**s) for s in data.get("summaries", [])],
    )


def config_to_dict(config: Dict[str, Any]) -> Dict[str, Any]:
    return dict(config)
