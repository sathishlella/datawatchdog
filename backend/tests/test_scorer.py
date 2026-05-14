import pytest
from app.core.scorer import compute_score, RuleCheckInput, ScoreResult


def test_all_passing_rules_gives_100():
    rules = [
        RuleCheckInput(rule_type="null", column="age", passed=True, weight=1.0, message="ok"),
        RuleCheckInput(rule_type="range", column="age", passed=True, weight=1.0, message="ok"),
    ]
    result = compute_score(rules)
    assert result.score == 100.0
    assert len(result.issues) == 0


def test_one_failing_rule_reduces_score():
    rules = [
        RuleCheckInput(rule_type="null", column="age", passed=True, weight=1.0, message="ok"),
        RuleCheckInput(rule_type="range", column="age", passed=False, weight=1.0,
                       message="2 values out of range"),
    ]
    result = compute_score(rules)
    assert result.score < 100.0
    assert len(result.issues) == 1


def test_weighted_rules():
    rules = [
        RuleCheckInput(rule_type="null", column="name", passed=False, weight=2.0,
                       message="high null rate"),
        RuleCheckInput(rule_type="format", column="email", passed=True, weight=1.0, message="ok"),
    ]
    result = compute_score(rules)
    # Weight-2 failing rule: score = 1/(2+1) * 100 = 33.33
    assert result.score == pytest.approx(33.33, abs=0.1)


def test_empty_rules_returns_100():
    result = compute_score([])
    assert result.score == 100.0
