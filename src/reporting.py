from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _pct(v: Any) -> str:
    try: return f"{float(v):.1f}%"
    except Exception: return "0.0%"


def _num(v: Any) -> str:
    try: return f"{float(v):.1f}"
    except Exception: return "0.0"


def build_graduation_report(
    run: dict | None = None,
    comparison: dict | None = None,
    app_url: str = "Public deployment pending",
) -> str:
    run = run or {}
    comparison = comparison or {}
    summary = run.get("summary", {}) or {}
    lines = [
        "# PromptBench AI — Graduation Project Report",
        "",
        "## 1. Project Overview",
        "PromptBench AI is a mini LLM evaluation platform that tests how well language models understand and follow user prompts.",
        f"Application URL: {app_url}",
        "",
        "## 2. Problem",
        "A model response can look fluent while still missing instructions, constraints, required format, or parts of the requested task.",
        "",
        "## 3. Solution",
        "The system combines deterministic rule checks with an independent LLM evaluator, then produces a weighted score and a binary UNDERSTOOD / FAILED verdict.",
        "",
        "## 4. Evaluation Criteria",
        "- Instruction Following: 35%",
        "- Relevance: 30%",
        "- Completeness: 20%",
        "- Clarity: 15%",
        "",
        "## 5. System Flow",
        "User Prompt → Target Model → Response → Rule Checks + LLM Judge → Weighted Score → Verdict → Analytics / History / Comparison",
        "",
        "## 6. Latest Benchmark",
        f"- Run ID: `{run.get('run_id', 'N/A')}`",
        f"- Target model: `{run.get('target_model', 'N/A')}`",
        f"- Evaluator model: `{run.get('evaluator_model', 'N/A')}`",
        f"- Provider: `{run.get('provider', comparison.get('provider', 'N/A'))}`",
        f"- Tests run: **{summary.get('tests_run', 0)}**",
        f"- Pass rate: **{_pct(summary.get('pass_rate', 0))}**",
        f"- Average score: **{_num(summary.get('average_score', 0))}/100**",
        f"- Passed: **{summary.get('passed', 0)}**",
        f"- Failed: **{summary.get('failed', 0)}**",
        f"- API/test errors: **{sum(1 for row in run.get('rows', []) if row.get('status') == 'ERROR')}**",
        "",
        "## 7. Multi-Model Comparison",
        f"- Comparison ID: `{comparison.get('comparison_id', 'N/A')}`",
        f"- Winner in the latest saved comparison: `{comparison.get('winner', 'N/A')}`",
        f"- Evaluator used: `{comparison.get('evaluator_model', 'N/A')}`",
        f"- Provider: `{comparison.get('provider', 'N/A')}`",
        f"- Cases per model: **{len(comparison.get('case_ids', []))}**",
        "",
        "### Latest Comparison Leaderboard",
        "| Rank | Model | Tests | Pass rate | Average | Errors |",
        "|---:|---|---:|---:|---:|---:|",
        *[
            f"| {row.get('rank', '')} | `{row.get('model', '')}` | {row.get('tests_run', 0)} | "
            f"{_pct(row.get('pass_rate', 0))} | {_num(row.get('average_score', 0))} | {row.get('errors', 0)} |"
            for row in comparison.get("leaderboard", [])
        ],
        "",
        "## 8. Reliability & Fairness",
        "- Same prompts and order are used when comparing target models.",
        "- The same evaluator is used for a full comparison.",
        "- API/test errors remain failures instead of being silently excluded.",
        "- Secrets such as HF_TOKEN are not stored in reports or run history.",
        "",
        "## 9. Limitations",
        "LLM-as-a-Judge is useful but not ground truth. Results are benchmark-specific and depend on the selected prompts, evaluator, provider, model versions, and runtime conditions.",
        "",
        "## 10. Conclusion",
        "The project satisfies the graduation requirement of sending prompts to a language model, analyzing the response, and deciding whether the model understood the input, while extending it with measurable scoring, benchmarking, analytics, and fair model comparison.",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
    ]
    return "\n".join(lines)


def save_graduation_report(
    run: dict | None = None,
    comparison: dict | None = None,
    output_dir: str = "outputs",
    app_url: str = "Public deployment pending",
) -> str:
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    out = path / "PromptBench_AI_Graduation_Report.md"
    out.write_text(build_graduation_report(run, comparison, app_url=app_url), encoding="utf-8")
    return str(out)
