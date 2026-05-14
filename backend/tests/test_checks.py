import pytest
from app.core.checks import (
    check_null_pct, check_duplicate_pct, check_range, check_format, check_referential,
    CheckResult,
)


def test_null_check_passes_when_below_threshold():
    values = ["Alice", "Bob", "Carol", None, "Dave"]  # 20% null
    result = check_null_pct(values, threshold=25.0)
    assert result.passed is True
    assert result.actual_value == pytest.approx(20.0)


def test_null_check_fails_when_above_threshold():
    values = [None, None, "Alice", "Bob"]  # 50% null
    result = check_null_pct(values, threshold=25.0)
    assert result.passed is False
    assert "50.0%" in result.message


def test_duplicate_check_passes_when_below_threshold():
    values = ["a", "b", "c", "d", "d"]  # 20% duplicate
    result = check_duplicate_pct(values, threshold=25.0)
    assert result.passed is True


def test_duplicate_check_fails():
    values = ["a", "a", "a", "b"]  # 75% duplicate
    result = check_duplicate_pct(values, threshold=25.0)
    assert result.passed is False


def test_range_check_passes():
    values = [10, 20, 30, 40]
    result = check_range(values, min_val=0.0, max_val=100.0)
    assert result.passed is True


def test_range_check_fails_with_outliers():
    values = [10, 20, 999]  # 999 out of range
    result = check_range(values, min_val=0.0, max_val=100.0)
    assert result.passed is False
    assert "1 value" in result.message.lower() or "33" in result.message


def test_format_check_passes():
    values = ["2024-01-15", "2024-06-30", "2025-01-01"]
    result = check_format(values, pattern=r"^\d{4}-\d{2}-\d{2}$")
    assert result.passed is True


def test_format_check_fails():
    values = ["2024-01-15", "not-a-date", "01/15/2024"]
    result = check_format(values, pattern=r"^\d{4}-\d{2}-\d{2}$")
    assert result.passed is False


def test_referential_check_passes():
    values = ["Male", "Female", "Non-binary", "Male"]
    result = check_referential(values, allowed=["Male", "Female", "Non-binary"])
    assert result.passed is True


def test_referential_check_fails():
    values = ["Male", "Female", "Unknown"]
    result = check_referential(values, allowed=["Male", "Female"])
    assert result.passed is False
