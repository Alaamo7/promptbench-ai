"""Offline smoke test for the evaluation pipeline; no Hugging Face token required."""
from __future__ import annotations

import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.evaluator import EvaluationEngine


class FakeJudgeClient:
    def chat(self, prompt, model=None, temperature=0.0, max_tokens=400):
        return json.dumps({
            "instruction_following": 92,
            "relevance": 95,
            "completeness": 88,
            "clarity": 90,
            "reason": "The response is relevant and follows the requested structure.",
        })


def main():
    engine = EvaluationEngine(FakeJudgeClient())
    result = engine.evaluate(
        "Give exactly two bullet points about DNS.",
        "- DNS maps domain names to IP addresses.\n- It helps users reach services by readable names.",
        {"exact_bullets": 2},
    )
    print(result.model_dump_json(indent=2))
    assert result.verdict == "UNDERSTOOD"
    assert result.deterministic_checks["bullet_count_pass"] is True
    print("MVP OFFLINE SMOKE: PASS")


if __name__ == "__main__":
    main()
