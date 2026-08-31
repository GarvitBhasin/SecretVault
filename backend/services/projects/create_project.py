from sqlalchemy.orm import Session

from backend.database import Action, Asset, Projects
from backend.helpers import add_log, now


def create_project(name: str, user_id: int, session: Session):
    # Create project object and add to db
    current_time = now()
    project = Projects(
        name=name, creator_id=user_id, created_at=current_time, updated_at=current_time
    )

    session.add(project)
    session.flush()

    add_log(session, user_id, Action.CREATE, Asset.PROJECT, project.id)
