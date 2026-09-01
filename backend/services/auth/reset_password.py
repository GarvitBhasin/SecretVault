from sqlalchemy.orm import Session

from backend.database import Action, Asset, Users
from backend.helpers import add_log, raise_error
from backend.security import check_input, hash_password


def reset_password(password: str, confirm: str, user: Users, session: Session) -> None:
    # Check credentials
    if password != confirm:
        raise_error(400, "Passwords do not match.")

    # Check password strenght
    check_input(password)

    # Update password
    user.password_hash = hash_password(password)

    add_log(session, user.id, Action.UPDATE, Asset.ACCOUNT, user.id)
