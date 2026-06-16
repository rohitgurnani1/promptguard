from promptguard.eval.metrics import AttackEvalRecord, EvalRunResult, EvalSummary
from promptguard.history.regression import compare_results


def _result(defense: str, attack: str, asr: float, success: bool):
    return EvalRunResult(
        attack_records=[
            AttackEvalRecord(attack, defense, success=success, raw_output=""),
        ],
        summaries=[
            EvalSummary(
                total=1,
                successes=1 if success else 0,
                asr=asr,
                attack_breakdown={attack: 1.0 if success else 0.0},
                num_attacks=1,
                precision=1.0,
                recall=0.0 if success else 1.0,
            )
        ],
    )


def test_compare_detects_asr_regression():
    baseline = _result("d1", "a1", asr=0.0, success=False)
    current = _result("d1", "a1", asr=1.0, success=True)

    report = compare_results(baseline, current)
    assert report.has_regression is True
    assert report.defenses[0].asr_delta == 1.0
    assert len(report.defenses[0].attack_regressions) == 1


def test_compare_no_regression_when_improved():
    baseline = _result("d1", "a1", asr=1.0, success=True)
    current = _result("d1", "a1", asr=0.0, success=False)

    report = compare_results(baseline, current)
    assert report.has_regression is False
    assert report.defenses[0].asr_delta == -1.0
