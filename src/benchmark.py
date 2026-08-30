from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Iterable

import pandas as pd

from .evaluator import EvaluationEngine
from .model_client import ModelClient
from .test_cases import load_test_cases


@dataclass
class BenchmarkRun:
    rows: list[dict]

    @property
    def dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(self.rows)

    @property
    def summary(self) -> dict:
        if not self.rows:
            return {
                "tests_run": 0,
                "passed": 0,
                "failed": 0,
                "pass_rate": 0.0,
                "average_score": 0.0,
                "category_scores": {},
            }
        df = self.dataframe
        passed = int((df["verdict"] == "UNDERSTOOD").sum())
        total = len(df)
        category_scores = (
            df.groupby("category")["overall_score"].mean().round(1).to_dict()
        )
        return {
            "tests_run": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": round((passed / total) * 100, 1),
            "average_score": round(float(df["overall_score"].mean()), 1),
            "category_scores": category_scores,
        }


class BenchmarkEngine:
    def __init__(
        self,
        target_client: ModelClient | None = None,
        evaluator: EvaluationEngine | None = None,
    ):
        self.target_client = target_client or ModelClient()
        self.evaluator = evaluator or EvaluationEngine()

    def select_cases(
        self,
        categories: Iterable[str] | None = None,
        languages: Iterable[str] | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        cases = load_test_cases()
        category_set = {c for c in (categories or []) if c}
        language_set = {l for l in (languages or []) if l}
        if category_set:
            cases = [c for c in cases if c.get("category") in category_set]
        if language_set:
            cases = [c for c in cases if c.get("language") in language_set]
        if limit is not None:
            cases = cases[: max(0, int(limit))]
        return cases

    def run(
        self,
        model: str,
        cases: list[dict] | None = None,
        delay_seconds: float = 0.0,
    ) -> BenchmarkRun:
        selected = cases if cases is not None else load_test_cases()
        rows: list[dict] = []
        for index, case in enumerate(selected):
            base = {
                "id": case.get("id"),
                "category": case.get("category"),
                "language": case.get("language"),
                "prompt": case.get("prompt"),
            }
            try:
                response = self.target_client.chat(case["prompt"], model=model)
                result = self.evaluator.evaluate(case["prompt"], response, case.get("rules") or {})
                rows.append({
                    **base,
                    "status": "OK",
                    "response": response,
                    "instruction_following": result.scores.instruction_following,
                    "relevance": result.scores.relevance,
                    "completeness": result.scores.completeness,
                    "clarity": result.scores.clarity,
                    "overall_score": result.overall_score,
                    "quality_band": result.quality_band,
                    "verdict": result.verdict,
                    "reason": result.reason,
                })
            except Exception as exc:
                rows.append({
                    **base,
                    "status": "ERROR",
                    "response": "",
                    "instruction_following": 0,
                    "relevance": 0,
                    "completeness": 0,
                    "clarity": 0,
                    "overall_score": 0,
                    "quality_band": "POOR",
                    "verdict": "FAILED",
                    "reason": f"Execution error: {exc}",
                })
            if delay_seconds > 0 and index < len(selected) - 1:
                time.sleep(delay_seconds)
        return BenchmarkRun(rows)
