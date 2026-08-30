from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.database import Users
from backend.security import verify_password, encode_token
from backend.helpers import raise_error, add_log

def login_user(
    email: str,
    password: str,
    session: Session
):
    # Find user in db
    result = session.execute(
        select(Users.id, Users.password_hash)
        .where(Users.email == email)
    ).first()

    if result is None:
        raise_error(401, "Incorrect email or password.")

    user_id, stored_hash = result

    # Check if password matches
    verify_password(password, stored_hash)

    # Return token and message
    token = encode_token({"sub": str(user_id)})

    return token