from __future__ import annotations

from scripts.run_phase3_live_gate import merge_gate_rows, select_gate_cases
from src.test_cases import load_test_cases


def test_dataset_has_at_least_fifty_unique_valid_cases() -> None:
    cases = load_test_cases()
    ids = [case["id"] for case in cases]
    assert len(cases) >= 50
    assert len(ids) == len(set(ids))
    assert all(case.get("prompt", "").strip() for case in cases)
    assert all(isinstance(case.get("rules", {}), dict) for case in cases)


def test_full_live_gate_is_ten_bilingual_cases_across_three_categories() -> None:
    cases = select_gate_cases("full")
    assert len(cases) == 10
    assert len({case["category"] for case in cases}) >= 3
    assert {case["language"] for case in cases} == {"en", "ar"}


def test_resume_merge_keeps_successes_and_replaces_only_pending_rows() -> None:
    cases = [{"id": "a"}, {"id": "b"}, {"id": "c"}]
    previous_ok = {"a": {"id": "a", "status": "OK", "overall_score": 90}}
    pending_rows = [
        {"id": "b", "status": "OK", "overall_score": 80},
        {"id": "c", "status": "OK", "overall_score": 70},
    ]
    merged = merge_gate_rows(cases, previous_ok, pending_rows)
    assert [row["id"] for row in merged] == ["a", "b", "c"]
    assert [row["overall_score"] for row in merged] == [90, 80, 70]
