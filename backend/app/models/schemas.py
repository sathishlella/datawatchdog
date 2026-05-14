from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Numeric, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.models.database import Base


class Dataset(Base):
    __tablename__ = "datasets"
    __table_args__ = {"schema": "datawatchdog"}

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    columns = Column(JSON, nullable=False, default=list)
    row_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    rules = relationship("Rule", back_populates="dataset", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="dataset", cascade="all, delete-orphan")
    schedules = relationship("Schedule", back_populates="dataset", cascade="all, delete-orphan")


class Rule(Base):
    __tablename__ = "rules"
    __table_args__ = {"schema": "datawatchdog"}

    id = Column(Integer, primary_key=True)
    dataset_id = Column(Integer, ForeignKey("datawatchdog.datasets.id"), nullable=False)
    column_name = Column(String(100), nullable=False)
    rule_type = Column(String(20), nullable=False)
    rule_config = Column(JSON, nullable=False, default=dict)
    weight = Column(Numeric(4, 2), nullable=False, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    dataset = relationship("Dataset", back_populates="rules")


class Report(Base):
    __tablename__ = "reports"
    __table_args__ = {"schema": "datawatchdog"}

    id = Column(Integer, primary_key=True)
    dataset_id = Column(Integer, ForeignKey("datawatchdog.datasets.id"), nullable=False)
    score = Column(Numeric(5, 2), nullable=False)
    issues = Column(JSON, nullable=False, default=list)
    run_at = Column(DateTime, default=datetime.utcnow)

    dataset = relationship("Dataset", back_populates="reports")


class AlertHistory(Base):
    __tablename__ = "alert_history"
    __table_args__ = {"schema": "datawatchdog"}

    id = Column(Integer, primary_key=True)
    dataset_id = Column(Integer, ForeignKey("datawatchdog.datasets.id"), nullable=False)
    score = Column(Numeric(5, 2), nullable=False)
    threshold = Column(Numeric(5, 2), nullable=False)
    email_sent_to = Column(String(200), nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow)


class Schedule(Base):
    __tablename__ = "schedules"
    __table_args__ = {"schema": "datawatchdog"}

    id = Column(Integer, primary_key=True)
    dataset_id = Column(Integer, ForeignKey("datawatchdog.datasets.id"), nullable=False)
    cron_expression = Column(String(50), nullable=False)
    alert_email = Column(String(200), nullable=False)
    alert_threshold = Column(Numeric(5, 2), nullable=False, default=80.0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    dataset = relationship("Dataset", back_populates="schedules")
