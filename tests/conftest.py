import pytest

from backend.database import SessionLocal, Users


@pytest.fixture()
def db_session():
    try:
        session = SessionLocal()

        yield session

    finally:
        session.close()


@pytest.fixture()
def viewer(db_session):
    user = Users(
        username="viewer",
        email="viewer@org.com",
        password_hash="abcd1234",
        role="viewer",
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


@pytest.fixture()
def admin(db_session):
    user = Users(
        username="admin",
        email="admin@org.com",
        password_hash="abcd1234",
        role="admin",
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


@pytest.fixture()
def owner(db_session):
    user = Users(
        username="owner",
        email="owner@org.com",
        password_hash="abcd1234",
        role="owner",
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user
