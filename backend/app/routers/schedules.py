from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.schemas import Schedule, Dataset
from app.models.pydantic_models import ScheduleCreate, ScheduleOut
from app.core.scheduler import get_scheduler

router = APIRouter()


@router.post("/", response_model=ScheduleOut)
def create_schedule(body: ScheduleCreate, db: Session = Depends(get_db)):
    if not db.query(Dataset).filter(Dataset.id == body.dataset_id).first():
        raise HTTPException(404, "Dataset not found")

    sched = Schedule(**body.model_dump())
    db.add(sched)
    db.commit()
    db.refresh(sched)

    scheduler = get_scheduler()
    scheduler.add_job(
        _run_scheduled_check,
        trigger="cron",
        id=f"schedule_{sched.id}",
        replace_existing=True,
        kwargs={"dataset_id": sched.dataset_id},
        **_parse_cron(sched.cron_expression),
    )
    return sched


@router.get("/", response_model=list[ScheduleOut])
def list_schedules(db: Session = Depends(get_db)):
    return db.query(Schedule).all()


@router.delete("/{schedule_id}")
def delete_schedule(schedule_id: int, db: Session = Depends(get_db)):
    sched = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not sched:
        raise HTTPException(404, "Schedule not found")
    scheduler = get_scheduler()
    try:
        scheduler.remove_job(f"schedule_{schedule_id}")
    except Exception:
        pass
    db.delete(sched)
    db.commit()
    return {"deleted": schedule_id}


def _parse_cron(expr: str) -> dict:
    """Parse '0 */6 * * *' into APScheduler cron kwargs."""
    parts = expr.strip().split()
    if len(parts) != 5:
        return {"minute": "0", "hour": "*"}
    return {
        "minute": parts[0], "hour": parts[1],
        "day": parts[2], "month": parts[3], "day_of_week": parts[4],
    }


async def _run_scheduled_check(dataset_id: int):
    """Called by APScheduler — runs quality check for a dataset."""
    from app.models.database import SessionLocal
    from app.models.schemas import Dataset, Rule, Report, AlertHistory, Schedule
    from app.core.scorer import compute_score
    from app.core.alerter import send_quality_alert
    from app.routers.reports import run_rule_check

    db = SessionLocal()
    try:
        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            return
        rules = db.query(Rule).filter(Rule.dataset_id == dataset_id).all()
        rule_results = [run_rule_check(rule, dataset.name) for rule in rules]
        score_result = compute_score(rule_results)
        report = Report(dataset_id=dataset_id, score=score_result.score,
                        issues=score_result.issues)
        db.add(report)
        db.commit()

        schedule = db.query(Schedule).filter(
            Schedule.dataset_id == dataset_id, Schedule.is_active == True
        ).first()
        if schedule and score_result.score < float(schedule.alert_threshold):
            sent = send_quality_alert(
                schedule.alert_email, dataset.name,
                score_result.score, float(schedule.alert_threshold),
                score_result.issues,
            )
            if sent:
                db.add(AlertHistory(
                    dataset_id=dataset_id, score=score_result.score,
                    threshold=schedule.alert_threshold,
                    email_sent_to=schedule.alert_email,
                ))
                db.commit()
    finally:
        db.close()
