from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import uuid
import pandas as pd

from .comparison import ModelComparison

COMPARISON_DIR = Path("data/history")
COMPARISON_FILE = COMPARISON_DIR / "comparisons.jsonl"


def save_comparison(comparison: ModelComparison) -> dict:
    COMPARISON_DIR.mkdir(parents=True, exist_ok=True)
    record = {
        "comparison_id": uuid.uuid4().hex[:12],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "evaluator_model": comparison.evaluator_model,
        "provider": comparison.provider,
        "case_ids": comparison.case_ids,
        "case_ids_by_model": {
            model: [str(row.get("id", "")) for row in run.rows]
            for model, run in comparison.runs.items()
        },
        "winner": comparison.winner,
        "leaderboard": comparison.leaderboard.to_dict(orient="records"),
        "category_table": comparison.category_table.to_dict(orient="records"),
        "criterion_table": comparison.criterion_table.to_dict(orient="records"),
        "results_by_model": {
            model: run.rows for model, run in comparison.runs.items()
        },
    }
    with COMPARISON_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


def load_comparisons(limit: int | None = 50) -> list[dict]:
    if not COMPARISON_FILE.exists():
        return []
    records = []
    for line in COMPARISON_FILE.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    records.reverse()
    return records[:limit] if limit else records


def comparison_history_dataframe(limit: int = 50) -> pd.DataFrame:
    rows = []
    for r in load_comparisons(limit):
        lb = r.get("leaderboard", [])
        rows.append({
            "comparison_id": r.get("comparison_id"),
            "created_at": r.get("created_at"),
            "winner": r.get("winner"),
            "models": len(lb),
            "tests_per_model": lb[0].get("tests_run", 0) if lb else 0,
            "winner_score": lb[0].get("average_score", 0.0) if lb else 0.0,
            "evaluator_model": r.get("evaluator_model"),
            "provider": r.get("provider", "unknown"),
        })
    return pd.DataFrame(rows)
