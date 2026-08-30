from src.benchmark import BenchmarkEngine, BenchmarkRun
from src.evaluator import EvaluationEngine


class FakeTargetClient:
    def chat(self, prompt, model=None, **kwargs):
        if "bullet" in prompt.lower() or "نقط" in prompt:
            return "- One\n- Two"
        return "A concise answer."


class FakeJudgeClient:
    def chat(self, prompt, model=None, **kwargs):
        return '{"instruction_following":90,"relevance":95,"completeness":88,"clarity":92,"reason":"Good"}'


def test_summary_metrics():
    run = BenchmarkRun([
        {"category":"a","overall_score":80,"verdict":"UNDERSTOOD"},
        {"category":"a","overall_score":60,"verdict":"FAILED"},
        {"category":"b","overall_score":90,"verdict":"UNDERSTOOD"},
    ])
    s = run.summary
    assert s["tests_run"] == 3
    assert s["passed"] == 2
    assert s["failed"] == 1
    assert s["pass_rate"] == 66.7
    assert s["average_score"] == 76.7
    assert s["category_scores"] == {"a": 70.0, "b": 90.0}


def test_case_selection_filters():
    engine = BenchmarkEngine(target_client=FakeTargetClient(), evaluator=EvaluationEngine(FakeJudgeClient()))
    cases = engine.select_cases(categories=["translation"], limit=2)
    assert len(cases) == 2
    assert all(c["category"] == "translation" for c in cases)

class FailingTargetClient:
    def __init__(self):
        self.calls = 0
    def chat(self, prompt, model=None, **kwargs):
        self.calls += 1
        if self.calls == 1:
            raise RuntimeError("temporary failure")
        return "A concise answer."


def test_batch_continues_after_case_error():
    engine = BenchmarkEngine(target_client=FailingTargetClient(), evaluator=EvaluationEngine(FakeJudgeClient()))
    cases = engine.select_cases(limit=2)
    run = engine.run("fake-model", cases)
    assert len(run.rows) == 2
    assert run.rows[0]["status"] == "ERROR"
    assert run.rows[0]["verdict"] == "FAILED"
    assert run.rows[1]["status"] == "OK"


def test_batch_applies_delay_only_between_cases(monkeypatch):
    sleeps = []
    monkeypatch.setattr("src.benchmark.time.sleep", sleeps.append)
    engine = BenchmarkEngine(target_client=FakeTargetClient(), evaluator=EvaluationEngine(FakeJudgeClient()))
    cases = engine.select_cases(limit=2)
    run = engine.run("fake-model", cases, delay_seconds=10)
    assert len(run.rows) == 2
    assert sleeps == [10]
