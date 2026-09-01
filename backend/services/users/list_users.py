from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import Users
from backend.helpers import raise_error


def list_users(session: Session) -> list[dict[str, str]]:
    users = session.execute(select(Users)).scalars().all()

    if not users:
        raise_error(404, "No users found.")

    users_arr = []

    for user in users:
        users_arr.append(
            {
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "role": user.role,
            }
        )

    return users_arr
