# Deployment Guide

How to run PromptGuard locally, in the cloud, and as a REST API.

## Prerequisites

- Python 3.8+
- Provider credentials (see [.env.example](.env.example))

```bash
git clone https://github.com/rohitgurnani1/promptguard.git
cd promptguard
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[all]"   # or: pip install -r requirements.txt
cp .env.example .env      # edit with your keys
```

---

## Local development

### Streamlit UI

```bash
streamlit run app.py
# → http://localhost:8501
```

### REST API

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
# → http://localhost:8000/docs
```

### CLI examples

```bash
python -m examples.run_quick_eval
python -m examples.run_multi_model_eval
```

---

## Environment variables

| Variable | Required for | Default |
|----------|--------------|---------|
| `OPENAI_API_KEY` | OpenAI provider | — |
| `ANTHROPIC_API_KEY` | Anthropic provider | — |
| `OLLAMA_BASE_URL` | Ollama provider | `http://localhost:11434` |
| `PROMPTGUARD_HISTORY_DB` | Run history path | `~/.promptguard/history.db` |
| `LOG_LEVEL` | Logging | `INFO` |

See [.env.example](.env.example) for a full template.

**Ollama (local):**

```bash
ollama serve
ollama pull llama3.2
# Select provider "ollama" in the UI — no API key needed
```

---

## Streamlit Cloud (recommended for demos)

1. Push the repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**.
3. Set **Main file path** to `app.py`.
4. Add secrets under **Settings → Secrets**:

```toml
OPENAI_API_KEY = "sk-..."
ANTHROPIC_API_KEY = "sk-ant-..."   # optional
OLLAMA_BASE_URL = "http://..."     # only if Ollama is reachable from cloud (usually N/A)
```

5. Deploy — URL will be `https://<app-name>.streamlit.app`.

**Notes:**

- Use Streamlit secrets for API keys; never commit keys to git.
- Ollama generally does not work on Streamlit Cloud (needs local network). Use OpenAI or Anthropic there.
- Run history writes to the container filesystem and may not persist across redeploys unless you mount storage.

---

## REST API in production

### Run with uvicorn

```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 2
```

### Behind a reverse proxy (nginx example)

```nginx
location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

### Security checklist

- [ ] Set provider API keys via environment, not request body, in production
- [ ] Add authentication (API key header) before exposing `/eval` publicly
- [ ] Rate-limit `/eval` — each call makes many LLM requests
- [ ] Set OpenAI/Anthropic spending limits
- [ ] Do not expose Streamlit/API without TLS

---

## Heroku

The repo includes `Procfile` and `setup.sh`:

```
web: sh setup.sh && streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

```bash
heroku create your-app-name
heroku config:set OPENAI_API_KEY=sk-...
git push heroku main
```

For the API instead of Streamlit, change the `Procfile` command to:

```
web: uvicorn api:app --host 0.0.0.0 --port $PORT
```

---

## ngrok (quick public demo)

```bash
streamlit run app.py &
ngrok http 8501
# Share the HTTPS URL ngrok prints
```

Free tier URLs change each session.

---

## AWS / GCP / Azure (VM)

1. Provision a small VM (Ubuntu).
2. Install Python, clone repo, `pip install -e ".[all]"`.
3. Run Streamlit or uvicorn bound to `0.0.0.0`.
4. Open firewall port (8501 or 8000) or put nginx + TLS in front.

```bash
nohup streamlit run app.py --server.port=8501 --server.address=0.0.0.0 &
# or
nohup uvicorn api:app --host 0.0.0.0 --port 8000 &
```

---

## Presentation tips

### Before demo

- Run one eval end-to-end with your API key.
- Pick 2–3 attacks and 2 defenses to showcase.
- Have screenshots or a backup recording.

### During demo

1. Explain prompt injection risk (30s).
2. Walk sidebar: **provider**, models, **14 attacks**, **4 defenses**, scorer, benign baseline (1 min).
3. Run eval — show ASR, precision/recall, benign FP rate (2 min).
4. Open **Run History & Regression** if you have saved runs (1 min).
5. Q&A.

### Metrics to mention

- **ASR** — lower is better (fewer successful attacks)
- **Precision / Recall** — defense accuracy (precision uses benign false positives)
- **Benign FP rate** — lower is better (defense not over-blocking)

---

## Troubleshooting deployment

| Problem | Fix |
|---------|-----|
| App won't start | Check `pip install -e ".[dev]"`, port not in use |
| API 400 on eval | Verify provider API key and model name |
| Ollama connection error | Run `ollama serve`, check `OLLAMA_BASE_URL` |
| History section crashes | Pull latest `main` (PR #2 fix); don't set `PROMPTGUARD_HISTORY_DB=""` |
| Slow evals | Reduce attacks/defenses; use `max_concurrency`; avoid `llm_judge` for large runs |

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for evaluation-specific issues.

---

## Pre-demo checklist

- [ ] App or API running and reachable
- [ ] API keys configured (env or Streamlit secrets)
- [ ] Test eval completes successfully
- [ ] Backup screenshots/video ready
- [ ] Know which provider/model/attacks to demo
