from dataclasses import replace
from pathlib import Path
import re

import pytest

from src.config import settings


ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".py", ".md", ".json", ".yml", ".yaml", ".toml", ".ini", ".txt"}
TOKEN_PATTERNS = {
    "OpenAI": re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    "Hugging Face": re.compile(r"hf_[A-Za-z0-9]{20,}"),
    "GitHub": re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    "AWS access key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "Lob-style": re.compile(r"(?:live|test)_[a-f0-9]{32,}", re.IGNORECASE),
}
HARDCODED_ASSIGNMENT = re.compile(
    r"(?im)^\s*(?:[A-Z0-9_]*(?:API_KEY|TOKEN|SECRET|PASSWORD))\s*=\s*['\"][^'\"]{8,}['\"]"
)


def repository_text_files():
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in {".git", ".venv", "__pycache__"} for part in path.parts):
            continue
        if path.suffix in TEXT_SUFFIXES or path.name in {".env.example", ".gitignore"}:
            yield path


def test_no_common_hardcoded_secret_patterns() -> None:
    findings = []
    for path in repository_text_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        for name, pattern in TOKEN_PATTERNS.items():
            if pattern.search(text):
                findings.append(f"{path.relative_to(ROOT)}: {name} pattern")
        if HARDCODED_ASSIGNMENT.search(text):
            findings.append(f"{path.relative_to(ROOT)}: hardcoded secret assignment")
    assert findings == []


def test_env_is_ignored_and_example_has_blank_token() -> None:
    ignore_rules = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert ".env" in ignore_rules
    example = (ROOT / ".env.example").read_text(encoding="utf-8")
    assert re.search(r"(?m)^HF_TOKEN=\s*$", example)


def test_missing_hf_token_fails_configuration_validation() -> None:
    candidate = replace(settings, model_backend="huggingface", hf_token="")
    with pytest.raises(RuntimeError, match="HF_TOKEN is missing"):
        candidate.validate()
