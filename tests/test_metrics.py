from promptguard.eval.metrics import AttackEvalRecord, compute_summary


def test_compute_summary_all_success():
    records = [
        AttackEvalRecord(
            attack_name="a1",
            defense_name="d1",
            success=True,
            raw_output="",
        )
        for _ in range(5)
    ]

    summary = compute_summary(records)
    assert summary.total == 5
    assert summary.successes == 5
    assert summary.asr == 1.0
    assert summary.robustness == 0.0


def test_compute_summary_mixed():
    records = [
        AttackEvalRecord(
            attack_name="a1",
            defense_name="d1",
            success=i % 2 == 0,
            raw_output="",
        )
        for i in range(4)
    ]

    summary = compute_summary(records)
    assert summary.total == 4
    assert summary.successes == 2
    assert summary.asr == 0.5
    assert summary.robustness == 0.5
