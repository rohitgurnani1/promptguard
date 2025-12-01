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
- [Web UI](#web-ui)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

PromptGuard is a security testing framework designed to help developers, researchers, and organizations evaluate how well their LLM applications are protected against prompt injection attacks. It provides:

- **Comprehensive Attack Library**: 8 different prompt injection attack techniques
- **Multiple Defense Strategies**: Test various defense mechanisms
- **Multi-Model Support**: Evaluate across different LLM providers
- **Detailed Metrics**: Attack success rates, robustness scores, and detailed reports

## ✨ Features

### 🎯 Attack Types

1. **Direct Override** - Classic "ignore previous instructions" attack
2. **Direct Override Paraphrase** - Paraphrased override to bypass naive filters
3. **Persona Jailbreak** - Role-play persona that ignores rules
4. **Sandwich Instruction** - Benign content with malicious instruction in the middle
5. **Indirect Embedded** - Malicious instruction hidden in embedded documents
6. **Indirect Quoted** - Malicious instructions inside quotes
7. **Meta Question** - Asks meta-questions about policies and system prompts
8. **Multi-Step Refinement** - Requests internal rules as "style guidelines"

### 🛡️ Defense Strategies

- **Prompt Hardening**: Strengthens system prompts with explicit priority rules
- **Prompt Filtering**: Detects and flags suspicious patterns in user input
- **Context Isolation**: Separates trusted system context from untrusted content

### 📊 Evaluation Capabilities

- Multi-model evaluation (OpenAI GPT-4o-mini, GPT-5-mini, etc.)
- Batch evaluation across multiple attacks and defenses
- Detailed metrics and reporting
- Export results to JSON/CSV

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
    benign_task_prompt="Summarize this conversation."
)

records, summaries = run_eval(
    model=client,
    attacks=attacks,
    defenses=defenses,
    eval_config=eval_config,
)

# Print results
for summary in summaries:
    print(f"Robustness: {summary.robustness:.2%}")
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

## 🌐 Web UI

The Streamlit web interface provides an interactive way to:

- ✅ Select models, attacks, and defenses
- ✅ Run evaluations with a single click
- ✅ View detailed results and metrics
- ✅ Compare performance across models
- ✅ Export results to JSON/CSV

Launch with:
```bash
streamlit run app.py
```

## 📊 Example Results

```
Defense: prompt_hardening
Total attacks:       8
Successful attacks:  4
Attack success rate: 50.00%
Robustness score:    50.00%

Defense: prompt_filtering
Total attacks:       8
Successful attacks:  3
Attack success rate: 37.50%
Robustness score:    62.50%
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

See [IMPROVEMENTS.md](IMPROVEMENTS.md) for a detailed improvement plan.

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
- Empty responses may occur with certain model/defense combinations
- Rate limiting may affect large batch evaluations

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
- [ ] Async/parallel evaluation
- [ ] Cost tracking
- [ ] Advanced metrics (semantic similarity, etc.)
- [ ] Test suite
- [ ] CI/CD pipeline

---

**Made with ❤️ for LLM security**

