import re
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class CheckResult:
    passed: bool
    actual_value: float
    message: str


def check_null_pct(values: list[Any], threshold: float) -> CheckResult:
    if not values:
        return CheckResult(passed=True, actual_value=0.0, message="No values to check")
    null_count = sum(1 for v in values if v is None or (isinstance(v, float) and v != v))
    pct = round((null_count / len(values)) * 100, 2)
    passed = pct <= threshold
    msg = f"Null rate: {pct}% (threshold: {threshold}%)"
    return CheckResult(passed=passed, actual_value=pct, message=msg)


def check_duplicate_pct(values: list[Any], threshold: float) -> CheckResult:
    if not values:
        return CheckResult(passed=True, actual_value=0.0, message="No values to check")
    non_null = [v for v in values if v is not None]
    if not non_null:
        return CheckResult(passed=True, actual_value=0.0, message="All null")
    duplicate_count = len(non_null) - len(set(str(v) for v in non_null))
    pct = round((duplicate_count / len(non_null)) * 100, 2)
    passed = pct <= threshold
    msg = f"Duplicate rate: {pct}% (threshold: {threshold}%)"
    return CheckResult(passed=passed, actual_value=pct, message=msg)


def check_range(values: list[Any], min_val: float, max_val: float) -> CheckResult:
    numeric = []
    for v in values:
        try:
            numeric.append(float(v))
        except (TypeError, ValueError):
            pass
    if not numeric:
        return CheckResult(passed=True, actual_value=0.0, message="No numeric values")
    out_of_range = [v for v in numeric if v < min_val or v > max_val]
    pct = round((len(out_of_range) / len(numeric)) * 100, 2)
    passed = len(out_of_range) == 0
    msg = f"{len(out_of_range)} value(s) outside [{min_val}, {max_val}] — {pct}% of total"
    return CheckResult(passed=passed, actual_value=pct, message=msg)


def check_format(values: list[Any], pattern: str) -> CheckResult:
    compiled = re.compile(pattern)
    non_null = [str(v) for v in values if v is not None]
    if not non_null:
        return CheckResult(passed=True, actual_value=0.0, message="No non-null values")
    failures = [v for v in non_null if not compiled.match(v)]
    pct = round((len(failures) / len(non_null)) * 100, 2)
    passed = len(failures) == 0
    msg = f"{len(failures)} value(s) do not match pattern '{pattern}' — {pct}% fail rate"
    return CheckResult(passed=passed, actual_value=pct, message=msg)


def check_referential(values: list[Any], allowed: list[str]) -> CheckResult:
    allowed_set = set(allowed)
    non_null = [str(v) for v in values if v is not None]
    if not non_null:
        return CheckResult(passed=True, actual_value=0.0, message="No non-null values")
    invalid = [v for v in non_null if v not in allowed_set]
    pct = round((len(invalid) / len(non_null)) * 100, 2)
    passed = len(invalid) == 0
    msg = f"{len(invalid)} value(s) not in allowed set — {pct}% invalid. Examples: {invalid[:3]}"
    return CheckResult(passed=passed, actual_value=pct, message=msg)
