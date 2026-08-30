# Security

## Secret handling

`HF_TOKEN` is read from the environment. For Hugging Face Spaces, store it under **Settings → Variables and secrets → Secrets**. For local use, keep it in `.env`, which is ignored. `.env.example` contains names and safe defaults only.

The source history showed that a public secret-scanning alert had previously been associated with `tests/test_evaluator.py`. The current file no longer contains a credential, but removal does not revoke a credential that was public. Status: **Credential rotation required**. Revoke or rotate the affected credential at its provider and update the Space secret before treating the incident as closed.

## Current controls

- `.env`, `.env.*`, credentials/secrets JSON/TOML, PEM/key files, generated outputs, and JSONL history are ignored.
- Offline security tests inspect repository text for common live-token prefixes and hardcoded secret assignments.
- CI runs Gitleaks against repository history.
- Tests use fake clients and do not require a production credential.
- Error handling does not intentionally log `HF_TOKEN`.

## Attack surface

- Public prompt and rules input in the Gradio UI.
- Outbound calls to Hugging Face Inference Providers or a configured Ollama URL.
- LLM evaluator prompt containing user input and model output.
- CSV/JSON exports and local JSONL history containing prompts and responses.
- Python dependencies and Hugging Face build/runtime supply chain.

## Prompt injection

The target response is embedded inside the evaluator prompt. A malicious or accidental response can attempt to instruct the judge. The system prompt asks the judge to base its decision only on supplied evidence, but this is not a complete isolation boundary. Deterministic checks reduce dependence on the judge for explicit constraints, yet evaluator manipulation remains a documented risk.

Recommended future controls include structured provider output where supported, delimiter hardening, adversarial evaluator tests, judge/model separation, and human review for high-impact decisions.

## Input validation

Current validation rejects empty prompts and malformed/non-object rules JSON. Deterministic score fields are constrained to integers from 0 to 100. There is no explicit maximum prompt length at the UI or client boundary; provider limits and timeouts currently act as the practical boundary.

## Dependency risk

`requirements.txt` specifies minimum versions rather than a locked dependency graph. CI checks dependency consistency, but reproducibility and supply-chain control would improve with a reviewed lock file or pinned constraints plus scheduled dependency updates.

## Credential rotation policy

1. Revoke the exposed credential at the provider immediately.
2. Create a replacement with the minimum required scope.
3. Update Hugging Face Space Secrets and any authorized local environment.
4. Confirm the old credential no longer authenticates.
5. Rerun offline tests, the secret scan, and one bounded integration test.
6. Record only dates/status/evidence—never credential values—in the security issue.
