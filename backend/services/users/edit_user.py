from sqlalchemy import select, update
from sqlalchemy.orm import Session
from backend.database import Users, Role, Action, Asset
from backend.helpers import raise_error, add_log

def edit_user(
    id: int,
    role: int,
    self_role: Role,
    user_id: int,
    session: Session
):
    # Validate role
    if role not in range(1, 4):
        raise_error(400, "Invalid role.")    

    # Retrieve role to be edited
    editing_role = session.execute(
        select(Users.role)
        .where(Users.id == id)
    ).scalar_one_or_none()

    # Check if user not found
    if editing_role is None:
        raise_error(404, "User not found.")

    # Cannot edit your own role
    if user_id == id:
        raise_error(400, "Cannot edit your own account")

    # Admin cannot edit owner account
    if editing_role == Role.OWNER.name and self_role == Role.ADMIN:
        raise_error(403, "Admins cannot alter owner accounts.")

    # Admin cannot assign owner role
    if self_role == Role.ADMIN and Role(role) == Role.OWNER:
        raise_error(403, "Admins cannot assign owner role.")

    # Edit
    session.execute(
        update(Users)
        .where(Users.id == id)
        .values(role=Role(role).name)
    )

    add_log(session, user_id, Action.UPDATE, Asset.ACCOUNT, id)