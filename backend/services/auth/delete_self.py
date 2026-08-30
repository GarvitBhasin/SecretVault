from sqlalchemy import select, delete, func
from sqlalchemy.orm import Session
from backend.database import Users, Role, Action, Asset
from backend.security import verify_user, verify_password
from backend.helpers import raise_error, add_log

def delete_self(
    password: str,
    user_id: int,
    session: Session
):  
    # Retrieve user's role and hash
    role, stored_hash = session.execute(
        select(Users.role, Users.password_hash)
        .where(Users.id == user_id)
    ).first()

    # Check password
    verify_password(password, stored_hash)

    # Count owners
    owner_count = session.execute(
        select(func.count(Users.id))
        .select_from(Users)
        .where(Users.role == Role.OWNER.name.lower())
    ).scalar_one()

    # Forbid user from deleting if user is owner and only one owner exists
    if role == Role.OWNER.name and owner_count == 1:
        raise_error(403, "Organization must have atleast 1 owner.")

    # Delete user and add log
    result = session.execute(
        delete(Users)
        .where(Users.id == user_id)
    )

    add_log(session, user_id, Action.DELETE, Asset.ACCOUNT, user_id)