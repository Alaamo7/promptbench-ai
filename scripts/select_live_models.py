"""Inspect the Hugging Face OpenAI-compatible router for currently live chat models.

This avoids hard-coding stale model availability. It prints likely candidates and provider/pricing metadata.
Requires: HF_TOKEN and requests.
"""
from __future__ import annotations

import os
import sys
import requests
import truststore


# Use the operating-system trust store so authenticated requests remain TLS
# verified on managed Windows networks with locally trusted certificates.
truststore.inject_into_ssl()

ROUTER_MODELS_URL = "https://router.huggingface.co/v1/models"
PREFERRED_HINTS = ("qwen", "gemma", "mistral", "gpt-oss", "deepseek")


def main() -> int:
    token = os.getenv("HF_TOKEN", "")
    if not token:
        print("HF_TOKEN is missing.", file=sys.stderr)
        return 2

    response = requests.get(
        ROUTER_MODELS_URL,
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    response.raise_for_status()
    items = response.json().get("data", [])

    ranked = []
    for item in items:
        model_id = item.get("id", "")
        providers = [p for p in item.get("providers", []) if p.get("status") == "live"]
        if not providers:
            continue
        hint_rank = next((i for i, h in enumerate(PREFERRED_HINTS) if h in model_id.lower()), 99)
        ranked.append((hint_rank, model_id, providers))

    ranked.sort(key=lambda x: (x[0], x[1].lower()))
    print(f"Live chat models returned by router: {len(ranked)}\n")
    for _, model_id, providers in ranked[:40]:
        provider_bits = []
        for p in providers[:3]:
            pricing = p.get("pricing") or {}
            provider_bits.append(
                f"{p.get('provider')} | ctx={p.get('context_length')} | in={pricing.get('input')} out={pricing.get('output')}"
            )
        print(model_id)
        print("  " + " ; ".join(provider_bits))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
