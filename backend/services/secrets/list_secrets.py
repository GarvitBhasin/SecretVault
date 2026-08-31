from sqlalchemy.orm import Session
from sqlalchemy import select
from backend.database import Projects, Secrets, Users
from backend.helpers import raise_error

def list_secrets(
    id: int,
    session: Session
):
    # Check if project exists
    project_found = session.execute(
        select(Projects)
        .where(Projects.id == id)
    ).first()

    if not project_found:
        raise_error(404, "Project not found.")

    # Join Secrets with creator's corrosponding username
    secrets = session.execute(
        select(Secrets, Users.username)
        .where(Secrets.project_id == id)
        .outerjoin(Users, Users.id == Secrets.creator_id)
        .order_by(Secrets.id.asc())
    ).all()

    if not secrets:
        raise_error(404, "No secrets found.")

    secrets_list = []

    # Create array of secret dicts (used to display table on cli)
    for secret, username in secrets:

        secrets_list.append({
            "id": str(secret.id),
            "name": secret.name,
            "creator": username if username else "Deleted user",
            "created_at": str(secret.created_at),
            "updated_at": str(secret.updated_at),
        })

    return secrets_list