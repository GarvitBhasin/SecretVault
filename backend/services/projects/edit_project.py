from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import Action, Asset, Projects, Users
from backend.helpers import add_log, now, raise_error


def edit_project(name: str, id: int, user: Users, session: Session) -> None:
    # Edit project and add log
    project = session.execute(
        select(Projects).where(Projects.id == id)
    ).scalar_one_or_none()

    if project is None:
        raise_error(404, "Project not found.")

    project.name = name
    project.updated_at = now()

    add_log(session, user.id, Action.UPDATE, Asset.PROJECT, id)
