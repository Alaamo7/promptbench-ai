from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import uuid
import pandas as pd

HISTORY_DIR = Path("data/history")
HISTORY_FILE = HISTORY_DIR / "runs.jsonl"


def save_run(model: str, evaluator_model: str, summary: dict, rows: list[dict]) -> dict:
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    record = {
        "run_id": uuid.uuid4().hex[:12],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "target_model": model,
        "evaluator_model": evaluator_model,
        "summary": summary,
        "rows": rows,
    }
    with HISTORY_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


def load_runs(limit: int | None = 50) -> list[dict]:
    if not HISTORY_FILE.exists():
        return []
    records = []
    for line in HISTORY_FILE.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    records.reverse()
    return records[:limit] if limit else records


def history_dataframe(limit: int = 50) -> pd.DataFrame:
    rows = []
    for r in load_runs(limit):
        s = r.get("summary", {})
        rows.append({
            "run_id": r.get("run_id"),
            "created_at": r.get("created_at"),
            "target_model": r.get("target_model"),
            "tests_run": s.get("tests_run", 0),
            "pass_rate": s.get("pass_rate", 0.0),
            "average_score": s.get("average_score", 0.0),
        })
    return pd.DataFrame(rows)


def get_run(run_id: str) -> dict | None:
    for r in load_runs(limit=None):
        if r.get("run_id") == run_id:
            return r
    return None
