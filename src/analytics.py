from __future__ import annotations

from collections import Counter
import pandas as pd
import matplotlib.pyplot as plt


def category_metrics(rows: list[dict]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame(columns=["category","tests","passed","pass_rate","average_score"])
    df = pd.DataFrame(rows)
    grouped = []
    for category, g in df.groupby("category"):
        total = len(g)
        passed = int((g["verdict"] == "UNDERSTOOD").sum())
        grouped.append({
            "category": category,
            "tests": total,
            "passed": passed,
            "pass_rate": round(passed / total * 100, 1),
            "average_score": round(float(g["overall_score"].mean()), 1),
        })
    return pd.DataFrame(grouped).sort_values("average_score", ascending=False).reset_index(drop=True)


def criterion_metrics(rows: list[dict]) -> pd.DataFrame:
    criteria = ["instruction_following", "relevance", "completeness", "clarity"]
    if not rows:
        return pd.DataFrame({"criterion": criteria, "average_score": [0.0]*4})
    df = pd.DataFrame(rows)
    return pd.DataFrame({
        "criterion": criteria,
        "average_score": [round(float(df[c].mean()), 1) for c in criteria],
    })


def strongest_weakest(rows: list[dict]) -> tuple[str, str]:
    cm = category_metrics(rows)
    if cm.empty:
        return "N/A", "N/A"
    strongest = cm.iloc[0]
    weakest = cm.iloc[-1]
    return (
        f"{strongest['category']} ({strongest['average_score']:.1f}/100)",
        f"{weakest['category']} ({weakest['average_score']:.1f}/100)",
    )


def error_count(rows: list[dict]) -> int:
    return sum(1 for r in rows if r.get("status") == "ERROR")


def quality_distribution(rows: list[dict]) -> dict[str, int]:
    return dict(Counter(r.get("quality_band", "UNKNOWN") for r in rows))


def category_figure(rows: list[dict]):
    cm = category_metrics(rows)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    if cm.empty:
        ax.text(0.5, 0.5, "No benchmark data", ha="center", va="center")
        ax.set_axis_off()
        return fig
    ax.bar(cm["category"], cm["average_score"])
    ax.set_ylim(0, 100)
    ax.set_ylabel("Average Score")
    ax.set_title("Average Score by Category")
    ax.tick_params(axis="x", rotation=35)
    fig.tight_layout()
    return fig


def criterion_figure(rows: list[dict]):
    cm = criterion_metrics(rows)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(cm["criterion"], cm["average_score"])
    ax.set_ylim(0, 100)
    ax.set_ylabel("Average Score")
    ax.set_title("Evaluation Criteria")
    ax.tick_params(axis="x", rotation=25)
    fig.tight_layout()
    return fig
