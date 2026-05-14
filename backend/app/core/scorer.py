from dataclasses import dataclass


@dataclass
class RuleCheckInput:
    rule_type: str
    column: str
    passed: bool
    weight: float
    message: str


@dataclass
class ScoreResult:
    score: float
    issues: list[dict]


def compute_score(rule_results: list[RuleCheckInput]) -> ScoreResult:
    if not rule_results:
        return ScoreResult(score=100.0, issues=[])

    total_weight = sum(r.weight for r in rule_results)
    passing_weight = sum(r.weight for r in rule_results if r.passed)

    score = round((passing_weight / total_weight) * 100, 2) if total_weight > 0 else 100.0

    issues = [
        {"column": r.column, "rule_type": r.rule_type, "message": r.message}
        for r in rule_results
        if not r.passed
    ]

    return ScoreResult(score=score, issues=issues)
