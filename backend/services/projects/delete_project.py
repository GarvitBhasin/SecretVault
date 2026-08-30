from sqlalchemy import delete
from sqlalchemy.orm import Session
from backend.database import Projects, Action, Asset
from backend.helpers import raise_error, add_log

def delete_project(
    id: int,
    user_id: int,
    session: Session
):  
    # Delete project and add log
    project = session.execute(
        delete(Projects)
        .where(Projects.id == id)
    )

    if project.rowcount == 0:
        raise_error(404, "Project not found.")

    add_log(session, user_id, Action.DELETE, Asset.PROJECT, id)