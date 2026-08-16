from fastapi import HTTPException
from datetime import datetime, timezone, timedelta
from backend.database import Projects, Secrets, Logs
from sqlalchemy import select, update

def raise_error(code, detail):
    raise HTTPException(
        status_code=code,
        detail=detail
    )

def now():
    return datetime.now(timezone.utc).replace(microsecond=0)

def update_project_timestamp(session, project_id):
    session.execute(
        update(Projects)
        .where(Projects.id == project_id)
        .values(updated_at = now())
    )

def find_project(session, id):
    project_id = session.execute(
        select(Secrets.project_id)
        .where(Secrets.id == id)
    ).scalar_one_or_none()

    if project_id is None:
        raise_error(404, "Secret not found.")

    return project_id

def add_log(session, user_id, action, asset_type, asset_id):
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