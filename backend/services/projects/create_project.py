from sqlalchemy.orm import Session

from backend.database import Action, Asset, Projects, Users
from backend.helpers import add_log, now


def create_project(name: str, user: Users, session: Session) -> None:
    # Create project object and add to db
    current_time = now()
    project = Projects(
        name=name, creator_id=user.id, created_at=current_time, updated_at=current_time
    )

    session.add(project)
    session.flush()

    add_log(session, user.id, Action.CREATE, Asset.PROJECT, project.id)
