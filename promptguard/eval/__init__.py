"""Evaluation module for PromptGuard."""

from .metrics import (
    AttackEvalRecord,
    BenignEvalRecord,
    EvalRunResult,
    EvalSummary,
    compute_summary,
)
from .heuristics import classify_heuristic, default_success_heuristic
from .scorers import HeuristicScorer, HybridScorer, LLMJudgeScorer, get_scorer
from .presets import EvalPreset, load_preset, list_bundled_presets, resolve_attacks_from_preset, resolve_defenses_from_preset
from .runner import run_eval, EvalConfig, DEFAULT_SYSTEM_PROMPT

__all__ = [
    "AttackEvalRecord",
    "BenignEvalRecord",
    "EvalRunResult",
    "EvalSummary",
    "compute_summary",
    "run_eval",
    "EvalConfig",
    "DEFAULT_SYSTEM_PROMPT",
    "classify_heuristic",
    "default_success_heuristic",
    "HeuristicScorer",
    "HybridScorer",
    "LLMJudgeScorer",
    "get_scorer",
    "EvalPreset",
    "load_preset",
    "list_bundled_presets",
    "resolve_attacks_from_preset",
    "resolve_defenses_from_preset",
]
