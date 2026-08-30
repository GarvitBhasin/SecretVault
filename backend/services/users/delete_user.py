from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.database import Users, Role, Action, Asset
from backend.helpers import raise_error, add_log

def delete_user(
    id: int,
    user_id: int,
    session: Session
):
    # Retrieve user to be deleted
    user = session.execute(
        select(Users)
        .where(Users.id == id)
    ).scalar_one_or_none()

    # Perform security checks
    if user is None:
        raise_error(404, "User not found.")

    if user.id == user_id:
        raise_error(403, "Cannot delete your own account through this method.")

    if user.role == Role.OWNER.name:
        raise_error(403, "Cannot delete owner account.")

    # delete user and add log
    session.delete(user)

    add_log(session, user_id, Action.DELETE, Asset.ACCOUNT, user.id)