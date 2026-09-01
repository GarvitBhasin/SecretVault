from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.database import Projects, Secrets, Users
from backend.helpers import raise_error


def list_projects(session: Session) -> list[dict[str, str]]:
    # Join project id, project name, and project creator's username
    projects = session.execute(
        select(Projects, Users.username)
        .join(Users, Projects.creator_id == Users.id)
        .order_by(Projects.id.asc())
    ).all()

    if not projects:
        raise_error(404, "No projects found.")

    # Calculate sum of secrets for each project
    secrets_sum = session.execute(
        select(func.count(Secrets.project_id))
        .select_from(Projects)
        .outerjoin(Secrets, Projects.id == Secrets.project_id)
        .group_by(Projects.id)
        .order_by(Projects.id.asc())
    ).all()

    project_list = []

    # Create array of project dicts (used to display table on cli)
    for index, project in enumerate(projects):
        project_list.append(
            {
                "id": str(project.id),
                "name": project.name,
                "creator": project.username,
                "secrets": str(secrets_sum[index][0]),
                "created_at": str(project.created_at.replace(microsecond=0)),
                "updated_at": str(project.updated_at.replace(microsecond=0)),
            }
        )

    return project_list
