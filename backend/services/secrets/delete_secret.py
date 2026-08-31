from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import Action, Asset, Secrets
from backend.helpers import add_log, raise_error, update_project_timestamp


def delete_secret(id: int, user_id, session: Session):
    # Find secret
    secret = session.execute(
        select(Secrets).where(Secrets.id == id)
    ).scalar_one_or_none()

    if secret is None:
        raise_error(404, "Secret not found.")

    # Update project's updated at column
    update_project_timestamp(session, secret.project_id)

    # Delete secret and add log
    session.delete(secret)

    add_log(session, user_id, Action.DELETE, Asset.SECRET, id)
