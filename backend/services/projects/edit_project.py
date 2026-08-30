from sqlalchemy import update
from sqlalchemy.orm import Session
from backend.database import Projects, Action, Asset
from backend.helpers import now, raise_error, add_log

def edit_project(
    name: str,
    id: int,
    user_id: int,
    session: Session
):  
    # Edit project and add log
    result = session.execute(
        update(Projects)
        .where(Projects.id == id)
        .values(
            name = name,
            updated_at = now()
        )
    )

    if result.rowcount == 0:
        raise_error(404, "Project not found.")

    add_log(session, user_id, Action.UPDATE, Asset.PROJECT, id)