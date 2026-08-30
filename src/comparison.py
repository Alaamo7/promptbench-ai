from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Iterable

import pandas as pd

from .benchmark import BenchmarkEngine, BenchmarkRun


@dataclass
class ModelComparison:
    runs: dict[str, BenchmarkRun]
    evaluator_model: str
    case_ids: list[str]
    provider: str = "unknown"

    @property
    def leaderboard(self) -> pd.DataFrame:
        rows = []
        for model, run in self.runs.items():
            s = run.summary
            rows.append({
                "model": model,
                "tests_run": s["tests_run"],
                "passed": s["passed"],
                "failed": s["failed"],
                "pass_rate": s["pass_rate"],
                "average_score": s["average_score"],
                "errors": sum(1 for r in run.rows if r.get("status") == "ERROR"),
            })
        if not rows:
            return pd.DataFrame(columns=["rank","model","tests_run","passed","failed","pass_rate","average_score","errors"])
        df = pd.DataFrame(rows).sort_values(
            ["average_score", "pass_rate", "errors", "model"],
            ascending=[False, False, True, True],
        ).reset_index(drop=True)
        df.insert(0, "rank", range(1, len(df) + 1))
        return df

    @property
    def winner(self) -> str | None:
        lb = self.leaderboard
        return None if lb.empty else str(lb.iloc[0]["model"])

    @property
    def category_table(self) -> pd.DataFrame:
        records: list[dict] = []
        for model, run in self.runs.items():
            df = run.dataframe
            if df.empty:
                continue
            for category, group in df.groupby("category"):
                total = len(group)
                passed = int((group["verdict"] == "UNDERSTOOD").sum())
                records.append({
                    "model": model,
                    "category": category,
                    "tests": total,
                    "pass_rate": round(passed / total * 100, 1),
                    "average_score": round(float(group["overall_score"].mean()), 1),
                })
        return pd.DataFrame(records)

    @property
    def criterion_table(self) -> pd.DataFrame:
        criteria = ["instruction_following", "relevance", "completeness", "clarity"]
        records: list[dict] = []
        for model, run in self.runs.items():
            df = run.dataframe
            if df.empty:
                continue
            for criterion in criteria:
                records.append({
                    "model": model,
                    "criterion": criterion,
                    "average_score": round(float(df[criterion].mean()), 1),
                })
        return pd.DataFrame(records)


class ComparisonEngine:
    """Runs exactly the same selected cases against each target model.

    Fairness rules:
    - Same case objects and order for every model.
    - Same evaluator instance/model for the entire comparison.
    - Errors remain failures; they are never silently removed.
    - At least two distinct models are required.
    """

    def __init__(
        self,
        benchmark_engine: BenchmarkEngine,
        evaluator_model: str,
        provider: str = "unknown",
    ):
        self.benchmark_engine = benchmark_engine
        self.evaluator_model = evaluator_model
        self.provider = provider

    @staticmethod
    def normalize_models(models: Iterable[str]) -> list[str]:
        cleaned: list[str] = []
        seen = set()
        for raw in models:
            model = (raw or "").strip()
            if model and model not in seen:
                cleaned.append(model)
                seen.add(model)
        return cleaned

    def run(
        self,
        models: Iterable[str],
        cases: list[dict],
        delay_seconds: float = 0.0,
    ) -> ModelComparison:
        normalized = self.normalize_models(models)
        if len(normalized) < 2:
            raise ValueError("At least two distinct target models are required for comparison.")
        if not cases:
            raise ValueError("At least one benchmark case is required for comparison.")

        case_ids = [str(c.get("id", "")) for c in cases]
        runs: dict[str, BenchmarkRun] = {}
        for index, model in enumerate(normalized):
            if delay_seconds > 0 and index > 0:
                time.sleep(delay_seconds)
            runs[model] = self.benchmark_engine.run(
                model=model,
                cases=cases,
                delay_seconds=delay_seconds,
            )
        return ModelComparison(
            runs=runs,
            evaluator_model=self.evaluator_model,
            case_ids=case_ids,
            provider=self.provider,
        )
