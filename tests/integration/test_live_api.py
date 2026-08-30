import os

import pytest

from src.model_client import ModelClient


pytestmark = pytest.mark.integration


def test_live_huggingface_chat_is_opt_in() -> None:
    token = os.getenv("HF_TOKEN", "")
    if not token:
        pytest.skip("HF_TOKEN is not configured; live integration is opt-in")
    client = ModelClient(token=token, backend="huggingface")
    response = client.chat("Reply with exactly: OK", max_tokens=8, temperature=0.0)
    assert response.strip()
