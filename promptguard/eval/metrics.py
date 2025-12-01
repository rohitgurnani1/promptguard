"""
Evaluation metrics for PromptGuard.
"""

from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class EvaluationResult:
    """Result of a single evaluation."""
    attack_name: str
    defense_name: str
    original_prompt: str
    attack_prompt: str
    defended_prompt: str
    model_response: str
    success: bool
    metadata: Dict[str, Any]


class EvaluationMetrics:
    """Metrics calculator for evaluation results."""
    
    @staticmethod
    def calculate_success_rate(results: List[EvaluationResult]) -> float:
        """
        Calculate the success rate (defense effectiveness).
        
        Args:
            results: List of evaluation results
            
        Returns:
            Success rate as a float between 0 and 1
        """
        if not results:
            return 0.0
        
        successful_defenses = sum(1 for r in results if not r.success)
        return successful_defenses / len(results)
    
    @staticmethod
    def calculate_attack_success_rate(results: List[EvaluationResult]) -> float:
        """
        Calculate the attack success rate.
        
        Args:
            results: List of evaluation results
            
        Returns:
            Attack success rate as a float between 0 and 1
        """
        if not results:
            return 0.0
        
        successful_attacks = sum(1 for r in results if r.success)
        return successful_attacks / len(results)
    
    @staticmethod
    def aggregate_by_defense(results: List[EvaluationResult]) -> Dict[str, Dict[str, Any]]:
        """
        Aggregate results by defense type.
        
        Args:
            results: List of evaluation results
            
        Returns:
            Dictionary mapping defense names to aggregated metrics
        """
        defense_stats = {}
        
        for result in results:
            defense_name = result.defense_name
            if defense_name not in defense_stats:
                defense_stats[defense_name] = {
                    "total": 0,
                    "successful_defenses": 0,
                    "failed_defenses": 0,
                }
            
            defense_stats[defense_name]["total"] += 1
            if not result.success:
                defense_stats[defense_name]["successful_defenses"] += 1
            else:
                defense_stats[defense_name]["failed_defenses"] += 1
        
        # Calculate rates
        for defense_name, stats in defense_stats.items():
            stats["success_rate"] = (
                stats["successful_defenses"] / stats["total"]
                if stats["total"] > 0
                else 0.0
            )
        
        return defense_stats


# Additional classes for run_eval interface
@dataclass
class AttackEvalRecord:
    """Record of an attack evaluation."""
    attack_name: str
    defense_name: str
    success: bool
    raw_output: str

@dataclass
class EvalSummary:
    """Summary of evaluation results."""
    total: int
    successes: int
    asr: float  # Attack Success Rate
    robustness: float  # 1 - ASR

def compute_summary(records: List[AttackEvalRecord]) -> EvalSummary:
    """Compute summary statistics from records."""
    total = len(records)
    successes = sum(1 for r in records if r.success)
    asr = successes / total if total > 0 else 0.0
    robustness = 1.0 - asr
    return EvalSummary(total=total, successes=successes, asr=asr, robustness=robustness)
