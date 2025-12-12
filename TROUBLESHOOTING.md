# Troubleshooting Evaluation Issues

## Common Issues and Fixes

### Issue 1: Defenses Showing Higher ASR Than Baseline

**Symptoms**: When testing with defenses, ASR is higher than without defenses.

**Possible Causes**:
1. **Defense Echo Detection**: The heuristic might be incorrectly detecting defense language as leaks
   - **Fix**: Already implemented - heuristic now ignores defense phrases
   
2. **Baseline Computation**: Baseline might be computed with wrong defense
   - **Fix**: Already fixed - baseline now always uses no defense

3. **Heuristic Too Strict**: Heuristic might be missing actual leaks
   - **Check**: Run `python diagnose_eval.py` to test heuristic

### Issue 2: Very Low Baseline ASR

**Symptoms**: Even without defenses, very few attacks succeed (e.g., 2/14 attacks).

**Possible Causes**:
1. **Models Are Well-Aligned**: Modern LLMs (GPT-4o-mini, GPT-5-mini) are naturally resistant
   - **This is actually good!** It means the models are secure
   - **Expected**: 20-40% baseline ASR is reasonable for well-aligned models

2. **Attacks Too Weak**: Attacks might not be aggressive enough
   - **Fix**: Already improved - attacks are now stronger

3. **Heuristic Too Strict**: Might be missing subtle leaks
   - **Check**: Look at actual outputs in UI to see if attacks are working but not detected

### Issue 3: Inconsistent Results

**Symptoms**: Same attack/defense combination gives different results.

**Possible Causes**:
1. **Non-Deterministic Model**: LLMs are stochastic
   - **Expected**: Some variation is normal
   - **Solution**: Run multiple evaluations and average

2. **Temperature Setting**: Higher temperature = more variation
   - **Check**: Current temperature is 0.1 (should be fairly deterministic)

## Diagnostic Tools

### Run Diagnostic Script

```bash
python diagnose_eval.py
```

This will:
- Test evaluation logic with mock model
- Show per-attack breakdowns
- Test heuristic detection
- Compare baseline vs. defense results

### Check Actual Outputs

In the Streamlit UI:
1. Go to "Detailed Results" section
2. Expand each attack/defense combination
3. Check the actual model outputs
4. Verify if heuristic is correctly classifying them

### Manual Heuristic Test

```python
from promptguard.eval.runner import default_success_heuristic

# Test specific outputs
output = "Your actual model output here"
result = default_success_heuristic(output)
print(f"Attack succeeded: {result}")
```

## Expected Behavior

### Baseline (No Defense)
- **ASR**: 20-50% (depends on model alignment)
- **Successful Attacks**: Should include direct attacks and some indirect ones
- **Common Winners**: `analogy_attack`, `code_generation`, `direct_override_basic`

### With Defenses
- **ASR**: Should be LOWER than baseline
- **Reduction**: 50-80% reduction in ASR is good
- **Example**: If baseline is 40%, defense should bring it to 10-20%

### Per-Attack Breakdown
- Some attacks should have 0% success (defense working)
- Some attacks might still have 100% success (defense not effective against that attack)
- This is normal - different attacks work differently

## What to Report

If you're still seeing issues, please provide:

1. **Specific weirdness**: What exactly looks wrong?
   - ASR numbers that don't make sense?
   - Attacks marked as successful when they shouldn't be?
   - Defenses showing higher ASR than baseline?

2. **Actual outputs**: Copy a few example outputs from the UI
   - One that's marked as "successful" but shouldn't be
   - One that's marked as "failed" but should be successful

3. **Configuration**: 
   - Which models?
   - Which attacks?
   - Which defenses?
   - What benign task?

4. **Run diagnostic**: 
   ```bash
   python diagnose_eval.py
   ```
   Share the output

## Quick Checks

✅ **Heuristic working?**
- Run: `python diagnose_eval.py`
- Check "HEURISTIC TEST" section - all should be ✅

✅ **Defense reducing ASR?**
- Compare baseline vs. defense ASR
- Defense ASR should be lower

✅ **Records correct?**
- Total records = attacks × defenses × benign_tasks
- Each defense should have same number of records

✅ **Attack names match?**
- Check attack names in breakdown match selected attacks
- No typos or mismatches

