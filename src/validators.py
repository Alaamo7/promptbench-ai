from __future__ import annotations

import json
import re
from typing import Any


def word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text, flags=re.UNICODE))


def sentence_count(text: str) -> int:
    parts = re.split(r"(?<=[.!?؟])\s+", text.strip())
    return len([p for p in parts if p.strip()]) if text.strip() else 0


def bullet_count(text: str) -> int:
    return sum(1 for line in text.splitlines() if re.match(r"^\s*(?:[-*•]|\d+[.)])\s+", line))


def is_valid_json(text: str) -> bool:
    try:
        json.loads(text)
        return True
    except Exception:
        return False


def run_rule_checks(response: str, rules: dict[str, Any] | None) -> dict[str, bool | int | str]:
    rules = rules or {}
    checks: dict[str, bool | int | str] = {}

    if "exact_sentences" in rules:
        actual = sentence_count(response)
        expected = int(rules["exact_sentences"])
        checks["sentence_count"] = actual
        checks["sentence_count_pass"] = actual == expected

    if "exact_bullets" in rules:
        actual = bullet_count(response)
        expected = int(rules["exact_bullets"])
        checks["bullet_count"] = actual
        checks["bullet_count_pass"] = actual == expected

    if "max_words" in rules:
        actual = word_count(response)
        maximum = int(rules["max_words"])
        checks["word_count"] = actual
        checks["max_words_pass"] = actual <= maximum

    if rules.get("must_be_json"):
        checks["json_pass"] = is_valid_json(response)

    for term in rules.get("required_terms", []):
        checks[f"required:{term}"] = term.casefold() in response.casefold()

    for term in rules.get("forbidden_terms", []):
        checks[f"forbidden:{term}"] = term.casefold() not in response.casefold()

    return checks
