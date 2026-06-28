# 🛡️ PromptGuard

A comprehensive framework for evaluating and defending against prompt injection attacks on Large Language Models (LLMs).

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [REST API](#rest-api)
- [Run History & Regression](#run-history--regression)
- [Architecture](#architecture)
- [Attacks](#attacks)
- [Defenses](#defenses)
- [Metrics](#metrics)
- [Web UI](#web-ui)
- [Configuration](#configuration)
- [Testing](#testing)
- [Contributing](#contributing)
- [Deployment](#deployment)

## 🎯 Overview

PromptGuard is a security testing framework for evaluating how well LLM applications resist prompt injection. It provides:

- **14 attack techniques** across direct, indirect, and jailbreak categories
- **4 defense strategies** including a no-defense baseline
- **Multi-provider support** — OpenAI, Anthropic, and local Ollama models
- **Advanced metrics** — ASR, SDS, precision/recall, benign false-positive rate, LSS, token usage, and cost estimates
- **Run history & regression** — SQLite-backed storage with run-to-run comparison
- **Web UI and REST API** — Streamlit dashboard and FastAPI for CI integration

## ✨ Features

### 🎯 Attack Types (14 Total)

**Direct:** Direct Override, Direct Override Paraphrase, Sandwich Instruction

**Indirect:** Indirect Embedded, Indirect Quoted, Example Based, Analogy Attack, Code Generation

**Jailbreak:** Persona Jailbreak, Meta Question, Multi-Step Refinement, Hypothetical Scenario, Reverse Psychology, DAN Attack

### 🛡️ Defense Strategies

| Defense | Description |
|---------|-------------|
| **No Defense** | Baseline — passes prompts through unchanged |
| **Prompt Hardening** | Adds explicit system-prompt priority rules |
| **Prompt Filtering** | Strips suspicious injection patterns from user input |
| **Context Isolation** | Treats quoted/document content as data, not commands |

### 📊 Evaluation Capabilities

- **Multi-provider evaluation** — OpenAI, Anthropic Claude, Ollama (local)
- **Custom system prompts** — test your actual production prompt
- **Benign baseline suite** — measures false-positive rate for real precision
- **Parallel evaluation** — configurable concurrency (`max_concurrency`, default 5)
- **Success scorers** — keyword heuristic or LLM-as-judge
- **Token & cost tracking** — per-run token counts and USD estimates
- **Run history** — persist results to SQLite for regression analysis
- **Export** — JSON/CSV from the web UI

## 🚀 Installation

### Prerequisites

- Python 3.8+
- API key for your chosen provider (OpenAI or Anthropic), or a running [Ollama](https://ollama.com) instance

### Setup

```bash
git clone https://github.com/rohitgurnani1/promptguard.git
cd promptguard

python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Core install (editable)
pip install -e ".[dev]"

# Optional extras
pip install -e ".[anthropic]"   # Anthropic Claude support
pip install -e ".[api]"         # FastAPI REST server
pip install -e ".[all]"         # Everything
```

### Environment Variables

Copy [.env.example](.env.example) or export directly:

```bash
cp .env.example .env   # then edit

export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"   # optional
export OLLAMA_BASE_URL="http://localhost:11434" # optional
```

## 🏃 Quick Start

### Web UI

```bash
streamlit run app.py
# → http://localhost:8501
```

### CLI Examples

```bash
python -m examples.run_quick_eval
python -m examples.run_multi_model_eval
```

### REST API

```bash
uvicorn api:app --reload --port 8000
# → http://localhost:8000/docs
```

### Run Tests

```bash
pytest tests/ -v
```

## 📖 Usage

### Basic Evaluation

```python
from promptguard.config import ModelConfig
from promptguard.models.factory import create_client
from promptguard.attacks.library import get_default_attacks
from promptguard.defenses.hardening import PromptHardening
from promptguard.defenses.no_defense import NoDefense
from promptguard.eval.runner import run_eval, EvalConfig, DEFAULT_SYSTEM_PROMPT

model_config = ModelConfig(provider="openai", model_name="gpt-4o-mini", max_tokens=512)
client = create_client(model_config)

attacks = get_default_attacks()
defenses = [NoDefense(), PromptHardening()]

eval_config = EvalConfig(
    benign_tasks=["Summarize this conversation."],
    system_prompt=DEFAULT_SYSTEM_PROMPT,
    include_benign_baseline=True,
    scorer="heuristic",       # or "llm_judge"
    max_concurrency=5,
)

result = run_eval(client, attacks, defenses, eval_config)

for summary in result.summaries:
    print(f"ASR: {summary.asr:.2%}")
    print(f"Precision: {summary.precision:.2%}, Recall: {summary.recall:.2%}")
    print(f"Benign FP rate: {summary.benign_fp_rate:.2%}")
    print(f"Tokens: {summary.total_tokens}, Cost: ${summary.estimated_cost_usd:.4f}")
```

### Multi-Provider

```python
from promptguard.models.factory import create_client, get_models_for_provider

# OpenAI
client = create_client(ModelConfig(provider="openai", model_name="gpt-4o-mini"))

# Anthropic (requires: pip install anthropic)
client = create_client(ModelConfig(provider="anthropic", model_name="claude-3-5-haiku-latest"))

# Ollama local (requires: ollama serve && ollama pull llama3.2)
client = create_client(ModelConfig(provider="ollama", model_name="llama3.2"))
```

### Custom Attacks

```python
from promptguard.attacks.base import BaseAttack

class CustomAttack(BaseAttack):
    name = "custom_attack"
    description = "My custom attack"
    category = "direct"

    def build_user_prompt(self, benign_task_prompt: str) -> str:
        return f"{benign_task_prompt}\n\n[Your attack here]"
```

### Custom Defenses

```python
from typing import List
from promptguard.defenses.base import BaseDefense, DefenseContext
from promptguard.models.base import Message

class CustomDefense(BaseDefense):
    def __init__(self):
        super().__init__(name="custom_defense", description="My custom defense")

    def apply(self, ctx: DefenseContext) -> List[Message]:
        return [
            Message(role="system", content=ctx.system_prompt),
            Message(role="user", content=ctx.user_prompt),
        ]
```

## 🌐 REST API

Start the server:

```bash
uvicorn api:app --reload --port 8000
```

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/providers` | GET | List providers, models, attacks, defenses |
| `/eval` | POST | Run an evaluation |
| `/runs` | GET | List saved runs |
| `/runs/{id}` | GET | Get run details |
| `/runs/compare` | GET | Regression comparison (`baseline_id`, `current_id`) |
| `/runs/{id}` | DELETE | Delete a run |

Example:

```bash
curl -X POST http://localhost:8000/eval \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "openai",
    "model_name": "gpt-4o-mini",
    "api_key": "sk-...",
    "attack_names": ["direct_override_basic"],
    "defense_names": ["prompt_hardening", "no_defense"],
    "include_benign_baseline": true,
    "scorer": "heuristic",
    "save_to_history": true
  }'
```

Interactive docs: `http://localhost:8000/docs`

## 📚 Run History & Regression

Runs are stored in SQLite (default: `~/.promptguard/history.db`).

```python
from promptguard.history import RunHistoryStore, compare_results

store = RunHistoryStore()
run_id = store.save("openai", "gpt-4o-mini", {"scorer": "heuristic"}, result)

# Compare two runs
baseline = store.get_result("baseline-run-id")
current = store.get_result("current-run-id")
report = compare_results(baseline, current)

if report.has_regression:
    print("⚠️ ASR increased:", report.summary)
for d in report.defenses:
    print(f"{d.defense_name}: ASR Δ {d.asr_delta:+.2%}")
```

The Streamlit UI includes a **Run History & Regression** section for comparing saved runs visually.

## 🏗️ Architecture

```
promptguard/
├── attacks/              # 14 attack implementations
├── defenses/             # 4 defense strategies
├── eval/
│   ├── runner.py         # Parallel evaluation orchestrator
│   ├── metrics.py        # ASR, SDS, precision/recall, LSS
│   ├── heuristics.py     # Keyword-based success detection
│   ├── scorers.py        # Heuristic + LLM-as-judge scorers
│   └── pricing.py        # Token cost estimates
├── history/
│   ├── store.py          # SQLite run persistence
│   └── regression.py     # Run-to-run comparison
├── models/
│   ├── factory.py        # Multi-provider client factory
│   ├── openai_client.py
│   ├── anthropic_client.py
│   └── ollama_client.py
└── utils/
api.py                    # FastAPI REST server
app.py                    # Streamlit web UI
```

## 🎯 Attacks

Attacks implement `build_user_prompt(benign_task) → str` on the `BaseAttack` interface. See `promptguard/attacks/library.py` for all 14 implementations.

## 🛡️ Defenses

Defenses implement `apply(DefenseContext) → List[Message]`. Each defense receives the system prompt and user prompt (which may contain an injected attack) and returns the message list sent to the model.

## 📊 Metrics

| Metric | Description | Better |
|--------|-------------|--------|
| **ASR** | Attack Success Rate — % of attacks that leaked info | Lower |
| **SDS** | Semantic Deviation Score — output drift from benign baseline (0–1) | Lower |
| **Precision** | TP / (TP + FP) using benign false positives | Higher |
| **Recall** | TP / (TP + FN) — attacks blocked | Higher |
| **Benign FP Rate** | Benign prompts incorrectly flagged as leaks | Lower |
| **LSS** | Leakage Severity Score for successful attacks (0–1) | Lower |
| **Token / Cost** | API usage and estimated USD cost per run | — |

**Scorers:** `heuristic` (fast, keyword-based) or `llm_judge` (more accurate, extra API calls).

## 🌐 Web UI

The Streamlit interface supports:

- Provider selection (OpenAI / Anthropic / Ollama)
- Model, attack, and defense multiselect
- Custom system prompt and benign task
- Benign baseline toggle, scorer choice, concurrency slider
- Save to run history
- Results tables, charts, per-attack breakdowns, advanced metrics
- Run history & regression comparison
- JSON/CSV export

```bash
streamlit run app.py
```

## 🔧 Configuration

### EvalConfig Options

```python
EvalConfig(
    benign_tasks=[...],           # Tasks used as attack carriers
    system_prompt="...",          # System prompt under test
    include_benign_baseline=True, # Run benign-only prompts for precision
    max_concurrency=5,            # Parallel API calls
    scorer="heuristic",           # "heuristic" | "llm_judge"
)
```

### Supported Providers & Models

| Provider | Example Models | Install |
|----------|---------------|---------|
| `openai` | gpt-4o-mini, gpt-5-mini, gpt-4o | included |
| `anthropic` | claude-3-5-haiku-latest, claude-3-5-sonnet-latest | `pip install anthropic` |
| `ollama` | llama3.2, mistral, gemma2 | [ollama.com](https://ollama.com) |

## 🧪 Testing

```bash
pytest tests/ -v        # 40 tests
```

CI runs automatically on push/PR to `main` via GitHub Actions (`.github/workflows/ci.yml`).

## 🤝 Contributing

Contributions welcome! See [PROJECT_STATUS.md](PROJECT_STATUS.md) for current status and [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues.

## 🚀 Deployment

For detailed hosting instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

| Option | Command |
|--------|---------|
| Streamlit Cloud | Push to GitHub → [share.streamlit.io](https://share.streamlit.io) |
| Local demo | `streamlit run app.py` + `ngrok http 8501` |
| REST API | `uvicorn api:app --host 0.0.0.0 --port 8000` |
| Heroku | See `Procfile` and `setup.sh` |

## 🔮 Roadmap

- [x] Anthropic Claude support
- [x] Parallel evaluation
- [x] Cost / token tracking
- [x] LLM-as-judge scorer
- [x] Run history & regression
- [x] REST API & CI pipeline
- [ ] Google Gemini support
- [ ] Multi-turn & RAG injection attacks
- [ ] HTML report export
- [ ] Advanced visualizations (heatmaps, radar charts)

## 📄 License

MIT — see [LICENSE](LICENSE).

## 📚 Resources

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Anthropic API Documentation](https://docs.anthropic.com)
- [Prompt Injection Research](https://arxiv.org/abs/2302.12173)
- [OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/)

---

**Made with ❤️ for LLM security**
