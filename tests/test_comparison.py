from src.benchmark import BenchmarkEngine
from src.comparison import ComparisonEngine
from src.evaluator import EvaluationEngine


class ModelAwareTarget:
    def chat(self, prompt, model=None, **kwargs):
        if model == "strong":
            return "- One\n- Two"
        return "One answer"


class Judge:
    def chat(self, prompt, model=None, **kwargs):
        response_block = prompt.split("MODEL RESPONSE:", 1)[-1]
        score = 95 if "- One" in response_block else 60
        return '{"instruction_following":%d,"relevance":%d,"completeness":%d,"clarity":%d,"reason":"test"}' % (score, score, score, score)


def test_comparison_requires_two_models():
    benchmark = BenchmarkEngine(target_client=ModelAwareTarget(), evaluator=EvaluationEngine(Judge()))
    engine = ComparisonEngine(benchmark, evaluator_model="judge")
    cases = [{"id":"1","category":"formatting","language":"en","prompt":"two bullets","rules":{"exact_bullets":2}}]
    try:
        engine.run(["strong"], cases)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_same_cases_and_winner_ranked():
    benchmark = BenchmarkEngine(target_client=ModelAwareTarget(), evaluator=EvaluationEngine(Judge()))
    engine = ComparisonEngine(benchmark, evaluator_model="judge")
    cases = [
        {"id":"1","category":"formatting","language":"en","prompt":"two bullets","rules":{"exact_bullets":2}},
        {"id":"2","category":"general","language":"en","prompt":"answer","rules":{}},
    ]
    result = engine.run(["weak", "strong", "weak"], cases)
    assert result.case_ids == ["1", "2"]
    assert list(result.runs) == ["weak", "strong"]
    assert result.leaderboard.iloc[0]["rank"] == 1
    assert result.winner in {"weak", "strong"}
    assert all(run.summary["tests_run"] == 2 for run in result.runs.values())


def test_category_table_has_each_model():
    benchmark = BenchmarkEngine(target_client=ModelAwareTarget(), evaluator=EvaluationEngine(Judge()))
    engine = ComparisonEngine(benchmark, evaluator_model="judge")
    cases = [{"id":"1","category":"formatting","language":"en","prompt":"two bullets","rules":{"exact_bullets":2}}]
    result = engine.run(["weak", "strong"], cases)
    assert set(result.category_table["model"]) == {"weak", "strong"}


def test_comparison_applies_delay_between_all_requests(monkeypatch):
    sleeps = []
    monkeypatch.setattr("src.benchmark.time.sleep", sleeps.append)
    monkeypatch.setattr("src.comparison.time.sleep", sleeps.append)
    benchmark = BenchmarkEngine(target_client=ModelAwareTarget(), evaluator=EvaluationEngine(Judge()))
    engine = ComparisonEngine(benchmark, evaluator_model="judge", provider="test-provider")
    cases = [
        {"id":"1","category":"formatting","language":"en","prompt":"two bullets","rules":{"exact_bullets":2}},
        {"id":"2","category":"general","language":"en","prompt":"answer","rules":{}},
    ]
    result = engine.run(["weak", "strong"], cases, delay_seconds=5)
    assert sleeps == [5, 5, 5]
    assert result.provider == "test-provider"
    assert all([row["id"] for row in run.rows] == ["1", "2"] for run in result.runs.values())
