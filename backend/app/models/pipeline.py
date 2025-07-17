from sqlalchemy import Column, Integer, String, DateTime
from app.database.db import Base
from datetime import datetime

class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id = Column(Integer, primary_key=True, index=True)
    repo_name = Column(String(255))
    workflow_name = Column(String(255))
    status = Column(String(50))
    conclusion = Column(String(50))
    triggered_by = Column(String(255))
    run_started_at = Column(DateTime)
    run_duration = Column(Integer)  # in seconds
    created_at = Column(DateTime, default=datetime.utcnow)
