# Architecture

## Verified runtime components

| Component | Implementation | Responsibility |
|---|---|---|
| UI and entry point | `app.py`, Gradio 6.25.0 Space metadata | Collect inputs, invoke workflows, render tables/charts/files |
| Configuration | `src/config.py` | Load environment variables and validate backend/threshold/delay |
| Model access | `src/model_client.py` | Call Hugging Face `InferenceClient` or Ollama `/api/chat` |
| Deterministic validation | `src/validators.py` | Check counts, JSON, required and forbidden terms |
| LLM evaluation | `src/evaluator.py` | Build judge prompt, parse/validate JSON scores |
| Scoring | `src/scoring.py` | Apply criterion weights, deterministic penalties, bands and verdict |
| Batch benchmark | `src/benchmark.py` | Filter cases, execute sequentially, preserve failures |
| Model comparison | `src/comparison.py` | Reuse identical ordered cases and rank benchmark-scoped results |
| Analytics | `src/analytics.py` | Aggregate category/criterion metrics and build Matplotlib figures |
| Storage/export | `src/history.py`, `src/comparison_history.py`, exporters | Write local JSONL history and CSV/JSON outputs |
| Dataset | `data/test_prompts.json` | 50 unique Arabic/English cases across multiple categories |

## Single-test data flow

1. `evaluate_prompt()` validates non-empty input and parses optional rules as a JSON object.
2. `ModelClient.chat()` sends the prompt to the selected target model.
3. `EvaluationEngine.evaluate()` runs deterministic checks.
4. The evaluator sends the original prompt, target response, and check results to the configured evaluator model.
5. Pydantic-constrained scores are weighted: instruction following 35%, relevance 30%, completeness 20%, clarity 15%.
6. Failed deterministic checks subtract 10 points each, capped at 35.
7. The UI renders the response, score, quality band, verdict, reason, and structured result.

## Benchmark and comparison flow

`BenchmarkEngine` selects cases by category/language/limit. A case-level exception becomes an `ERROR`, zero-score, `FAILED` row, so failures remain in totals and averages. `ComparisonEngine` normalizes 2–4 model names and passes the same case objects and order to each run. Rankings are therefore scoped to that selected benchmark and evaluator, not universal model rankings.

## Dependency relationships

```text
app.py
  +-- config --> environment
  +-- model_client --> huggingface_hub | requests/Ollama
  +-- evaluator --> validators + scoring + schemas
  +-- benchmark --> model_client + evaluator + dataset
  +-- comparison --> benchmark
  +-- analytics --> pandas + matplotlib
  +-- history/export --> filesystem + pandas/json
```

## Storage

There is no database. Runs and comparisons are appended to `data/history/*.jsonl`; exports are written to `outputs/`. These paths are runtime-local and ignored in the GitHub mirror.

## Not present

No autonomous agent loop, authentication layer, server database, queue, fine-tuning pipeline, or model-training code was found.
