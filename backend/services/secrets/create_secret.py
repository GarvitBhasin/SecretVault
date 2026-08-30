from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.database import Projects, Secrets, Action, Asset
from backend.helpers import raise_error, now, update_project_timestamp, add_log
from backend.security import encrypt

def create_secret(
    id: int,
    name: str,
    description: str,
    value: str,
    user_id: int,
    session: Session
):
    project = session.execute(
        select(Projects)
        .where(Projects.id == id)
    ).scalar_one_or_none()

    if project is None:
        raise_error(404, "Project not found.")

    # Create secret object and add to db
    current_time = now()
    secret = Secrets(
        name = name,
        value = encrypt(value),
        description = description,
        project_id = id,
        creator_id = user_id,
        created_at = current_time,
        updated_at = current_time
    )

    session.add(secret)
    session.flush()

    # Update project last updated column
    update_project_timestamp(session, id)

    add_log(session, user_id, Action.CREATE, Asset.SECRET, secret.id)