from __future__ import annotations

import json
from pathlib import Path
from .comparison import ModelComparison

EXPORT_DIR = Path(__file__).resolve().parents[1] / "outputs"


def export_comparison(comparison: ModelComparison, stem: str = "model_comparison") -> tuple[str, str]:
    EXPORT_DIR.mkdir(exist_ok=True)
    csv_path = EXPORT_DIR / f"{stem}_leaderboard.csv"
    json_path = EXPORT_DIR / f"{stem}.json"
    comparison.leaderboard.to_csv(csv_path, index=False, encoding="utf-8-sig")
    payload = {
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
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(csv_path), str(json_path)
