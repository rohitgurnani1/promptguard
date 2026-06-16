# promptguard/utils/logging_utils.py
from typing import Iterable, Optional
import logging

from promptguard.eval.metrics import (
    AttackEvalRecord,
    BenignEvalRecord,
    EvalRunResult,
    EvalSummary,
)


def setup_logging(level: Optional[str] = None):
    log_level = level or "INFO"
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def print_records(records: Iterable[AttackEvalRecord]):
    for r in records:
        print("=" * 60)
        print(f"Attack:  {r.attack_name}")
        print(f"Defense: {r.defense_name}")
        print(f"Success: {r.success} (scorer: {r.scorer})")
        if r.total_tokens:
            print(f"Tokens:  {r.total_tokens}")
        print("Output snippet:")
        print(r.raw_output[:300], "...\n")


def print_benign_records(records: Iterable[BenignEvalRecord]):
    for r in records:
        print("=" * 60)
        print(f"Defense: {r.defense_name}")
        print(f"Task:    {r.benign_task}")
        print(f"Leaked:  {r.leaked} (false positive if True)")
        print("Output snippet:")
        print(r.raw_output[:300], "...\n")


def print_summaries(summaries: Iterable[EvalSummary], defenses: list):
    print("\n=== Overall Summary by Defense ===")
    for summary, defense_name in zip(summaries, defenses):
        print(f"\nDefense: {defense_name}")
        print(f"Total attacks:       {summary.total}")
        print(f"Successful attacks:  {summary.successes}")
        print(f"Attack success rate: {summary.asr:.2%}")
        print(f"Number of attack types: {summary.num_attacks}")

        if summary.benign_total:
            print(f"Benign prompts:      {summary.benign_total}")
            print(f"False positives:     {summary.benign_false_positives}")
            print(f"Benign FP rate:      {summary.benign_fp_rate:.2%}")

        if summary.avg_sds is not None:
            print(
                f"Avg Semantic Deviation Score: {summary.avg_sds:.3f} "
                "(0=identical, 1=completely different)"
            )
        if summary.precision is not None:
            print(f"Defense Precision: {summary.precision:.2%}")
        if summary.recall is not None:
            print(f"Defense Recall: {summary.recall:.2%}")
        if summary.avg_lss is not None:
            print(
                f"Avg Leakage Severity Score: {summary.avg_lss:.3f} "
                "(0=no leakage, 1=critical)"
            )
        if summary.total_tokens:
            print(f"Total tokens: {summary.total_tokens}")
        if summary.estimated_cost_usd is not None:
            print(f"Estimated cost: ${summary.estimated_cost_usd:.4f}")

        if summary.attack_breakdown:
            print("\nPer-Attack Success Rates:")
            for attack_name, success_rate in sorted(summary.attack_breakdown.items()):
                print(f"  {attack_name}: {success_rate:.2%}")


def print_eval_result(result: EvalRunResult, defenses: list):
    print_records(result.attack_records)
    if result.benign_records:
        print("\n=== Benign Baseline Results ===")
        print_benign_records(result.benign_records)
    print_summaries(result.summaries, defenses)
