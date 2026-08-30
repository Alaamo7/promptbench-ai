from src.schemas import CriterionScores
from src.scoring import deterministic_penalty, weighted_score


def test_weighted_score():
    s = CriterionScores(instruction_following=100, relevance=100, completeness=100, clarity=100)
    assert weighted_score(s) == 100


def test_penalty():
    assert deterministic_penalty({"max_words_pass": False, "json_pass": False}) == 20
    assert deterministic_penalty({"max_words_pass": False, "bullet_count_pass": False}) == 20
