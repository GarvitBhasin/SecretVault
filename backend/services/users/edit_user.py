from sqlalchemy import select, update
from sqlalchemy.orm import Session

from backend.database import Action, Asset, Role, Users
from backend.helpers import add_log, raise_error


def edit_user(id: int, role: int, user: Users, session: Session):
    # Validate role
    if role not in range(1, 4):
        raise_error(400, "Invalid role.")

    # Retrieve role to be edited
    editing_user = session.execute(
        select(Users.role).where(Users.id == id)
    ).scalar_one_or_none()

    # Check if user not found
    if editing_user is None:
        raise_error(404, "User not found.")

    # Cannot edit your own role
    if user.id == id:
        raise_error(400, "Cannot edit your own account")

    # Admin cannot edit owner account
    if editing_user.role == Role.OWNER.name and user.role == Role.ADMIN.name:
        raise_error(403, "Admins cannot alter owner accounts.")

    # Admin cannot assign owner role
    if user.role == Role.ADMIN and Role(role) == Role.OWNER:
        raise_error(403, "Admins cannot assign owner role.")

    # Edit
    editing_user.role = Role(role).name

    add_log(session, user.id, Action.UPDATE, Asset.ACCOUNT, id)
