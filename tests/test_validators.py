from src.validators import bullet_count, is_valid_json, run_rule_checks, sentence_count, word_count


def test_counts_and_json():
    assert word_count("one two three") == 3
    assert sentence_count("One. Two! Three?") == 3
    assert bullet_count("- a\n- b\ntext") == 2
    assert is_valid_json('{"ok": true}')


def test_rule_checks():
    checks = run_rule_checks("- Alpha\n- Beta", {"exact_bullets": 2, "required_terms": ["Alpha"], "forbidden_terms": ["Gamma"]})
    assert checks["bullet_count_pass"] is True
    assert checks["required:Alpha"] is True
    assert checks["forbidden:Gamma"] is True
