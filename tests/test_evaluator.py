import json

import pytest

from src.evaluator import EvaluationEngine, _extract_json


class FakeClient:
    def __init__(self, judge_payload):
        self.judge_payload = judge_payload
        self.calls = []

    def chat(self, prompt, model=None, temperature=0.2, max_tokens=512):
        self.calls.append({"prompt": prompt, "model": model})
        return json.dumps(self.judge_payload)


def test_evaluator_returns_binary_verdict_and_quality_band():
    client = FakeClient({
        "instruction_following": 90,
        "relevance": 90,
        "completeness": 85,
        "clarity": 90,
        "reason": "Good compliance",
    })
    result = EvaluationEngine(client).evaluate("Give two bullets", "- A\n- B", {"exact_bullets": 2})
    assert result.verdict == "UNDERSTOOD"
    assert result.quality_band in {"EXCELLENT", "GOOD"}
    assert result.deterministic_checks["bullet_count_pass"] is True


def test_failed_check_reduces_score():
    payload = {
        "instruction_following": 90,
        "relevance": 90,
        "completeness": 90,
        "clarity": 90,
        "reason": "Looks good semantically",
    }
    result = EvaluationEngine(FakeClient(payload)).evaluate(
        "Answer in exactly two bullets", "- One", {"exact_bullets": 2}
    )
    assert result.overall_score == 80
    assert result.deterministic_checks["bullet_count_pass"] is False


def test_invalid_score_is_rejected():
    payload = {
        "instruction_following": 101,
        "relevance": 90,
        "completeness": 90,
        "clarity": 90,
        "reason": "invalid",
    }
    with pytest.raises(ValueError):
        EvaluationEngine(FakeClient(payload)).evaluate("x", "y", {})


def test_malformed_evaluator_output_is_rejected():
    with pytest.raises(ValueError, match="valid JSON"):
        _extract_json("not valid JSON")
