# promptguard/utils/logging_utils.py
from typing import Iterable, Optional
import logging
from promptguard.eval.metrics import AttackEvalRecord, EvalSummary

def setup_logging(level: Optional[str] = None):
    """Set up logging configuration."""
    log_level = level or "INFO"
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)

def print_records(records: Iterable[AttackEvalRecord]):
    """Print evaluation records."""
    for r in records:
        print("=" * 60)
        print(f"Attack:  {r.attack_name}")
        print(f"Defense: {r.defense_name}")
        print(f"Success: {r.success}")
        print("Output snippet:")
        print(r.raw_output[:300], "...\n")

def print_summaries(summaries: Iterable[EvalSummary], defenses: list[str]):
    """Print evaluation summaries."""
    print("\n=== Overall Summary by Defense ===")
    for summary, defense_name in zip(summaries, defenses):
        print(f"\nDefense: {defense_name}")
        print(f"Total attacks:       {summary.total}")
        print(f"Successful attacks:  {summary.successes}")
        print(f"Attack success rate: {summary.asr:.2%}")
        print(f"Robustness score:    {summary.robustness:.2%}")