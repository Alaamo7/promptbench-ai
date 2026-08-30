from __future__ import annotations

import json
from pathlib import Path

from .benchmark import BenchmarkRun


EXPORT_DIR = Path(__file__).resolve().parents[1] / "outputs"


def export_benchmark(run: BenchmarkRun, stem: str = "benchmark_results") -> tuple[str, str]:
    EXPORT_DIR.mkdir(exist_ok=True)
    csv_path = EXPORT_DIR / f"{stem}.csv"
    json_path = EXPORT_DIR / f"{stem}.json"
    run.dataframe.to_csv(csv_path, index=False, encoding="utf-8-sig")
    payload = {"summary": run.summary, "results": run.rows}
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(csv_path), str(json_path)
