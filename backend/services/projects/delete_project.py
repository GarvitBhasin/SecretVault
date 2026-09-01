from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import Action, Asset, Projects, Users
from backend.helpers import add_log, raise_error


def delete_project(id: int, user: Users, session: Session) -> None:
    # Delete project and add log
    project = session.execute(
        select(Projects).where(Projects.id == id)
    ).scalar_one_or_none()

    if project is None:
        raise_error(404, "Project not found.")

    session.delete(project)

    add_log(session, user.id, Action.DELETE, Asset.PROJECT, id)
