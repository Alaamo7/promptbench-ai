# Troubleshooting

## `HF_TOKEN is missing`

Set `HF_TOKEN` as a Hugging Face Space Secret or local environment variable. Do not put it in source, README, screenshots, logs, or committed `.env` files.

## Provider authentication, quota, 402 or rate-limit errors

Confirm the token is valid, scoped appropriately, and authorized for the selected provider/model. Check the Space logs without copying credentials. Reduce benchmark size or increase `BENCHMARK_DELAY_SECONDS` when rate limits are the cause.

## Model is unavailable

Model/provider availability changes. Set `TARGET_MODEL`, `EVALUATOR_MODEL`, and optionally `HF_PROVIDER` to currently authorized compatible values; then run one bounded integration check before a full benchmark.

## Ollama connection failure

Confirm Ollama is running, `MODEL_BACKEND=ollama`, and `OLLAMA_BASE_URL` is reachable from the process. A Hugging Face-hosted Space normally cannot reach an Ollama service bound only to `127.0.0.1` on another machine.

## Tests fail while importing Gradio behind a SOCKS proxy

The local audit environment initially lacked the optional `socksio` transport required by an inherited SOCKS proxy. Running the offline suite without those proxy variables produced the verified result. In an environment that intentionally uses SOCKS, install the reviewed `httpx[socks]` extra.

## History disappeared after rebuild

History is filesystem-local JSONL, not durable database storage. Treat it as session/runtime evidence unless persistent storage is deliberately designed and configured.
