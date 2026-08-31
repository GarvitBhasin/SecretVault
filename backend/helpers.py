from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import update
from sqlalchemy.orm import Session
from typing import NoReturn

from backend.database import Action, Asset, Logs, Projects


def raise_error(code: int, detail: str) -> NoReturn:
    raise HTTPException(status_code=code, detail=detail)


def now():
    return datetime.now(timezone.utc).replace(microsecond=0)


def update_project_timestamp(session: Session, project_id: int):
    session.execute(
        update(Projects).where(Projects.id == project_id).values(updated_at=now())
    )


def add_log(
    session: Session, user_id: int, action: Action, asset_type: Asset, asset_id: int
):
    current_time = now()

    log = Logs(
        actor_id=user_id,
        action=action,
        asset_type=asset_type,
        asset_id=asset_id,
        action_date=current_time,
        expiry=current_time + timedelta(days=15),
    )

    session.add(log)
