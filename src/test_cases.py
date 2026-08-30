from __future__ import annotations

import json
from pathlib import Path

DATASET_PATH = Path(__file__).resolve().parents[1] / "data" / "test_prompts.json"


def load_test_cases() -> list[dict]:
    with DATASET_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)
