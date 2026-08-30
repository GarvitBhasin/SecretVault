from sqlalchemy import update
from sqlalchemy.orm import Session
from backend.database import Users, Action, Asset
from backend.security import password_strong, hash_password
from backend.helpers import raise_error, add_log

def reset_password(
    password: str,
    confirm: str,
    user_id: int,
    session: Session
):
    # Check credentials  
    if password != confirm:
        raise_error(400, "Passwords do not match.")

    if not password_strong(password):
        raise_error(422, "Password must have at least one character, digit, symbol and must be more than 8 characters long.")

    # Update password
    session.execute(
        update(Users)
        .where(Users.id == user_id)
        .values(password_hash=hash_password(password))
    )

    add_log(session, user_id, Action.UPDATE, Asset.ACCOUNT, user_id)