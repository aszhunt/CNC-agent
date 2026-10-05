# AI CNC Programming Copilot

Safety-first Streamlit + CrewAI foundation for an AI-assisted CNC manufacturing workflow.

## Current stage

This repository is intentionally a **prototype foundation**. It performs drawing-analysis/planning orchestration but does NOT release executable G-code.

The safety architecture is:

Drawing -> Structured Engineering Analysis -> Manufacturing Plan -> Tooling -> Parameters -> G-code -> Deterministic Validation -> Simulation -> Human Approval

## Run locally

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

## API configuration

Recommended: Streamlit Secrets.

Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and fill in:

```toml
GPT_API_KEY = "..."
GPT_BASE_URL = "https://your-provider/v1"
GPT_MODEL = "gpt-120b"
```

The exact GPT-120B provider/model ID and vision API format must be confirmed before enabling image-to-model inference.

## GitHub / Streamlit Cloud

Do NOT commit `.streamlit/secrets.toml`. Streamlit provides native secrets management for deployment.

## Safety

This project is not a substitute for a qualified CNC programmer/machinist, machine documentation, controller documentation, CAM simulation, or shop safety procedures.

Never run generated CNC code without independent review and simulation.
