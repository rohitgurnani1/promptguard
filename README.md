# 🛡️ PromptGuard

A comprehensive framework for evaluating and defending against prompt injection attacks on Large Language Models (LLMs).

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Architecture](#architecture)
- [Attacks](#attacks)
- [Defenses](#defenses)
- [Metrics](#metrics)
- [Web UI](#web-ui)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

PromptGuard is a security testing framework designed to help developers, researchers, and organizations evaluate how well their LLM applications are protected against prompt injection attacks. It provides:

- **Comprehensive Attack Library**: 14 different prompt injection attack techniques
- **Multiple Defense Strategies**: Test various defense mechanisms including baseline (no defense)
- **Multi-Model Support**: Evaluate across different LLM providers (OpenAI GPT-4o-mini, GPT-5-mini, etc.)
- **Advanced Metrics**: Attack success rates, semantic deviation scores, precision/recall, and leakage severity scores

## ✨ Features

### 🎯 Attack Types (14 Total)

**Direct Attacks:**
1. **Direct Override** - Classic "ignore previous instructions" attack
2. **Direct Override Paraphrase** - Paraphrased override to bypass naive filters
3. **Sandwich Instruction** - Benign content with malicious instruction in the middle

**Indirect Attacks:**
4. **Indirect Embedded** - Malicious instruction hidden in embedded documents
5. **Indirect Quoted** - Malicious instructions inside quotes
6. **Example Based** - Asks for examples that reveal internal structure
7. **Analogy Attack** - Uses analogies to extract information indirectly
8. **Code Generation** - Asks model to generate code that reveals its structure

**Jailbreak Attacks:**
9. **Persona Jailbreak** - Role-play persona that ignores rules
10. **Meta Question** - Asks meta-questions about policies and system prompts
11. **Multi-Step Refinement** - Requests internal rules as "style guidelines"
12. **Hypothetical Scenario** - Uses hypothetical scenarios to extract information
13. **Reverse Psychology** - Uses reverse psychology to get information
14. **DAN Attack** - Do Anything Now style attack - bypasses restrictions

### 🛡️ Defense Strategies

- **No Defense** (Baseline): Tests attacks without any defense to establish baseline performance
- **Prompt Hardening**: Strengthens system prompts with explicit priority rules
- **Prompt Filtering**: Detects and flags suspicious patterns in user input
- **Context Isolation**: Separates trusted system context from untrusted content

### 📊 Evaluation Capabilities

- Multi-model evaluation (OpenAI GPT-4o-mini, GPT-5-mini, etc.)
- Batch evaluation across multiple attacks and defenses
- **Advanced Metrics**:
  - Attack Success Rate (ASR) with per-attack breakdowns
  - Semantic Deviation Score (SDS) - measures output deviation from baseline
  - Defense Precision & Recall - measures defense effectiveness
  - Leakage Severity Score (LSS) - measures severity of information leakage
- Export results to JSON/CSV
- Baseline comparison (no defense vs. with defenses)

## 🚀 Installation

### Prerequisites

- Python 3.8+
- OpenAI API key (or other LLM provider API key)

### Setup

1. **Clone the repository**:
```bash
git clone <repository-url>
cd promptguard_project
```

2. **Create a virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install openai python-dotenv streamlit pandas
```

4. **Set up environment variables**:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

Or create a `.env` file:
```
OPENAI_API_KEY=your-api-key-here
```

## 🏃 Quick Start

### Command Line Interface

Run a quick evaluation:

```bash
python -m examples.run_quick_eval
```

Run multi-model evaluation:

```bash
python -m examples.run_multi_model_eval
```

### Web UI (Streamlit)

Launch the interactive web interface:

```bash
streamlit run app.py
```

Then open your browser to `http://localhost:8501`

## 📖 Usage

### Basic Evaluation

```python
from promptguard.config import ModelConfig
from promptguard.models.openai_client import OpenAIClient
from promptguard.attacks.library import get_default_attacks
from promptguard.defenses.hardening import PromptHardening
from promptguard.eval.runner import run_eval, EvalConfig

# Initialize model
model_config = ModelConfig(model_name="gpt-4o-mini", max_tokens=512)
client = OpenAIClient(config=model_config)

# Get attacks and defenses
attacks = get_default_attacks()
defenses = [PromptHardening()]

# Run evaluation
eval_config = EvalConfig(
    benign_tasks=["Summarize this conversation."]
)

records, summaries = run_eval(
    model=client,
    attacks=attacks,
    defenses=defenses,
    eval_config=eval_config,
)

# Print results
for summary in summaries:
    print(f"ASR: {summary.asr:.2%}")
    print(f"Per-attack breakdown: {summary.attack_breakdown}")
    if summary.avg_sds is not None:
        print(f"Avg SDS: {summary.avg_sds:.3f}")
    if summary.precision is not None:
        print(f"Precision: {summary.precision:.2%}, Recall: {summary.recall:.2%}")
    if summary.avg_lss is not None:
        print(f"Avg LSS: {summary.avg_lss:.3f}")
```

### Custom Attacks

```python
from promptguard.attacks.base import BaseAttack

class CustomAttack(BaseAttack):
    def __init__(self):
        super().__init__(
            name="custom_attack",
            description="My custom attack"
        )
    
    def build_user_prompt(self, benign_task_prompt: str) -> str:
        return f"{benign_task_prompt}\n\n[Your attack here]"
```

### Custom Defenses

```python
from promptguard.defenses.base import BaseDefense, DefenseContext
from promptguard.models.base import Message

class CustomDefense(BaseDefense):
    def __init__(self):
        super().__init__(
            name="custom_defense",
            description="My custom defense"
        )
    
    def apply(self, ctx: DefenseContext) -> List[Message]:
        # Your defense logic here
        return [
            Message(role="system", content=ctx.system_prompt),
            Message(role="user", content=ctx.user_prompt),
        ]
```

## 🏗️ Architecture

```
promptguard/
├── attacks/          # Attack implementations
│   ├── base.py      # Base attack interface
│   └── library.py   # Attack library
├── defenses/         # Defense implementations
│   ├── base.py      # Base defense interface
│   ├── hardening.py # Prompt hardening defense
│   └── filtering.py # Input filtering defense
├── eval/            # Evaluation framework
│   ├── runner.py    # Evaluation runner
│   └── metrics.py   # Metrics and summaries
├── models/          # LLM client implementations
│   ├── base.py      # Base model interface
│   └── openai_client.py  # OpenAI client
└── utils/           # Utility functions
    └── logging_utils.py
```

## 🎯 Attacks

### Direct Attacks

Direct attacks attempt to override system instructions explicitly:

- **Direct Override**: "Ignore all previous instructions..."
- **Direct Override Paraphrase**: Paraphrased versions to bypass filters
- **Sandwich Instruction**: Malicious instruction sandwiched between benign content

### Indirect Attacks

Indirect attacks hide malicious instructions in seemingly benign content:

- **Indirect Embedded**: Instructions in document excerpts
- **Indirect Quoted**: Instructions inside quoted text

### Jailbreak Attacks

Jailbreak attacks attempt to reframe the model's context:

- **Persona Jailbreak**: Role-play scenarios
- **Meta Question**: Questions about internal policies
- **Multi-Step Refinement**: Requests for "style guidelines"

## 🛡️ Defenses

### No Defense (Baseline)

Establishes baseline performance for comparison:

```python
from promptguard.defenses.no_defense import NoDefense

defense = NoDefense()  # Passes prompts through unchanged
```

### Prompt Hardening

Adds explicit instructions to prioritize system prompts over user input:

```python
from promptguard.defenses.hardening import PromptHardening

defense = PromptHardening()
```

### Prompt Filtering

Detects and flags suspicious patterns in user input:

```python
from promptguard.defenses.filtering import PromptFiltering

defense = PromptFiltering()
```

### Context Isolation

Separates trusted system context from untrusted embedded content:

```python
from promptguard.defenses.filtering import ContextIsolationDefense

defense = ContextIsolationDefense()
```

## 📊 Metrics

### Attack Success Rate (ASR)

The percentage of attacks that successfully extracted information:
- **Overall ASR**: Across all attacks
- **Per-Attack ASR**: Breakdown by attack type
- **Lower is better**: Indicates stronger defense

### Semantic Deviation Score (SDS)

Measures how much the model's output deviates from the expected baseline response:
- **Range**: 0 (identical) to 1 (completely different)
- **Use**: Detects when attacks cause semantic drift
- **Lower is better**: Indicates defense maintains normal behavior

### Defense Precision & Recall

Standard classification metrics adapted for defense evaluation:
- **Precision**: Accuracy of defense blocking (when it blocks, is it correct?)
- **Recall**: Coverage of defense blocking (how many attacks did it catch?)
- **Higher is better**: Indicates more effective defense

### Leakage Severity Score (LSS)

Quantifies the severity of information leaked during successful attacks:
- **Range**: 0 (no leakage) to 1 (critical leakage)
- **Use**: Prioritize fixing high-severity leaks
- **Lower is better**: Indicates less severe information exposure

For detailed metric documentation, see [NEW_METRICS_IMPLEMENTATION.md](NEW_METRICS_IMPLEMENTATION.md).

## 🌐 Web UI

The Streamlit web interface provides an interactive way to:

- ✅ Select models, attacks, and defenses (including baseline "no defense")
- ✅ Run evaluations with a single click
- ✅ View detailed results and advanced metrics (ASR, SDS, Precision/Recall, LSS)
- ✅ Per-attack breakdown visualization
- ✅ Compare performance across models and defenses
- ✅ Export results to JSON/CSV
- ✅ Real-time progress tracking

Launch with:
```bash
streamlit run app.py
```

## 📊 Example Results

```
Defense: no_defense (Baseline)
Total attacks:       14
Successful attacks:  3
Attack success rate: 21.43%
Attack breakdown:    {'analogy_attack': 100.0%, 'code_generation': 100.0%, ...}

Defense: prompt_hardening
Total attacks:       14
Successful attacks:  1
Attack success rate: 7.14%
Avg SDS:             0.45
Precision:           100.00%
Recall:              92.86%
Avg LSS:             0.85

Defense: prompt_filtering
Total attacks:       14
Successful attacks:  2
Attack success rate: 14.29%
Avg SDS:             0.52
Precision:           100.00%
Recall:              85.71%
Avg LSS:             0.78
```

## 🔧 Configuration

### Model Configuration

```python
from promptguard.config import ModelConfig

config = ModelConfig(
    provider="openai",
    model_name="gpt-4o-mini",
    max_tokens=512,
    temperature=0.2
)
```

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_MODEL`: Default model name (optional)
- `LOG_LEVEL`: Logging level (optional)

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- Additional attack types
- New defense strategies
- Support for more LLM providers (Anthropic, Google, etc.)
- Better evaluation metrics
- Test coverage
- Documentation improvements

See [IMPROVEMENTS_SUMMARY.md](IMPROVEMENTS_SUMMARY.md) for completed improvements and [PROJECT_STATUS.md](PROJECT_STATUS.md) for current project status.

## 📝 License

[Add your license here]

## 🙏 Acknowledgments

- Inspired by research on prompt injection attacks
- Built with OpenAI's API
- Uses Streamlit for the web interface

## 📚 Resources

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Prompt Injection Research](https://arxiv.org/abs/2302.12173)
- [OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/)

## 🐛 Known Issues

- Some models (like GPT-5-mini) require more tokens due to reasoning tokens
- Rate limiting may affect large batch evaluations
- Modern well-aligned models (GPT-4o-mini, GPT-5-mini) have naturally low baseline ASR (10-30%), which is expected and indicates good security

## 🚀 Deployment & Hosting

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

### Quick Options:

1. **Streamlit Cloud** (Recommended): Free, easy, automatic HTTPS
   - Push to GitHub → Deploy at [share.streamlit.io](https://share.streamlit.io)
   
2. **ngrok** (Quick demo): Create public tunnel for local app
   ```bash
   streamlit run app.py
   ngrok http 8501
   ```

3. **Heroku**: Production-ready hosting
   - See `Procfile` and `setup.sh` in repo

## 🔮 Future Enhancements

- [ ] Support for Anthropic Claude
- [ ] Support for Google Gemini
- [ ] Async/parallel evaluation (5-10x speedup)
- [ ] Cost tracking and token usage analytics
- [ ] LLM-based success heuristic (more accurate than keyword matching)
- [ ] Historical result tracking and comparison
- [ ] Advanced visualizations (heatmaps, radar charts)
- [ ] Test suite expansion
- [ ] CI/CD pipeline

---

**Made with ❤️ for LLM security**

