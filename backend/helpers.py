from fastapi import HTTPException
from datetime import datetime, timezone, timedelta
from backend.database import Projects, Secrets, Logs, Action, Asset
from sqlalchemy import select, update
from sqlalchemy.orm import Session

def raise_error(code: int, detail: str):
    raise HTTPException(
        status_code=code,
        detail=detail
    )

def now():
    return datetime.now(timezone.utc).replace(microsecond=0)

def update_project_timestamp(session: Session, project_id: int):
    session.execute(
        update(Projects)
        .where(Projects.id == project_id)
        .values(updated_at = now())
    )

def find_project(session: Session, id: int):
    project_id = session.execute(
        select(Secrets.project_id)
        .where(Secrets.id == id)
    ).scalar_one_or_none()

    if project_id is None:
        raise_error(404, "Secret not found.")

    return project_id

def add_log(session: Session, user_id: int, action: Action, asset_type: Asset, asset_id: int):
    current_time = now()

    log = Logs(
        actor_id=user_id,
        action=action,
        asset_type=asset_type,
        asset_id=asset_id,
        action_date=current_time,
        expiry=current_time+timedelta(days=15)
    )

    session.add(log)