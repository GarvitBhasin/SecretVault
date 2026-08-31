from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import Action, Asset, Role, Users
from backend.helpers import add_log, raise_error
from backend.security import check_input, hash_password


def create_user(
    username: str,
    email: str,
    password: str,
    confirm: str,
    role: int,
    user: Users,
    session: Session,
):

    # Check if username/email are alredy in use
    email_exists = session.scalar(select(Users).where(Users.email == email))
    username_exists = session.scalar(select(Users).where(Users.username == username))

    if email_exists:
        raise_error(409, "Email is already in use.")

    if username_exists:
        raise_error(409, "Username is already taken.")

    # Check email validity, password pairs, role validity and password strenght
    check_input(password, email, confirm, role)

    # Forbid admins from creating owner account
    if Role(role) == Role.OWNER and user.role == Role.ADMIN.name:
        raise_error(403, "Admins cannot create owner accounts.")

    # Create user object and add to db
    new_user = Users(
        username=username,
        email=email,
        password_hash=hash_password(password),
        role=Role(role).name,
    )

    session.add(new_user)
    session.flush()

    add_log(session, user.id, Action.CREATE, Asset.ACCOUNT, new_user.id)
