import pytest

from src.evaluator import _extract_json
from src.model_client import ModelClient
from src.validators import run_rule_checks


def test_extremely_long_text_is_checked_without_external_api() -> None:
    response = "word " * 20_000
    checks = run_rule_checks(response, {"max_words": 100})
    assert checks["word_count"] == 20_000
    assert checks["max_words_pass"] is False


def test_evaluator_json_must_be_an_object() -> None:
    with pytest.raises(ValueError, match="object"):
        _extract_json('[1, 2, 3]')


def test_model_client_rejects_empty_prompt_without_request() -> None:
    client = ModelClient(backend="ollama")
    with pytest.raises(ValueError, match="empty"):
        client.chat("   ", model="unused")
