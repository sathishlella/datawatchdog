from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.schemas import Dataset, Rule, Report, AlertHistory, Schedule
from app.models.pydantic_models import ReportOut
from app.core.checks import (
    check_null_pct, check_duplicate_pct, check_range, check_format, check_referential
)
from app.core.scorer import compute_score, RuleCheckInput
from app.core.alerter import send_quality_alert

router = APIRouter()

# In-memory store for uploaded CSV data (reset on restart)
_csv_data: dict[str, list[list]] = {}


def store_csv_data(dataset_name: str, data: list[list]):
    _csv_data[dataset_name] = data


def get_column_values(dataset_name: str, column_name: str) -> list:
    rows = _csv_data.get(dataset_name, [])
    if not rows or len(rows) < 2:
        return []
    headers = rows[0]
    if column_name not in headers:
        return []
    col_idx = headers.index(column_name)
    return [row[col_idx] if col_idx < len(row) else None for row in rows[1:]]


def run_rule_check(rule: Rule, dataset_name: str) -> RuleCheckInput:
    values = get_column_values(dataset_name, rule.column_name)
    cfg = rule.rule_config or {}

    if rule.rule_type == "null":
        result = check_null_pct(values, threshold=cfg.get("threshold", 5.0))
    elif rule.rule_type == "duplicate":
        result = check_duplicate_pct(values, threshold=cfg.get("threshold", 1.0))
    elif rule.rule_type == "range":
        result = check_range(values, min_val=cfg.get("min", 0), max_val=cfg.get("max", 1e9))
    elif rule.rule_type == "format":
        result = check_format(values, pattern=cfg.get("pattern", ".*"))
    elif rule.rule_type == "referential":
        result = check_referential(values, allowed=cfg.get("allowed", []))
    else:
        result = type("R", (), {"passed": True, "message": f"Unknown rule type: {rule.rule_type}"})()

    return RuleCheckInput(
        rule_type=rule.rule_type,
        column=rule.column_name,
        passed=result.passed,
        weight=float(rule.weight),
        message=result.message,
    )


@router.post("/{dataset_id}/run", response_model=ReportOut)
def run_quality_check(dataset_id: int, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(404, "Dataset not found")

    rules = db.query(Rule).filter(Rule.dataset_id == dataset_id).all()
    rule_results = [run_rule_check(rule, dataset.name) for rule in rules]
    score_result = compute_score(rule_results)

    report = Report(
        dataset_id=dataset_id,
        score=score_result.score,
        issues=score_result.issues,
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    schedule = db.query(Schedule).filter(
        Schedule.dataset_id == dataset_id,
        Schedule.is_active == True,
    ).first()

    if schedule and score_result.score < float(schedule.alert_threshold):
        sent = send_quality_alert(
            email=schedule.alert_email,
            dataset_name=dataset.name,
            score=score_result.score,
            threshold=float(schedule.alert_threshold),
            issues=score_result.issues,
        )
        if sent:
            alert = AlertHistory(
                dataset_id=dataset_id,
                score=score_result.score,
                threshold=schedule.alert_threshold,
                email_sent_to=schedule.alert_email,
            )
            db.add(alert)
            db.commit()

    return report


@router.get("/{dataset_id}/reports", response_model=list[ReportOut])
def get_reports(dataset_id: int, db: Session = Depends(get_db)):
    return (
        db.query(Report)
        .filter(Report.dataset_id == dataset_id)
        .order_by(Report.run_at.desc())
        .limit(20)
        .all()
    )


@router.get("/alerts", response_model=list[dict])
def get_all_alerts(db: Session = Depends(get_db)):
    alerts = (
        db.query(AlertHistory)
        .order_by(AlertHistory.sent_at.desc())
        .limit(50)
        .all()
    )
    return [
        {"id": a.id, "dataset_id": a.dataset_id, "score": float(a.score),
         "threshold": float(a.threshold), "email": a.email_sent_to,
         "sent_at": a.sent_at.isoformat()}
        for a in alerts
    ]
