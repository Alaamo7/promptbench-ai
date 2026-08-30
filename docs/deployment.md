# Deployment

## Verified Hugging Face Space configuration

- Space: `3la2mo7/promptbench-ai`
- SDK: Gradio
- SDK version: 6.25.0
- Entry point: `app.py`
- Dependency source: `requirements.txt`
- License metadata: MIT
- Observed state during the 2026-08-30 audit: `Sleeping`
- Python version: not pinned in repository metadata

## Initial deployment

1. Create or select a Gradio Hugging Face Space.
2. Copy the application source, `src/`, `data/test_prompts.json`, and `requirements.txt`.
3. In Space Settings, add `HF_TOKEN` as a secret. Add non-sensitive configuration as variables when appropriate.
4. Commit the source to the Space and wait for dependency installation/build completion.
5. Open the App tab and run a bounded smoke test.

## Update and rebuild

Push source changes to the Space repository. Hugging Face rebuilds when dependency or application files change. If a rebuild is needed without a code change, use the Space settings restart/rebuild control and record the resulting build status.

## Validation after an update

- Confirm the Home page loads.
- Confirm an empty prompt is rejected locally without an API call.
- Run one authorized single prompt and verify that target output plus structured evaluation render.
- Confirm exports/history only contain intended prompt/response data.
- Review build/runtime logs for dependency, authentication, timeout, and quota errors without copying secrets into tickets.

## Rollback considerations

Use the last known-good Hugging Face commit as the rollback target. Application source is versioned, but runtime-local JSONL history and generated outputs should not be treated as durable rollback data. Rotate credentials separately; reverting source must never restore an exposed secret.

## Local launch

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

For the Hugging Face backend, provide `HF_TOKEN`. For local Ollama, set `MODEL_BACKEND=ollama` and configure `OLLAMA_BASE_URL`.
