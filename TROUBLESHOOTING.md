# Troubleshooting

Common issues when running PromptGuard evaluations.

## Setup & installation

### `ModuleNotFoundError: No module named 'promptguard'`

Run tests and scripts from the project root with the package installed:

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

Or ensure `pyproject.toml` is present (sets pytest `pythonpath`).

### Anthropic provider fails on import

```bash
pip install anthropic
export ANTHROPIC_API_KEY=sk-ant-...
```

### Ollama connection error

```
Could not reach Ollama at http://localhost:11434
```

1. Start Ollama: `ollama serve`
2. Pull a model: `ollama pull llama3.2`
3. Confirm `OLLAMA_BASE_URL` matches your Ollama host

---

## Run history

### Crash after evaluation (`Run History` section)

**Symptom:** `os.makedirs` / `PermissionError` when loading history.

**Fix (merged in PR #2):** Update to latest `main`.

**Also check:**

- Do not set `PROMPTGUARD_HISTORY_DB=""` (empty string). Unset it or use a valid path.
- Default path is `~/.promptguard/history.db` — ensure home directory is writable.

### History empty on Streamlit Cloud

Container filesystem may reset on redeploy. History is best-effort on ephemeral hosting.

---

## Evaluation results

### Defenses show higher ASR than baseline

**Possible causes:**

1. **Specific attacks bypass that defense** — check per-attack breakdown.
2. **Heuristic false positive** — model echoes defense language; heuristic tries to filter this.
3. **Benign FP rate high** — check precision; defense may be altering outputs oddly.

**Debug:** Open **Detailed Results** in the UI and read raw model outputs.

### Very low baseline ASR (e.g. 0–10%)

Often **expected** for well-aligned models (GPT-4o-mini, Claude Haiku). Modern models resist many template attacks.

Attacks that still succeed often include `analogy_attack`, `code_generation`, and strong direct overrides.

### High benign false-positive rate

The scorer flagged benign responses as leaks.

- Try **`heuristic`** vs **`llm_judge`** and compare.
- Review benign outputs in detailed results.
- Precision drops when benign FP rate is high.

### Inconsistent results between runs

LLMs are stochastic. Mitigations:

- Lower temperature (default ~0.1–0.2 in configs)
- Run multiple times and compare saved runs via regression
- Use `llm_judge` for more stable success classification (at higher cost)

---

## API errors

### OpenAI `max_tokens` / `temperature` errors

Handled automatically in `OpenAIClient.chat()` for newer models (falls back to `max_completion_tokens`). If you see errors in custom code paths, use `chat()` not legacy `generate()`.

### Rate limits / timeouts

- Reduce `max_concurrency` in eval settings
- Run fewer attacks/defenses per batch
- Add retries (not yet built-in — reduce concurrency as workaround)

### LLM judge doubles cost/time

Each response gets an extra judge API call. Use `scorer="heuristic"` for development; reserve `llm_judge` for final validation.

---

## Debugging tools

### Run the test suite

```bash
pytest tests/ -v
```

### Test the heuristic manually

```python
from promptguard.eval.heuristics import default_success_heuristic

output = "paste model response here"
print(default_success_heuristic(output))  # True = attack succeeded
```

### Test scorers

```python
from promptguard.eval.scorers import HeuristicScorer

scorer = HeuristicScorer()
print(scorer.is_attack_successful(
    "model output",
    system_prompt="You are a helpful assistant.",
    user_prompt="user message",
))
```

### Inspect saved runs

```python
from promptguard.history import RunHistoryStore

store = RunHistoryStore()
for run in store.list_runs(limit=5):
    print(run.id, run.model_name, run.avg_asr)
```

---

## Expected behavior (rules of thumb)

| Scenario | Expected |
|----------|----------|
| Baseline ASR | ~10–40% on aligned models (varies by model + attacks) |
| Good defense | ASR lower than baseline; recall ↑ |
| Benign baseline | FP rate ideally near 0% |
| Precision | Meaningful only when benign baseline is enabled |

---

## What to include in a bug report

1. Provider, model, attacks, defenses, scorer settings
2. Whether benign baseline was enabled
3. Example raw outputs (success vs failure cases)
4. Error traceback (full text)
5. Output of `pytest tests/ -v` if relevant

See also [PROJECT_STATUS.md](PROJECT_STATUS.md) for known limitations.
