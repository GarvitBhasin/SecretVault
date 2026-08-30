from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.database import Logs, Users
from backend.security import check_credentials, hash_password
from backend.helpers import raise_error, add_log

def list_logs(
    session: Session
):
    logs_obj = session.execute(
        select(Logs, Users.username)
        .outerjoin(Users, Logs.actor_id == Users.id)
    ).all()

    logs = []

    for log, username in logs_obj:
        logs.append({
            "id": str(log.id),
            "actor": username if username else "Deleted User",
            "action": log.action,
            "asset_type": log.asset_type,
            "asset_id": str(log.asset_id),
            "action_date": str(log.action_date)
        })

    return logs