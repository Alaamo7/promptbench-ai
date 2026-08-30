from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.benchmark import BenchmarkEngine
from src.evaluator import EvaluationEngine


class FakeTargetClient:
    def chat(self, prompt, model=None, **kwargs):
        if "JSON" in prompt or "json" in prompt:
            return '{"name":"Ahmed","role":"Engineer"}'
        if "bullet" in prompt.lower() or "نقط" in prompt:
            return "- First point\n- Second point\n- Third point\n- Fourth point\n- Fifth point"
        return "This is a concise test response."


class FakeJudgeClient:
    def chat(self, prompt, model=None, **kwargs):
        return '{"instruction_following":88,"relevance":93,"completeness":85,"clarity":91,"reason":"Offline smoke evaluation"}'


engine = BenchmarkEngine(
    target_client=FakeTargetClient(),
    evaluator=EvaluationEngine(FakeJudgeClient()),
)
cases = engine.select_cases(limit=5)
run = engine.run("fake-model", cases)
assert run.summary["tests_run"] == 5
assert len(run.rows) == 5
print("OFFLINE BENCHMARK SMOKE: PASS")
print(run.summary)
