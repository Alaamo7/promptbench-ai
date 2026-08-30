from src import history


def test_history_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(history, "HISTORY_DIR", tmp_path)
    monkeypatch.setattr(history, "HISTORY_FILE", tmp_path / "runs.jsonl")
    rec = history.save_run("target", "judge", {"tests_run":2,"pass_rate":50,"average_score":70}, [{"id":"x"}])
    loaded = history.load_runs()
    assert loaded[0]["run_id"] == rec["run_id"]
    assert history.get_run(rec["run_id"])["target_model"] == "target"
