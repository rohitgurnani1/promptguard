"""
Quick evaluation example for PromptGuard.
"""

import sys
import os

# Add parent directory to path to import promptguard
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from promptguard.models.openai_client import OpenAIClient
from promptguard.attacks.library import AttackLibrary, SimpleInjectionAttack
from promptguard.defenses.hardening import PromptHardening
from promptguard.defenses.filtering import PromptFiltering
from promptguard.eval.runner import EvaluationRunner
from promptguard.eval.metrics import EvaluationMetrics
from promptguard.utils.logging_utils import setup_logging


def main():
    """Run a quick evaluation example."""
    # Set up logging
    setup_logging()
    
    # Initialize model (requires OPENAI_API_KEY environment variable)
    try:
        model = OpenAIClient()
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set OPENAI_API_KEY environment variable")
        return
    
    # Initialize attack library
    attack_lib = AttackLibrary()
    attack_lib.register(SimpleInjectionAttack())
    
    # Get an attack
    attack = attack_lib.get_attack("simple_injection")
    
    # Initialize defenses
    hardening = PromptHardening()
    filtering = PromptFiltering()
    
    # Initialize evaluation runner
    runner = EvaluationRunner(model)
    
    # Test prompt
    original_prompt = "What is the capital of France?"
    
    print("=" * 60)
    print("Running Quick Evaluation")
    print("=" * 60)
    
    # Test without defense
    print("\n1. Testing attack without defense:")
    result_no_defense = runner.run_evaluation(original_prompt, attack)
    print(f"   Attack successful: {result_no_defense.success}")
    print(f"   Response: {result_no_defense.model_response[:100]}...")
    
    # Test with hardening
    print("\n2. Testing attack with prompt hardening:")
    result_hardening = runner.run_evaluation(original_prompt, attack, hardening)
    print(f"   Attack successful: {result_hardening.success}")
    print(f"   Response: {result_hardening.model_response[:100]}...")
    
    # Test with filtering
    print("\n3. Testing attack with prompt filtering:")
    result_filtering = runner.run_evaluation(original_prompt, attack, filtering)
    print(f"   Attack successful: {result_filtering.success}")
    print(f"   Response: {result_filtering.model_response[:100]}...")
    
    # Calculate metrics
    print("\n" + "=" * 60)
    print("Evaluation Summary")
    print("=" * 60)
    
    results = [result_no_defense, result_hardening, result_filtering]
    metrics = EvaluationMetrics()
    
    defense_stats = metrics.aggregate_by_defense(results)
    for defense_name, stats in defense_stats.items():
        print(f"\n{defense_name}:")
        print(f"  Success Rate: {stats['success_rate']:.2%}")
        print(f"  Successful Defenses: {stats['successful_defenses']}/{stats['total']}")


if __name__ == "__main__":
    main()

