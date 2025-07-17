from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.db import SessionLocal
from app.services.github_service import get_pipeline_runs
from app.models.pipeline import PipelineRun
from datetime import datetime

router = APIRouter(prefix="/pipelines")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/{owner}/{repo}")
def fetch_pipelines(owner: str, repo: str, db: Session = Depends(get_db)):
    full_repo_name = f"{owner}/{repo}"
    data = get_pipeline_runs(full_repo_name)
    runs = data.get("workflow_runs", [])

    inserted = 0
    for run in runs:
        started_str = run.get("run_started_at") or run.get("created_at")
        updated_str = run.get("updated_at")

        if not started_str or not updated_str:
            continue

        try:
            run_started_at = datetime.strptime(started_str, "%Y-%m-%dT%H:%M:%SZ")
            updated_at = datetime.strptime(updated_str, "%Y-%m-%dT%H:%M:%SZ")
            run_duration = int((updated_at - run_started_at).total_seconds())
        except Exception:
            continue

        # Avoid duplicate entries
        existing = db.query(PipelineRun).filter(
            PipelineRun.repo_name == full_repo_name,
            PipelineRun.workflow_name == run.get("name"),
            PipelineRun.run_started_at == run_started_at
        ).first()

        if existing:
            continue

        pipeline = PipelineRun(
            repo_name=full_repo_name,
            workflow_name=run.get("name"),
            status=run.get("status"),
            conclusion=run.get("conclusion"),
            triggered_by=run.get("triggering_actor", {}).get("login"),
            run_started_at=run_started_at,
            run_duration=run_duration
        )
        db.add(pipeline)
        inserted += 1

    db.commit()
    return {"message": f"{inserted} new pipeline runs stored (out of {len(runs)} total)"}


@router.get("/{owner}/{repo}/summary")
def pipeline_summary(owner: str, repo: str, db: Session = Depends(get_db)):
    full_repo_name = f"{owner}/{repo}"

    success_count = db.query(PipelineRun).filter(
        PipelineRun.repo_name == full_repo_name,
        PipelineRun.conclusion == "success"
    ).count()

    failure_count = db.query(PipelineRun).filter(
        PipelineRun.repo_name == full_repo_name,
        PipelineRun.conclusion == "failure"
    ).count()

    return {
        "repo": full_repo_name,
        "success": success_count,
        "failure": failure_count
    }


@router.get("/history/{owner}/{repo}")
def get_pipeline_history(owner: str, repo: str):
    db = SessionLocal()
    try:
        runs = db.query(PipelineRun).filter_by(owner=owner, repo=repo).all()
        return [
            {
                "workflow_name": run.workflow_name,
                "run_started_at": run.run_started_at.isoformat() if run.run_started_at else None,
                "triggered_by": run.triggered_by,
                "run_duration": run.run_duration,
                "conclusion": run.conclusion
            }
            for run in runs
        ]
    finally:
        db.close()