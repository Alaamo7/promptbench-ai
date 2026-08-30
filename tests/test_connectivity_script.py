from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_connectivity_script_runs_directly_without_pythonpath() -> None:
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    env["HF_TOKEN"] = ""

    completed = subprocess.run(
        [sys.executable, "scripts/check_hf_connectivity.py"],
        cwd=PROJECT_ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    output = completed.stdout + completed.stderr
    assert completed.returncode != 0
    assert "HF_TOKEN is missing" in output
    assert "ModuleNotFoundError" not in output
