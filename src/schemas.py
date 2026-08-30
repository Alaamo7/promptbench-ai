from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field


Verdict = Literal["UNDERSTOOD", "FAILED"]
QualityBand = Literal["EXCELLENT", "GOOD", "PARTIAL", "POOR"]


class CriterionScores(BaseModel):
    instruction_following: int = Field(ge=0, le=100)
    relevance: int = Field(ge=0, le=100)
    completeness: int = Field(ge=0, le=100)
    clarity: int = Field(ge=0, le=100)


class EvaluationResult(BaseModel):
    scores: CriterionScores
    overall_score: int = Field(ge=0, le=100)
    verdict: Verdict
    quality_band: QualityBand
    reason: str
    deterministic_checks: dict[str, bool | int | str] = Field(default_factory=dict)
