import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.benchmark import BenchmarkEngine
from src.comparison import ComparisonEngine
from src.evaluator import EvaluationEngine

class FakeTarget:
    def chat(self, prompt, model=None, **kwargs):
        if model == "model-alpha":
            return "- First\n- Second"
        return "A short response."

class FakeJudge:
    def chat(self, prompt, model=None, **kwargs):
        response = prompt.split("MODEL RESPONSE:",1)[-1]
        score = 94 if "- First" in response else 78
        return '{"instruction_following":%d,"relevance":%d,"completeness":%d,"clarity":%d,"reason":"offline smoke"}' % (score,score,score,score)

cases = [
    {"id":"cmp-01","category":"formatting","language":"en","prompt":"Give exactly two bullet points.","rules":{"exact_bullets":2}},
    {"id":"cmp-02","category":"general","language":"en","prompt":"Explain DNS briefly.","rules":{}},
]
benchmark = BenchmarkEngine(target_client=FakeTarget(), evaluator=EvaluationEngine(FakeJudge()))
comparison = ComparisonEngine(benchmark, evaluator_model="offline-judge").run(["model-alpha","model-beta"], cases)
print(comparison.leaderboard.to_string(index=False))
print("Winner:", comparison.winner)
assert len(comparison.leaderboard) == 2
assert comparison.winner in {"model-alpha", "model-beta"}
assert all(run.summary["tests_run"] == len(cases) for run in comparison.runs.values())
print("OFFLINE COMPARISON SMOKE: PASS")
