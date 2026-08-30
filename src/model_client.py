from __future__ import annotations

import truststore
from huggingface_hub import InferenceClient
import requests

from .config import settings


# Preserve TLS verification while honoring certificates trusted by the host OS.
truststore.inject_into_ssl()


class ModelClient:
    def __init__(
        self,
        token: str | None = None,
        provider: str | None = None,
        backend: str | None = None,
    ):
        self.backend = (backend or settings.model_backend).strip().lower()
        if self.backend == "huggingface":
            self.client = InferenceClient(
                api_key=token or settings.hf_token,
                provider=provider or settings.hf_provider,
                timeout=settings.request_timeout,
            )
        elif self.backend == "ollama":
            self.client = None
        else:
            raise ValueError("Unsupported model backend. Use 'huggingface' or 'ollama'.")

    def chat(
        self,
        prompt: str,
        model: str | None = None,
        *,
        temperature: float = 0.2,
        max_tokens: int = 700,
    ) -> str:
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        selected_model = model or settings.target_model
        if self.backend == "ollama":
            response = requests.post(
                f"{settings.ollama_base_url}/api/chat",
                json={
                    "model": selected_model,
                    "messages": [{"role": "user", "content": prompt.strip()}],
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                    },
                },
                timeout=settings.request_timeout,
            )
            response.raise_for_status()
            content = (response.json().get("message") or {}).get("content")
        else:
            response = self.client.chat.completions.create(
                model=selected_model,
                messages=[{"role": "user", "content": prompt.strip()}],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = response.choices[0].message.content
        if not content:
            raise RuntimeError("The model returned an empty response.")
        return content.strip()
