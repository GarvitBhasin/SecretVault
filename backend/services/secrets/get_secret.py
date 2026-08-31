from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import Action, Asset, Secrets, Users
from backend.helpers import add_log, raise_error
from backend.security import decrypt


def get_secret(id: int, user_id: int, session: Session):
    # Find secret
    result = session.execute(
        select(Secrets, Users.username)
        .where(Secrets.id == id)
        .outerjoin(Users, Users.id == Secrets.creator_id)
    ).first()

    if result is None:
        raise_error(404, "Secret not found.")

    secret, username = result

    add_log(session, user_id, Action.READ, Asset.SECRET, id)

    return (
        f"Name: {secret.name}\nValue: {decrypt(secret.value)}\nDescription: {secret.description}\nCreator: {username if username else 'Deleted user'}\nCreated At: {secret.created_at}\nLast Updated: {secret.updated_at}",
    )
