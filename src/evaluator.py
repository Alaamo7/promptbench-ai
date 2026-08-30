from __future__ import annotations

import json
import re

from .config import settings
from .model_client import ModelClient
from .schemas import CriterionScores, EvaluationResult
from .scoring import deterministic_penalty, quality_band_for, verdict_for, weighted_score
from .validators import run_rule_checks


SYSTEM_PROMPT = """You are a strict evaluator of whether an LLM understood and followed a user prompt.
Score each criterion from 0 to 100: instruction_following, relevance, completeness, clarity.
Return JSON only with exactly these keys:
{
  "instruction_following": 0,
  "relevance": 0,
  "completeness": 0,
  "clarity": 0,
  "reason": "brief evidence-based explanation"
}
Do not reward verbosity. Penalize unmet explicit constraints. Base your judgment only on the user prompt, model response, and deterministic checks.
"""


def _extract_json(text: str) -> dict:
    text = text.strip()
    try:
        data = json.loads(text)
    except Exception:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            raise ValueError("Evaluator did not return valid JSON.")
        data = json.loads(match.group(0))
    if not isinstance(data, dict):
        raise ValueError("Evaluator JSON must be an object.")
    return data


def _score(value: object, field: str) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Evaluator field '{field}' must be an integer.") from exc
    if not 0 <= number <= 100:
        raise ValueError(f"Evaluator field '{field}' must be between 0 and 100.")
    return number


class EvaluationEngine:
    def __init__(self, client: ModelClient | None = None):
        self.client = client or ModelClient()

    def evaluate(self, prompt: str, response: str, rules: dict | None = None) -> EvaluationResult:
        checks = run_rule_checks(response, rules)
        judge_prompt = f"""{SYSTEM_PROMPT}

USER PROMPT:
{prompt}

MODEL RESPONSE:
{response}

DETERMINISTIC CHECKS:
{json.dumps(checks, ensure_ascii=False)}
"""
        raw = self.client.chat(
            judge_prompt,
            model=settings.evaluator_model,
            temperature=0.0,
            max_tokens=400,
        )
        data = _extract_json(raw)
        scores = CriterionScores(
            instruction_following=_score(data.get("instruction_following"), "instruction_following"),
            relevance=_score(data.get("relevance"), "relevance"),
            completeness=_score(data.get("completeness"), "completeness"),
            clarity=_score(data.get("clarity"), "clarity"),
        )
        base = weighted_score(scores)
        final = max(0, base - deterministic_penalty(checks))
        return EvaluationResult(
            scores=scores,
            overall_score=final,
            verdict=verdict_for(final, settings.pass_threshold),
            quality_band=quality_band_for(final),
            reason=str(data.get("reason", "")).strip(),
            deterministic_checks=checks,
        )
