"""Verify both Phase 5 target models and the fixed evaluator are live."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import time

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import settings
from src.model_client import ModelClient


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("target_a")
    parser.add_argument("target_b")
    parser.add_argument("--delay-seconds", type=float, default=5.0)
    args = parser.parse_args()

    probes = [
        ("TARGET_A", args.target_a, "Reply with exactly: TARGET_A_OK"),
        ("TARGET_B", args.target_b, "Reply with exactly: TARGET_B_OK"),
        ("EVALUATOR", settings.evaluator_model, 'Return JSON only: {"status":"EVALUATOR_OK"}'),
    ]
    client = ModelClient()
    passed = True
    for index, (label, model, prompt) in enumerate(probes):
        print(f"[{label}] {model}")
        try:
            output = client.chat(prompt, model=model, temperature=0.0, max_tokens=40)
            print(f"PASS: {output[:120]}")
        except Exception as exc:
            passed = False
            print(f"FAIL: {type(exc).__name__}: {str(exc)[:300]}")
        if index < len(probes) - 1 and args.delay_seconds > 0:
            time.sleep(args.delay_seconds)

    print("PHASE 5 CONNECTIVITY: PASS" if passed else "PHASE 5 CONNECTIVITY: FAIL")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
