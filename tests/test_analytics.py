from src.analytics import category_metrics, criterion_metrics, strongest_weakest, error_count

ROWS = [
    {"category":"a","verdict":"UNDERSTOOD","overall_score":90,"status":"OK","instruction_following":90,"relevance":90,"completeness":90,"clarity":90},
    {"category":"a","verdict":"FAILED","overall_score":50,"status":"OK","instruction_following":50,"relevance":50,"completeness":50,"clarity":50},
    {"category":"b","verdict":"UNDERSTOOD","overall_score":80,"status":"ERROR","instruction_following":80,"relevance":80,"completeness":80,"clarity":80},
]

def test_category_metrics():
    df = category_metrics(ROWS)
    a = df[df.category == "a"].iloc[0]
    assert a.tests == 2
    assert a.pass_rate == 50.0
    assert a.average_score == 70.0


def test_criterion_and_strength():
    df = criterion_metrics(ROWS)
    assert set(df.criterion) == {"instruction_following","relevance","completeness","clarity"}
    strongest, weakest = strongest_weakest(ROWS)
    assert strongest.startswith("b")
    assert weakest.startswith("a")
    assert error_count(ROWS) == 1
