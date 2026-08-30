from __future__ import annotations

import gradio as gr
import pytest

import app


def test_empty_prompt_is_rejected_without_api_call(monkeypatch) -> None:
    monkeypatch.setattr(
        app.client,
        "chat",
        lambda *args, **kwargs: pytest.fail("API must not be called"),
    )
    with pytest.raises(gr.Error, match="اكتب Prompt"):
        app.evaluate_prompt("   ", "model", "General", "{}")


def test_invalid_rules_json_is_rejected_without_api_call(monkeypatch) -> None:
    monkeypatch.setattr(
        app.client,
        "chat",
        lambda *args, **kwargs: pytest.fail("API must not be called"),
    )
    with pytest.raises(gr.Error, match="JSON object"):
        app.evaluate_prompt("Explain DNS.", "model", "General", "{bad")


def test_target_api_error_is_wrapped_for_gradio(monkeypatch) -> None:
    def fail_target(*args, **kwargs):
        raise TimeoutError("simulated target timeout")

    monkeypatch.setattr(app.client, "chat", fail_target)
    with pytest.raises(gr.Error, match="Execution failed: simulated target timeout"):
        app.evaluate_prompt("Explain DNS.", "model", "General", "{}")


def test_evaluator_parse_error_is_wrapped_for_gradio(monkeypatch) -> None:
    monkeypatch.setattr(app.client, "chat", lambda *args, **kwargs: "Target response")

    def fail_evaluator(*args, **kwargs):
        raise ValueError("Evaluator did not return valid JSON.")

    monkeypatch.setattr(app.evaluator, "evaluate", fail_evaluator)
    with pytest.raises(gr.Error, match="Evaluator did not return valid JSON"):
        app.evaluate_prompt("Explain DNS.", "model", "General", "{}")
