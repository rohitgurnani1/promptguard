from promptguard.eval.metrics import (
    AttackEvalRecord,
    BenignEvalRecord,
    compute_precision_recall,
    compute_summary,
)


def test_compute_summary_all_success():
    records = [
        AttackEvalRecord(attack_name="a1", defense_name="d1", success=True, raw_output="")
        for _ in range(5)
    ]
    summary = compute_summary(records)
    assert summary.total == 5
    assert summary.successes == 5
    assert summary.asr == 1.0


def test_compute_summary_mixed():
    records = [
        AttackEvalRecord(attack_name="a1", defense_name="d1", success=i % 2 == 0, raw_output="")
        for i in range(4)
    ]
    summary = compute_summary(records)
    assert summary.asr == 0.5


def test_compute_precision_recall_with_benign_false_positives():
    attack_records = [
        AttackEvalRecord("a1", "d1", success=False, raw_output=""),  # TP
        AttackEvalRecord("a1", "d1", success=False, raw_output=""),  # TP
        AttackEvalRecord("a1", "d1", success=True, raw_output=""),   # FN
    ]
    benign_records = [
        BenignEvalRecord("d1", "task1", leaked=True, raw_output=""),   # FP
        BenignEvalRecord("d1", "task2", leaked=False, raw_output=""),  # TN
    ]

    precision, recall = compute_precision_recall(attack_records, benign_records)
    assert precision == 2 / 3
    assert recall == 2 / 3


def test_compute_precision_without_benign_defaults_to_one():
    attack_records = [
        AttackEvalRecord("a1", "d1", success=False, raw_output=""),
    ]
    precision, recall = compute_precision_recall(attack_records, None)
    assert precision == 1.0
    assert recall == 1.0


def test_compute_summary_includes_benign_metrics():
    attack_records = [
        AttackEvalRecord("a1", "d1", success=True, raw_output="leak"),
    ]
    benign_records = [
        BenignEvalRecord("d1", "task1", leaked=True, raw_output="oops"),
        BenignEvalRecord("d1", "task2", leaked=False, raw_output="ok"),
    ]

    summary = compute_summary(attack_records, benign_records=benign_records)
    assert summary.benign_total == 2
    assert summary.benign_false_positives == 1
    assert summary.benign_fp_rate == 0.5
    assert summary.precision == 0.0  # 0 TP, 1 FP
