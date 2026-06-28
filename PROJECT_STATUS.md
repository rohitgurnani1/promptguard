# PromptGuard Project Status

**Last Updated**: June 2026  
**Version**: 0.3.0

## Overview

PromptGuard is a framework for evaluating prompt injection attacks against LLM applications. It ships with a Streamlit UI, FastAPI server, CLI examples, SQLite run history, and regression comparison.

## Current Capabilities

### Attack library (19)

| Category | Attacks |
|----------|---------|
| Direct | `direct_override_basic`, `direct_override_paraphrase`, `sandwich_instruction` |
| Indirect | `indirect_embedded`, `indirect_quoted`, `example_based`, `analogy_attack`, `code_generation` |
| Jailbreak | `persona_jailbreak`, `meta_question`, `multi_step_style`, `hypothetical_scenario`, `reverse_psychology`, `dan_attack` |
| Multi-turn | `multi_turn_gradual`, `multi_turn_context_poison` |
| RAG | `rag_chunk_injection`, `rag_citation_override`, `rag_system_in_doc` |

### Defenses (4)

| Defense | Behavior |
|---------|----------|
| `no_defense` | Baseline — no modification |
| `prompt_hardening` | Adds system-prompt priority instructions |
| `prompt_filtering` | Strips suspicious injection patterns from user input |
| `context_isolation` | Marks quoted/document text as data, not commands |

### Metrics

| Metric | Description |
|--------|-------------|
| ASR | Attack success rate (overall + per-attack) |
| SDS | Semantic deviation from benign baseline |
| Precision / Recall | Defense effectiveness (precision uses benign false positives) |
| Benign FP rate | Benign prompts incorrectly flagged as leaks |
| LSS | Leakage severity on successful attacks |
| Tokens / cost | Usage counts and USD estimates |

### Scorers

- **`heuristic`** — keyword/pattern based (fast, default)
- **`hybrid`** — heuristic first, LLM judge on uncertain cases (balanced cost/accuracy)
- **`llm_judge`** — LLM evaluates each response (most accurate, highest cost)

### Providers

| Provider | Models (examples) | Extra install |
|----------|-------------------|---------------|
| `openai` | gpt-4o-mini, gpt-5-mini, gpt-4o | included |
| `anthropic` | claude-3-5-haiku-latest, claude-3-5-sonnet-latest | `pip install anthropic` |
| `ollama` | llama3.2, mistral, gemma2 | [ollama.com](https://ollama.com) |

### Interfaces

- **Streamlit** — `app.py` (multi-provider, history, regression, export)
- **REST API** — `api.py` via `uvicorn api:app`
- **CLI** — `examples/run_quick_eval.py`, `examples/run_multi_model_eval.py`, `examples/run_preset_eval.py`
- **YAML presets** — `configs/quick.yaml`, `configs/full.yaml`
- **Python API** — `run_eval()`, `load_preset()`, `RunHistoryStore`, `compare_results()`

### Run history

- SQLite store (default: `~/.promptguard/history.db`)
- Save runs from UI or API
- Compare runs for ASR regression in UI and `GET /runs/compare`

## Architecture

```
promptguard/
├── attacks/          # library, multi_turn, rag
├── defenses/         # Defense strategies
├── eval/
│   ├── runner.py     # Parallel evaluation orchestrator
│   ├── metrics.py    # Summaries and metric math
│   ├── heuristics.py # Keyword success detection
│   ├── scorers.py    # Heuristic, hybrid, LLM judge
│   ├── presets.py    # YAML preset loader
│   └── pricing.py    # Token cost estimates
├── history/          # SQLite persistence + regression
├── models/           # OpenAI, Anthropic, Ollama + factory
└── utils/
configs/              # quick.yaml, full.yaml eval presets
api.py                # FastAPI REST server
app.py                # Streamlit UI
```

## Testing & CI

- **58 tests** across attacks, defenses, metrics, runner, scorers, presets, history, API, providers
- **GitHub Actions** — `.github/workflows/ci.yml` runs `pytest` on push/PR to `main`
- Install for dev: `pip install -e ".[dev]"`

## Known limitations

1. **No Gemini provider** yet
2. **LLM judge cost** — doubles API usage when `llm_judge` is enabled (`hybrid` reduces this)
3. **SDS uses word overlap** — not embedding-based semantics
4. **`EvalSummary` lacks `defense_name`** — regression aligns summaries by defense order in records
5. **No Docker** yet (planned)
6. **Streamlit API keys** — entered in sidebar; prefer `st.secrets` in production

## Roadmap

### Next (planned)

- [ ] Docker + docker-compose
- [ ] HTML report export
- [ ] Google Gemini provider
- [ ] `defense_name` on `EvalSummary`
- [ ] GitHub Action: fail PR on ASR regression

### Completed (recent)

- [x] Eval YAML presets (`configs/quick.yaml`, `configs/full.yaml`)
- [x] Multi-turn and RAG injection attacks
- [x] Hybrid scorer (heuristic + judge on uncertain cases)
- [x] Multi-provider support (OpenAI, Anthropic, Ollama)
- [x] Parallel evaluation (`max_concurrency`)
- [x] Benign baseline + real precision
- [x] LLM-as-judge scorer
- [x] Token / cost tracking
- [x] Run history + regression
- [x] FastAPI + CI pipeline
- [x] History DB path fix (PR #2)

## Documentation

| File | Purpose |
|------|---------|
| [README.md](README.md) | Main docs, quick start, API reference |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Hosting Streamlit, API, secrets |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Common issues and fixes |
| [PROJECT_STATUS.md](PROJECT_STATUS.md) | This file |
| [.env.example](.env.example) | Environment variable template |

## Support

1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Run `pytest tests/ -v`
3. Review [README.md](README.md) for usage examples

---

**Status**: Production-ready for internal red-teaming and demos | Actively developed
