from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.database import Action, Asset, Role, Users
from backend.helpers import add_log, raise_error
from backend.security import verify_password


def delete_self(password: str, user: Users, session: Session) -> None:

    # Check password
    verify_password(password, user.password_hash)

    # Count owners
    owner_count = session.execute(
        select(func.count(Users.id))
        .select_from(Users)
        .where(Users.role == Role.OWNER.name)
    ).scalar_one()

    # Forbid user from deleting if user is owner and only one owner exists
    if user.role == Role.OWNER.name and owner_count == 1:
        raise_error(403, "Organization must have atleast 1 owner.")

    # Delete user and add log
    session.delete(user)

    add_log(session, user.id, Action.DELETE, Asset.ACCOUNT, user.id)
