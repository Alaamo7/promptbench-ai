from __future__ import annotations

from .schemas import EvaluationResult


ARABIC_VERDICTS = {
    "UNDERSTOOD": "✔ فهم التعليمات",
    "FAILED": "❌ لم يفهم التعليمات",
}

ARABIC_BANDS = {
    "EXCELLENT": "ممتاز",
    "GOOD": "جيد",
    "PARTIAL": "فهم جزئي",
    "POOR": "ضعيف",
}


def result_markdown(result: EvaluationResult) -> str:
    verdict = ARABIC_VERDICTS[result.verdict]
    band = ARABIC_BANDS[result.quality_band]
    return f"""## {verdict}

**الدرجة النهائية:** {result.overall_score}/100  
**مستوى الجودة:** {band}

- Instruction Following: **{result.scores.instruction_following}/100**
- Relevance: **{result.scores.relevance}/100**
- Completeness: **{result.scores.completeness}/100**
- Clarity: **{result.scores.clarity}/100**

**سبب التقييم:** {result.reason or 'لا يوجد تفسير من نموذج التقييم.'}
"""
