"""Persist verified public Phase 6 exports into the repository history files."""
from __future__ import annotations

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = PROJECT_ROOT / "outputs"
HISTORY = PROJECT_ROOT / "data" / "history"


def append_unique(path: Path, id_key: str, record: dict) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                existing.append(json.loads(line))
    if any(item.get(id_key) == record.get(id_key) for item in existing):
        return False
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    return True


def main() -> int:
    benchmark = json.loads((OUTPUTS / "phase6_live_benchmark.json").read_text(encoding="utf-8"))
    comparison = json.loads((OUTPUTS / "phase6_live_comparison.json").read_text(encoding="utf-8"))

    run_record = {
        "run_id": "3e622134accf",
        "created_at": "2026-08-21T14:38:57.407274+00:00",
        "target_model": "Qwen/Qwen3-4B-Instruct-2507",
        "evaluator_model": "google/gemma-3-12b-it",
        "provider": "huggingface:auto",
        "summary": benchmark["summary"],
        "rows": benchmark["results"],
    }
    comparison_record = {
        "comparison_id": "b4b86ade5319",
        "created_at": "2026-08-21T14:41:50.252990+00:00",
        **comparison,
    }

    run_added = append_unique(HISTORY / "runs.jsonl", "run_id", run_record)
    comparison_added = append_unique(
        HISTORY / "comparisons.jsonl", "comparison_id", comparison_record
    )
    print(f"PHASE6_RUN_IMPORTED={run_added}")
    print(f"PHASE6_COMPARISON_IMPORTED={comparison_added}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
