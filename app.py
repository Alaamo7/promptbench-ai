from __future__ import annotations

import json
import gradio as gr

from src.analytics import category_figure, category_metrics, criterion_figure, criterion_metrics, error_count, strongest_weakest
from src.benchmark import BenchmarkEngine
from src.comparison import ComparisonEngine
from src.comparison_exporter import export_comparison
from src.comparison_history import comparison_history_dataframe, save_comparison
from src.config import settings
from src.evaluator import EvaluationEngine
from src.exporter import export_benchmark
from src.history import history_dataframe, load_runs, save_run
from src.model_client import ModelClient
from src.presentation import result_markdown
from src.test_cases import load_test_cases

client = ModelClient()
evaluator = EvaluationEngine(client)
benchmark_engine = BenchmarkEngine(target_client=client, evaluator=evaluator)
comparison_engine = ComparisonEngine(
    benchmark_engine=benchmark_engine,
    evaluator_model=settings.evaluator_model,
    provider=settings.provider_label,
)

CATEGORY_HELP = {
    "Instruction Following": '{"exact_bullets": 4}',
    "Formatting": '{"must_be_json": true}',
    "Constraint Following": '{"max_words": 100}',
    "Translation": '{}',
    "Extraction": '{}',
    "Reasoning": '{}',
    "General": '{}',
}

DATASET = load_test_cases()
BENCHMARK_CATEGORIES = sorted({case.get("category", "general") for case in DATASET})
BENCHMARK_LANGUAGES = sorted({case.get("language", "unknown") for case in DATASET})


def default_rules(category: str) -> str:
    return CATEGORY_HELP.get(category, "{}")


def evaluate_prompt(prompt: str, model: str, category: str, rules_json: str):
    if not prompt or not prompt.strip():
        raise gr.Error("اكتب Prompt أولاً.")
    try:
        rules = json.loads(rules_json) if rules_json.strip() else {}
        if not isinstance(rules, dict):
            raise ValueError
    except (json.JSONDecodeError, ValueError):
        raise gr.Error("Rules لازم تكون JSON object صحيحة.")
    try:
        response = client.chat(prompt.strip(), model=(model or settings.target_model).strip())
        result = evaluator.evaluate(prompt.strip(), response, rules)
    except Exception as exc:
        raise gr.Error(f"Execution failed: {exc}")
    structured = {
        "category": category,
        "target_model": (model or settings.target_model).strip(),
        "evaluator_model": settings.evaluator_model,
        "overall_score": result.overall_score,
        "verdict": result.verdict,
        "quality_band": result.quality_band,
        "reason": result.reason,
        **result.scores.model_dump(),
        "deterministic_checks": result.deterministic_checks,
    }
    return response, result_markdown(result), structured


def benchmark_summary_markdown(summary: dict, model: str, rows: list[dict]) -> str:
    strongest, weakest = strongest_weakest(rows)
    errors = error_count(rows)
    category_lines = "\n".join(
        f"- **{category}:** {score:.1f}/100"
        for category, score in sorted(summary.get("category_scores", {}).items())
    ) or "- No category results"
    return (
        f"## Benchmark Result\n"
        f"**Target Model:** `{model}`  \n"
        f"**Evaluator:** `{settings.evaluator_model}`  \n\n"
        f"- Tests Run: **{summary['tests_run']}**\n"
        f"- Passed: **{summary['passed']}**\n"
        f"- Failed: **{summary['failed']}**\n"
        f"- Pass Rate: **{summary['pass_rate']:.1f}%**\n"
        f"- Average Score: **{summary['average_score']:.1f}/100**\n"
        f"- API/Test Errors: **{errors}**\n"
        f"- Strongest Category: **{strongest}**\n"
        f"- Weakest Category: **{weakest}**\n\n"
        f"### Category Scores\n{category_lines}"
    )


def run_benchmark_ui(model: str, categories: list[str], languages: list[str], limit: int):
    model = (model or settings.target_model).strip()
    if not model:
        raise gr.Error("حدد Target Model.")
    cases = benchmark_engine.select_cases(
        categories=categories or None,
        languages=languages or None,
        limit=int(limit) if limit else None,
    )
    if not cases:
        raise gr.Error("لا توجد Test Cases تطابق الفلاتر الحالية.")
    run = benchmark_engine.run(
        model=model,
        cases=cases,
        delay_seconds=settings.benchmark_delay_seconds,
    )
    csv_path, json_path = export_benchmark(run)
    record = save_run(model, settings.evaluator_model, run.summary, run.rows)
    display_columns = ["id", "category", "language", "status", "overall_score", "quality_band", "verdict", "reason"]
    table = run.dataframe[display_columns]
    return (
        benchmark_summary_markdown(run.summary, model, run.rows),
        table,
        csv_path,
        json_path,
        category_metrics(run.rows),
        criterion_metrics(run.rows),
        category_figure(run.rows),
        criterion_figure(run.rows),
        history_dataframe(),
        f"Saved run: `{record['run_id']}`",
    )



