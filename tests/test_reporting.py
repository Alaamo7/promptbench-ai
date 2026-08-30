from src.reporting import build_graduation_report


def test_report_contains_core_sections():
    run = {"target_model":"model-a", "evaluator_model":"judge-b", "summary":{"tests_run":10,"pass_rate":80,"average_score":82,"passed":8,"failed":2}}
    comp = {"winner":"model-a", "evaluator_model":"judge-b", "provider":"test", "case_ids":["1"], "leaderboard":[{"rank":1,"model":"model-a","tests_run":10,"pass_rate":80,"average_score":82,"errors":0}]}
    text = build_graduation_report(run, comp, app_url="https://example.invalid")
    assert "PromptBench AI" in text
    assert "model-a" in text
    assert "80.0%" in text
    assert "Limitations" in text
    assert "https://example.invalid" in text
    assert "Latest Comparison Leaderboard" in text
