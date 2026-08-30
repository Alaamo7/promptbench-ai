"""Run the reproducible Phase 3 live benchmark gates.

Usage:
    python scripts/run_phase3_live_gate.py small
    python scripts/run_phase3_live_gate.py full

Requires HF_TOKEN. The small run covers three categories. The full run covers
ten bilingual cases across extraction, question answering, and summarization.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.benchmark import BenchmarkEngine, BenchmarkRun
from src.config import settings
from src.evaluator import EvaluationEngine
from src.exporter import export_benchmark
from src.history import save_run
from src.model_client import ModelClient
from src.test_cases import load_test_cases


CASE_IDS = {
    "small": ["IF-001", "FMT-001", "TR-001"],
    "full": [
        "EX-001",
        "EX-002",
        "QA-001",
        "QA-002",
        "SUM-001",
        "SUM-002",
        "EX-003",
        "EX-004",
        "QA-003",
        "QA-004",
    ],
}


def select_gate_cases(size: str) -> list[dict]:
    wanted = CASE_IDS[size]
    by_id = {case["id"]: case for case in load_test_cases()}
    missing = [case_id for case_id in wanted if case_id not in by_id]
    if missing:
        raise RuntimeError(f"Missing Phase 3 case IDs: {missing}")
    return [by_id[case_id] for case_id in wanted]


def merge_gate_rows(
    cases: list[dict],
    previous_ok: dict[str, dict],
    pending_rows: list[dict],
) -> list[dict]:
    pending_by_id = {row["id"]: row for row in pending_rows}
    return [
        previous_ok[case["id"]]
        if case["id"] in previous_ok
        else pending_by_id[case["id"]]
        for case in cases
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("size", choices=CASE_IDS)
    parser.add_argument(
        "--resume",
        type=Path,
        help="Previous benchmark JSON; successful rows are kept and only errors are retried.",
    )
    parser.add_argument(
        "--delay-seconds",
        type=float,
        default=float(os.getenv("BENCHMARK_DELAY_SECONDS", "0")),
        help="Pause between live cases to respect provider quota replenishment.",
    )
    args = parser.parse_args()
    size = args.size

    settings.validate()
    cases = select_gate_cases(size)
    target_backend = os.getenv("TARGET_BACKEND", settings.model_backend).strip().lower()
    evaluator_backend = os.getenv("EVALUATOR_BACKEND", settings.model_backend).strip().lower()
    target_client = ModelClient(backend=target_backend)
    evaluator_client = ModelClient(backend=evaluator_backend)
    engine = BenchmarkEngine(
        target_client=target_client,
        evaluator=EvaluationEngine(evaluator_client),
    )
    previous_ok: dict[str, dict] = {}
    if args.resume:
        payload = json.loads(args.resume.read_text(encoding="utf-8"))
        previous_ok = {
            row["id"]: row
            for row in payload.get("results", [])
            if row.get("status") == "OK" and row.get("id") in CASE_IDS[size]
        }

    pending_cases = [case for case in cases if case["id"] not in previous_ok]
    pending_rows: list[dict] = []
    for index, case in enumerate(pending_cases):
        pending_rows.extend(engine.run(settings.target_model, [case]).rows)
        if args.delay_seconds > 0 and index < len(pending_cases) - 1:
            time.sleep(args.delay_seconds)
    merged_rows = merge_gate_rows(cases, previous_ok, pending_rows)
    run = BenchmarkRun(merged_rows)
    csv_path, json_path = export_benchmark(run, stem=f"phase3_live_{size}_{len(cases)}")
    record = save_run(settings.target_model, settings.evaluator_model, run.summary, run.rows)
    evidence = {
        "gate_size": size,
        "target_model": settings.target_model,
        "evaluator_model": settings.evaluator_model,
        "provider": (
            f"target={target_backend}:{settings.hf_provider if target_backend == 'huggingface' else settings.ollama_base_url};"
            f"evaluator={evaluator_backend}:{settings.hf_provider if evaluator_backend == 'huggingface' else settings.ollama_base_url}"
        ),
        "case_ids": [case["id"] for case in cases],
        "resumed_from": str(args.resume) if args.resume else None,
        "retried_case_ids": [case["id"] for case in pending_cases],
        "delay_seconds": args.delay_seconds,
        "categories": sorted({case["category"] for case in cases}),
        "languages": sorted({case["language"] for case in cases}),
        "summary": run.summary,
        "error_count": sum(row["status"] == "ERROR" for row in run.rows),
        "csv_path": csv_path,
        "json_path": json_path,
        "run_id": record["run_id"],
    }
    print(json.dumps(evidence, ensure_ascii=False, indent=2))
    return 0 if evidence["error_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
