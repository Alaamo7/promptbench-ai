# Source audit

Audit date: 2026-08-30. Source baseline: Hugging Face Space commit `fd64045`. GitHub mirror commit validated by CI: `2b2ba5a`.

## Verified

- Programming language: Python.
- Hugging Face Space SDK/UI framework: Gradio, with `sdk_version: 6.25.0` in the Space README metadata.
- Application entry point: `app.py`.
- Model backends: Hugging Face Inference Providers through `huggingface_hub.InferenceClient`, plus optional Ollama through `POST /api/chat`.
- Default configured model identifiers: `Qwen/Qwen3-4B-Instruct-2507` for the target and `google/gemma-3-12b-it` for the evaluator. These are configuration defaults, not claims of current provider availability.
- Main libraries declared in `requirements.txt`: Gradio, huggingface_hub, Pydantic, python-dotenv, pandas, pytest, requests, Matplotlib, and truststore.
- Configuration variables: `HF_TOKEN`, `MODEL_BACKEND`, `HF_PROVIDER`, `OLLAMA_BASE_URL`, `TARGET_MODEL`, `EVALUATOR_MODEL`, `APP_TITLE`, `PASS_THRESHOLD`, `REQUEST_TIMEOUT`, and `BENCHMARK_DELAY_SECONDS`.
- Evaluation logic: deterministic checks plus an LLM judge, four weighted criteria, deterministic penalties, configurable threshold, verdict, and quality band.
- Test assets: an inspected 50-case Arabic/English JSON dataset and offline pytest coverage for evaluation, validation, scoring, benchmarking, comparison, history, reporting, analytics, configuration, failures, and security.
- Storage: runtime-local JSONL under `data/history/` and generated CSV/JSON under `outputs/`; no database implementation was found.
- Logging: no configured Python logging subsystem was found. Failures are surfaced to the Gradio UI or stored as benchmark error rows.
- Prompts: a fixed evaluator system prompt in `src/evaluator.py`, user prompts from the UI/dataset, and deterministic rule objects.
- Agent logic: no autonomous agent loop, tool-calling agent runtime, planner, or multi-agent orchestration exists in the application code.
- GitHub CI run #1 passed the offline job and Gitleaks secret-scan job. The live integration job was skipped by design.

## Inferred

- Runtime-local JSONL history may survive normal requests within one running Space container, but should not be treated as durable storage across rebuilds or container replacement.
- Hugging Face builds the application in its managed container environment using `requirements.txt`; the exact resolved dependency graph can change because requirements use minimum versions.
- The interface screenshots in `docs/assets/` represent a prior running deployment state and are genuine project evidence, but not proof of current API availability.

These points are documented as operational implications, not presented as verified runtime guarantees.

## Unknown

- Exact Python version used by the current Hugging Face Space; it is not pinned in the inspected source metadata.
- Current authorization/availability of the configured target and evaluator model identifiers.
- Whether the credential associated with the historical public secret alert has been revoked or rotated.
- Exact persistence lifecycle and retention guarantees for local Space filesystem data.
- Current live target/evaluator API result after this GitHub mirror; no credentialed integration call was made.

Unknown items remain limitations or open issues and are not converted into README feature claims.
