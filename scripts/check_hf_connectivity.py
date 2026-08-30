"""Phase 1 connectivity gate.

Usage:
    python scripts/check_hf_connectivity.py

Requires HF_TOKEN. Optional TARGET_MODEL/EVALUATOR_MODEL in environment.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Make the documented `python scripts/check_hf_connectivity.py` command work
# without requiring callers to set PYTHONPATH manually.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import settings
from src.model_client import ModelClient


def probe(label: str, model: str, prompt: str) -> bool:
    client = ModelClient()
    print(f"\n[{label}] {model}")
    try:
        output = client.chat(prompt, model=model, temperature=0.0, max_tokens=120)
        print("PASS")
        print(output[:500])
        return True
    except Exception as exc:
        print(f"FAIL: {type(exc).__name__}: {exc}")
        return False


def main() -> int:
    settings.validate()
    target_ok = probe(
        "TARGET",
        settings.target_model,
        "Reply with exactly: TARGET_OK",
    )
    evaluator_ok = probe(
        "EVALUATOR",
        settings.evaluator_model,
        'Return JSON only: {"status":"EVALUATOR_OK"}',
    )
    if target_ok and evaluator_ok:
        print("\nPHASE 1 CONNECTIVITY GATE: PASS")
        return 0
    print("\nPHASE 1 CONNECTIVITY GATE: FAIL")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