def comparison_summary_markdown(comparison) -> str:
    lb = comparison.leaderboard
    if lb.empty:
        return "## Model Comparison\nNo results."
    winner_row = lb.iloc[0]
    lines = [
        "## Multi-Model Comparison",
        f"**Evaluator:** `{comparison.evaluator_model}`  ",
        f"**Same test cases for every model:** **{len(comparison.case_ids)}**  ",
        f"**Winner:** `{comparison.winner}` — **{winner_row['average_score']:.1f}/100**",
        f"**Scope:** winner of this selected benchmark only; this is not a universal model ranking.",
        "",
        "### Fairness Guardrails",
        "- Same selected prompts and order for every target model.",
        "- Same evaluator model for the full comparison.",
        "- API/test errors remain failures and are not removed from averages.",
        "- Duplicate target model names are removed before execution.",
    ]
    return "\n".join(lines)


def run_comparison_ui(models_text: str, categories: list[str], languages: list[str], limit: int):
    models = [m.strip() for m in (models_text or "").replace(",", "\n").splitlines() if m.strip()]
    models = comparison_engine.normalize_models(models)
    if len(models) < 2:
        raise gr.Error("اكتب اسمَي Target Models مختلفين على الأقل، كل Model في سطر.")
    if len(models) > 4:
        raise gr.Error("Phase 5 يقارن بحد أقصى 4 Models في التشغيل الواحد لتقليل التكلفة والـRate Limits.")
    cases = benchmark_engine.select_cases(
        categories=categories or None,
        languages=languages or None,
        limit=int(limit) if limit else None,
    )
    if not cases:
        raise gr.Error("لا توجد Test Cases تطابق الفلاتر الحالية.")
    comparison = comparison_engine.run(
        models=models,
        cases=cases,
        delay_seconds=settings.benchmark_delay_seconds,
    )
    csv_path, json_path = export_comparison(comparison)
    record = save_comparison(comparison)
    return (
        comparison_summary_markdown(comparison),
        comparison.leaderboard,
        comparison.category_table,
        comparison.criterion_table,
        csv_path,
        json_path,
        comparison_history_dataframe(),
        f"Saved comparison: `{record['comparison_id']}`",
    )


def refresh_history():
    df = history_dataframe()
    runs = load_runs()
    if not runs:
        return df, "No saved runs yet."
    latest = runs[0]
    s = latest.get("summary", {})
    text = (
        f"### Latest Run `{latest.get('run_id')}`\n"
        f"Target: `{latest.get('target_model')}`  \n"
        f"Tests: **{s.get('tests_run',0)}** | Pass Rate: **{s.get('pass_rate',0)}%** | "
        f"Average: **{s.get('average_score',0)}/100**"
    )
    return df, text


