from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.schemas import Rule, Dataset
from app.models.pydantic_models import RuleCreate, RuleOut

router = APIRouter()


@router.get("/{dataset_id}/rules", response_model=list[RuleOut])
def get_rules(dataset_id: int, db: Session = Depends(get_db)):
    return db.query(Rule).filter(Rule.dataset_id == dataset_id).all()


@router.post("/{dataset_id}/rules", response_model=RuleOut)
def create_rule(dataset_id: int, rule: RuleCreate, db: Session = Depends(get_db)):
    if not db.query(Dataset).filter(Dataset.id == dataset_id).first():
        raise HTTPException(404, "Dataset not found")
    r = Rule(dataset_id=dataset_id, **rule.model_dump())
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@router.delete("/rules/{rule_id}")
def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not rule:
        raise HTTPException(404, "Rule not found")
    db.delete(rule)
    db.commit()
    return {"deleted": rule_id}
