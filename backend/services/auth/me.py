from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import Users


def my_details(user_id: int, session: Session):
    # Find user in db
    username, email, role = session.execute(
        select(Users.username, Users.email, Users.role).where(Users.id == user_id)
    ).first()

    return (
        f"Loaded user details.\nUsername: {username}\nEmail: {email}\nRole: {role.lower()}",
    )