with gr.Blocks(title=settings.app_title) as demo:
    gr.Markdown(
        f"# {settings.app_title}\n"
        "منصة لاختبار مدى فهم نماذج اللغة للتعليمات باستخدام **Hybrid Evaluation**، "
        "Benchmark متعدد الحالات، Analytics Dashboard، وRun History."
    )

    with gr.Tabs():
        with gr.Tab("Home / About"):
            gr.Markdown(
                "## Graduation Project Overview\n"
                "**PromptBench AI** is a compact LLM evaluation platform for testing whether a model "
                "actually follows a user's instructions—not merely whether its answer sounds fluent.\n\n"
                "### Core Flow\n"
                "`Prompt → Target Model → Response → Deterministic Checks + LLM Judge → Weighted Score → ✔ UNDERSTOOD / ❌ FAILED`\n\n"
                "### Evaluation Methodology\n"
                "- **Instruction Following — 35%**\n"
                "- **Relevance — 30%**\n"
                "- **Completeness — 20%**\n"
                "- **Clarity — 15%**\n\n"
                "### Validated Capabilities\n"
                "Single-prompt evaluation, a 50-case Arabic/English dataset, batch benchmarking, "
                "category and criterion analytics, persistent run history, UTF-8 exports, and fair "
                "multi-model comparison using identical ordered prompts and one fixed evaluator.\n\n"
                "### Reliability Boundaries\n"
                "API and quota failures remain zero-score failed rows. Comparison winners apply only "
                "to the selected benchmark and runtime conditions. LLM-as-a-Judge is useful but is not ground truth."
            )

        with gr.Tab("Single Test"):
            with gr.Row():
                with gr.Column(scale=2):
                    prompt = gr.Textbox(label="Prompt", lines=9, placeholder="اكتب التعليمات أو السؤال هنا...")
                    with gr.Row():
                        model = gr.Textbox(label="Target Model", value=settings.target_model)
                        category = gr.Dropdown(label="Test Category", choices=list(CATEGORY_HELP), value="General")
                    rules = gr.Code(label="Optional deterministic rules (JSON)", language="json", value="{}")
                    run_btn = gr.Button("Evaluate Prompt", variant="primary")
                with gr.Column(scale=2):
                    response = gr.Textbox(label="Model Response", lines=11)
                    verdict = gr.Markdown("## النتيجة ستظهر هنا")
                    evaluation = gr.JSON(label="Structured Evaluation")
            category.change(default_rules, inputs=category, outputs=rules)
            run_btn.click(evaluate_prompt, inputs=[prompt, model, category, rules], outputs=[response, verdict, evaluation])

        with gr.Tab("Benchmark + Analytics"):
            gr.Markdown(f"### Dataset\nالحزمة الحالية تحتوي على **{len(DATASET)} Test Cases**.")
            with gr.Row():
                bench_model = gr.Textbox(label="Target Model", value=settings.target_model)
                bench_limit = gr.Slider(label="Max Test Cases", minimum=1, maximum=len(DATASET), value=5, step=1)
            with gr.Row():
                bench_categories = gr.Dropdown(label="Categories (empty = all)", choices=BENCHMARK_CATEGORIES, multiselect=True)
                bench_languages = gr.Dropdown(label="Languages (empty = all)", choices=BENCHMARK_LANGUAGES, multiselect=True)
            bench_btn = gr.Button("Run Benchmark", variant="primary")
            bench_summary = gr.Markdown("## Benchmark results will appear here")
            run_saved = gr.Markdown("")
            bench_table = gr.Dataframe(label="Benchmark Results", interactive=False)
            with gr.Row():
                csv_file = gr.File(label="CSV Export")
                json_file = gr.File(label="JSON Export")
            with gr.Row():
                category_plot = gr.Plot(label="Category Scores")
                criterion_plot = gr.Plot(label="Evaluation Criteria")
            with gr.Row():
                category_table = gr.Dataframe(label="Category Analytics", interactive=False)
                criterion_table = gr.Dataframe(label="Criterion Analytics", interactive=False)
            history_table = gr.Dataframe(label="Recent Runs", value=history_dataframe(), interactive=False)

            bench_btn.click(
                run_benchmark_ui,
                inputs=[bench_model, bench_categories, bench_languages, bench_limit],
                outputs=[bench_summary, bench_table, csv_file, json_file, category_table, criterion_table, category_plot, criterion_plot, history_table, run_saved],
            )

        with gr.Tab("Model Comparison"):
            gr.Markdown(
                "### Fair Multi-Model Benchmark\n"
                "نفس الـTest Cases ونفس الـEvaluator يتم استخدامهم لكل Target Model. "
                "اكتب من 2 إلى 4 Models، كل Model في سطر."
            )
            comparison_models = gr.Textbox(
                label="Target Models (one per line)",
                lines=5,
                value=f"{settings.target_model}\n",
                placeholder="model-a\nmodel-b",
            )
            with gr.Row():
                comparison_limit = gr.Slider(label="Test Cases per Model", minimum=1, maximum=len(DATASET), value=5, step=1)
                comparison_categories = gr.Dropdown(label="Categories (empty = all)", choices=BENCHMARK_CATEGORIES, multiselect=True)
                comparison_languages = gr.Dropdown(label="Languages (empty = all)", choices=BENCHMARK_LANGUAGES, multiselect=True)
            comparison_btn = gr.Button("Compare Models", variant="primary")
            comparison_summary = gr.Markdown("## Comparison results will appear here")
            comparison_saved = gr.Markdown("")
            comparison_leaderboard = gr.Dataframe(label="Leaderboard", interactive=False)
            with gr.Row():
                comparison_categories_table = gr.Dataframe(label="Category-by-Model", interactive=False)
                comparison_criteria_table = gr.Dataframe(label="Criteria-by-Model", interactive=False)
            with gr.Row():
                comparison_csv = gr.File(label="Leaderboard CSV")
                comparison_json = gr.File(label="Comparison JSON")
            comparison_history = gr.Dataframe(label="Recent Comparisons", value=comparison_history_dataframe(), interactive=False)
            comparison_btn.click(
                run_comparison_ui,
                inputs=[comparison_models, comparison_categories, comparison_languages, comparison_limit],
                outputs=[comparison_summary, comparison_leaderboard, comparison_categories_table, comparison_criteria_table, comparison_csv, comparison_json, comparison_history, comparison_saved],
            )

        with gr.Tab("Run History"):
            gr.Markdown("كل Benchmark ناجح أو جزئي يتم حفظه محليًا كـJSONL لسهولة المراجعة والمقارنة لاحقًا.")
            refresh_btn = gr.Button("Refresh History")
            history_full = gr.Dataframe(label="Saved Runs", value=history_dataframe(), interactive=False)
            latest_summary = gr.Markdown("No saved runs yet.")
            refresh_btn.click(refresh_history, outputs=[history_full, latest_summary])


if __name__ == "__main__":
    settings.validate()
    demo.launch()
