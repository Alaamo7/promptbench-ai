from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    model_backend: str = os.getenv("MODEL_BACKEND", "huggingface").strip().lower()
    hf_token: str = os.getenv("HF_TOKEN", "")
    hf_provider: str = os.getenv("HF_PROVIDER", "auto")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
    # Conservative defaults. scripts/select_live_models.py can discover currently live router models.
    target_model: str = os.getenv("TARGET_MODEL", "Qwen/Qwen3-4B-Instruct-2507")
    evaluator_model: str = os.getenv("EVALUATOR_MODEL", "google/gemma-3-12b-it")
    app_title: str = os.getenv("APP_TITLE", "PromptBench AI")
    pass_threshold: int = int(os.getenv("PASS_THRESHOLD", "70"))
    request_timeout: int = int(os.getenv("REQUEST_TIMEOUT", "90"))
    benchmark_delay_seconds: float = float(os.getenv("BENCHMARK_DELAY_SECONDS", "3"))

    def validate(self) -> None:
        if self.model_backend not in {"huggingface", "ollama"}:
            raise RuntimeError("MODEL_BACKEND must be 'huggingface' or 'ollama'.")
        if self.model_backend == "huggingface" and not self.hf_token:
            raise RuntimeError(
                "HF_TOKEN is missing. Add it as a Hugging Face Space secret or local environment variable."
            )
        if not 0 <= self.pass_threshold <= 100:
            raise RuntimeError("PASS_THRESHOLD must be between 0 and 100.")
        if self.benchmark_delay_seconds < 0:
            raise RuntimeError("BENCHMARK_DELAY_SECONDS must be zero or greater.")

    @property
    def provider_label(self) -> str:
        if self.model_backend == "ollama":
            return f"ollama:{self.ollama_base_url}"
        return f"huggingface:{self.hf_provider}"


settings = Settings()
