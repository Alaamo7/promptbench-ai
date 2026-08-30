from __future__ import annotations

from src.model_client import ModelClient


class FakeResponse:
    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return {"message": {"content": "LOCAL_OK"}}


def test_ollama_backend_uses_local_chat_api(monkeypatch) -> None:
    captured = {}

    def fake_post(url, json, timeout):
        captured.update({"url": url, "json": json, "timeout": timeout})
        return FakeResponse()

    monkeypatch.setattr("src.model_client.requests.post", fake_post)
    client = ModelClient(backend="ollama")
    output = client.chat("hello", model="qwen3:4b", temperature=0.0, max_tokens=20)

    assert output == "LOCAL_OK"
    assert captured["url"].endswith("/api/chat")
    assert captured["json"]["model"] == "qwen3:4b"
    assert captured["json"]["options"]["num_predict"] == 20
