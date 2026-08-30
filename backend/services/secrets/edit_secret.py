from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.database import Secrets, Action, Asset
from backend.helpers import now, raise_error, update_project_timestamp, add_log
from backend.security import encrypt

def edit_secret(
    id: int,
    name: str,
    value: str,
    description: str,
    user_id,
    session: Session
):
    # Find secret 
    secret = session.execute(
        select(Secrets)
        .where(Secrets.id == id)
    ).scalar_one_or_none()

    if secret is None:
        raise_error(404, "Secret not found.")

    # Update secret values
    secret.name = name
    secret.value = encrypt(value)
    secret.description = description if description else ""
    secret.updated_at = now()

    # Update project's last updated column and add log
    update_project_timestamp(session, secret.project_id)

    add_log(session, user_id, Action.UPDATE, Asset.SECRET, id)