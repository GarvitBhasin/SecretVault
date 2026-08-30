from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.database import Users, Role, Action, Asset
from backend.security import check_credentials, hash_password
from backend.helpers import raise_error, add_log

def initialize_vault(
    username: str,
    email: str,
    password: str,
    confirm: str,
    session: Session
):
    # Check if users exist
    users_exist = session.execute(
        select(Users)
    ).first()

    if users_exist:
        raise_error(403, "SecretVault has already been initialized.")

    # Check email validity, password pairs, and password strength
    check_credentials(email, password, confirm)

    # Hash password
    hashed_pass = hash_password(password)

    # Add first user to db and create log
    user = Users(
        username = username,
        email = email,
        password_hash = hashed_pass,
        role = Role.OWNER.name # First user is made owner 
    )

    session.add(user)
    session.flush()

    # Add log
    add_log(session, user.id, Action.CREATE, Asset.ACCOUNT, user.id)