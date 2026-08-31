from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import Action, Asset, Role, Users
from backend.helpers import add_log, raise_error


def delete_user(id: int, user: Users, session: Session):
    # Retrieve user to be deleted
    deleting_user = session.execute(
        select(Users).where(Users.id == id)
    ).scalar_one_or_none()

    # Perform security checks
    if deleting_user is None:
        raise_error(404, "User not found.")

    if deleting_user.id == user.id:
        raise_error(403, "Cannot delete your own account through this method.")

    if deleting_user.role == Role.OWNER.name:
        raise_error(403, "Cannot delete owner account.")

    # delete user and add log
    session.delete(user)

    add_log(session, user.id, Action.DELETE, Asset.ACCOUNT, deleting_user.id)
