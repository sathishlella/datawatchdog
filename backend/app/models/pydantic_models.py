from datetime import datetime
from decimal import Decimal
from typing import Any, Optional
from pydantic import BaseModel


class DatasetCreate(BaseModel):
    name: str
    columns: list[str]
    row_count: int = 0


class DatasetOut(BaseModel):
    id: int
    name: str
    columns: list[Any]
    row_count: int
    created_at: datetime
    model_config = {"from_attributes": True}


class RuleCreate(BaseModel):
    column_name: str
    rule_type: str  # 'null' | 'duplicate' | 'range' | 'format' | 'referential'
    rule_config: dict[str, Any] = {}
    weight: float = 1.0


class RuleOut(BaseModel):
    id: int
    dataset_id: int
    column_name: str
    rule_type: str
    rule_config: dict[str, Any]
    weight: Decimal
    model_config = {"from_attributes": True}


class ReportOut(BaseModel):
    id: int
    dataset_id: int
    score: Decimal
    issues: list[Any]
    run_at: datetime
    model_config = {"from_attributes": True}


class ScheduleCreate(BaseModel):
    dataset_id: int
    cron_expression: str
    alert_email: str
    alert_threshold: float = 80.0


class ScheduleOut(BaseModel):
    id: int
    dataset_id: int
    cron_expression: str
    alert_email: str
    alert_threshold: Decimal
    is_active: bool
    model_config = {"from_attributes": True}


class AlertHistoryOut(BaseModel):
    id: int
    dataset_id: int
    score: Decimal
    threshold: Decimal
    email_sent_to: str
    sent_at: datetime
    model_config = {"from_attributes": True}
