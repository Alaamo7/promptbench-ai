"""Generate the graduation report from the latest qualifying saved evidence."""
from __future__ import annotations

import os
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.comparison_history import load_comparisons
from src.history import load_runs
from src.reporting import save_graduation_report
from src.config import settings


def latest_qualifying_benchmark() -> dict:
    for run in load_runs(limit=None):
        summary = run.get("summary", {})
        categories = summary.get("category_scores", {})
        if summary.get("tests_run", 0) >= 10 and len(categories) >= 3:
            return run
    return {}


def main() -> int:
    published_benchmark = PROJECT_ROOT / "outputs" / "phase6_live_benchmark.json"
    if published_benchmark.exists():
        payload = json.loads(published_benchmark.read_text(encoding="utf-8"))
        run = {
            "run_id": os.getenv("PHASE6_BENCHMARK_RUN_ID", "3e622134accf"),
            "target_model": settings.target_model,
            "evaluator_model": settings.evaluator_model,
            "provider": settings.provider_label,
            "summary": payload.get("summary", {}),
            "rows": payload.get("results", []),
        }
    else:
        run = latest_qualifying_benchmark()

    published_comparison = PROJECT_ROOT / "outputs" / "phase6_live_comparison.json"
    if published_comparison.exists():
        comparison = json.loads(published_comparison.read_text(encoding="utf-8"))
        comparison["comparison_id"] = os.getenv("PHASE6_COMPARISON_ID", "b4b86ade5319")
    else:
        comparisons = load_comparisons(limit=1)
        comparison = comparisons[0] if comparisons else {}

    app_url = os.getenv("APP_URL", "https://3la2mo7-promptbench-ai.hf.space")
    output = save_graduation_report(run, comparison, app_url=app_url)
    print(f"GRADUATION REPORT: {output}")
    print(f"BENCHMARK RUN: {run.get('run_id', 'N/A')}")
    print(f"COMPARISON: {comparison.get('comparison_id', 'N/A')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
