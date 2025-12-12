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
    assert summary.num_attacks == 1
    assert "a1" in summary.attack_breakdown
    assert summary.attack_breakdown["a1"] == 1.0


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
    assert summary.num_attacks == 1
    assert summary.attack_breakdown["a1"] == 0.5


def test_compute_summary_multiple_attacks():
    """Test that per-attack breakdown works correctly with multiple attacks."""
    records = [
        AttackEvalRecord(attack_name="a1", defense_name="d1", success=True, raw_output="") for _ in range(3)
    ] + [
        AttackEvalRecord(attack_name="a2", defense_name="d1", success=False, raw_output="") for _ in range(2)
    ]
    
    summary = compute_summary(records)
    assert summary.total == 5
    assert summary.successes == 3
    assert summary.asr == 0.6
    assert summary.num_attacks == 2
    assert summary.attack_breakdown["a1"] == 1.0
    assert summary.attack_breakdown["a2"] == 0.0
