"""Regression comparison between evaluation runs."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from promptguard.eval.metrics import EvalRunResult, EvalSummary


@dataclass
class AttackRegression:
    attack_name: str
    baseline_rate: float
    current_rate: float
    delta: float


@dataclass
class DefenseRegression:
    defense_name: str
    baseline_asr: float
    current_asr: float
    asr_delta: float
    baseline_precision: Optional[float]
    current_precision: Optional[float]
    precision_delta: Optional[float]
    baseline_recall: float
    current_recall: float
    recall_delta: float
    baseline_benign_fp_rate: float
    current_benign_fp_rate: float
    benign_fp_delta: float
    attack_regressions: List[AttackRegression] = field(default_factory=list)


@dataclass
class RegressionReport:
    baseline_run_id: str
    current_run_id: str
    defenses: List[DefenseRegression] = field(default_factory=list)
    has_regression: bool = False
    summary: str = ""


def _defense_summaries(result: EvalRunResult) -> Dict[str, EvalSummary]:
    """Map defense name to its summary (summaries follow defense order in run_eval)."""
    defense_names = list(dict.fromkeys(r.defense_name for r in result.attack_records))
    if len(defense_names) != len(result.summaries):
        raise ValueError("Cannot align defense summaries with attack records")
    return {name: summary for name, summary in zip(defense_names, result.summaries)}


def compare_results(
    baseline: EvalRunResult,
    current: EvalRunResult,
    baseline_run_id: str = "baseline",
    current_run_id: str = "current",
    asr_threshold: float = 0.0,
) -> RegressionReport:
    """Compare two eval runs and flag ASR increases per defense/attack."""
    baseline_map = _defense_summaries(baseline)
    current_map = _defense_summaries(current)
    all_defenses = sorted(set(baseline_map) | set(current_map))

    defense_reports: List[DefenseRegression] = []
    has_regression = False

    for defense_name in all_defenses:
        base = baseline_map.get(defense_name)
        curr = current_map.get(defense_name)
        if base is None or curr is None:
            continue

        asr_delta = curr.asr - base.asr
        precision_delta = None
        if base.precision is not None and curr.precision is not None:
            precision_delta = curr.precision - base.precision

        recall_delta = (curr.recall or 0.0) - (base.recall or 0.0)
        benign_fp_delta = curr.benign_fp_rate - base.benign_fp_rate

        attack_regressions: List[AttackRegression] = []
        all_attacks = sorted(set(base.attack_breakdown) | set(curr.attack_breakdown))
        for attack_name in all_attacks:
            base_rate = base.attack_breakdown.get(attack_name, 0.0)
            curr_rate = curr.attack_breakdown.get(attack_name, 0.0)
            delta = curr_rate - base_rate
            if delta > asr_threshold:
                attack_regressions.append(
                    AttackRegression(
                        attack_name=attack_name,
                        baseline_rate=base_rate,
                        current_rate=curr_rate,
                        delta=delta,
                    )
                )

        if asr_delta > asr_threshold or attack_regressions:
            has_regression = True

        defense_reports.append(
            DefenseRegression(
                defense_name=defense_name,
                baseline_asr=base.asr,
                current_asr=curr.asr,
                asr_delta=asr_delta,
                baseline_precision=base.precision,
                current_precision=curr.precision,
                precision_delta=precision_delta,
                baseline_recall=base.recall or 0.0,
                current_recall=curr.recall or 0.0,
                recall_delta=recall_delta,
                baseline_benign_fp_rate=base.benign_fp_rate,
                current_benign_fp_rate=curr.benign_fp_rate,
                benign_fp_delta=benign_fp_delta,
                attack_regressions=attack_regressions,
            )
        )

    if has_regression:
        summary = "Regression detected: attack success rate increased for one or more defenses."
    else:
        summary = "No regression detected compared to baseline run."

    return RegressionReport(
        baseline_run_id=baseline_run_id,
        current_run_id=current_run_id,
        defenses=defense_reports,
        has_regression=has_regression,
        summary=summary,
    )
