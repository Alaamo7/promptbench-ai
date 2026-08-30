from __future__ import annotations

from .schemas import CriterionScores


WEIGHTS = {
    "instruction_following": 0.35,
    "relevance": 0.30,
    "completeness": 0.20,
    "clarity": 0.15,
}


def weighted_score(scores: CriterionScores) -> int:
    raw = sum(getattr(scores, key) * weight for key, weight in WEIGHTS.items())
    return round(raw)


def verdict_for(score: int, pass_threshold: int = 70) -> str:
    return "UNDERSTOOD" if score >= pass_threshold else "FAILED"


def quality_band_for(score: int) -> str:
    if score >= 85:
        return "EXCELLENT"
    if score >= 70:
        return "GOOD"
    if score >= 50:
        return "PARTIAL"
    return "POOR"


def deterministic_penalty(checks: dict[str, bool | int | str]) -> int:
    boolean_checks = [
        v
        for k, v in checks.items()
        if k.endswith("_pass") or k.startswith("required:") or k.startswith("forbidden:")
    ]
    failed = sum(1 for v in boolean_checks if v is False)
    return min(failed * 10, 35)
