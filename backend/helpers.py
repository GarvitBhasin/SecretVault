from fastapi import HTTPException
from datetime import datetime, timezone
from backend.models import Projects, Secrets
from sqlalchemy import select, update

def raise_error(code, detail):
    raise HTTPException(
        status_code=code,
        detail=detail
    )

def now():
    return datetime.now(timezone.utc).replace(microsecond=0)

def update_project_timestamp(session, data):
    project_id = session.execute(
        select(Secrets.project_id)
        .where(Secrets.id == data.id)
    ).scalar_one_or_none()

    updated = session.execute(
        update(Projects)
        .where(Projects.id == project_id)
        .values(updated_at = now())
    )