import os

# CI pipeline doesn't have access to env variables
# This temporarily changes db connection from production
# postgreSQL to SQLite for testing
TEST_DATABASE_URL = "sqlite:///:memory:"
os.environ["DB_URL"] = TEST_DATABASE_URL

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database import Base, Users


engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(bind=engine)


@pytest.fixture()
def db_session():
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def viewer(db_session):
    user = Users(
        username="viewer",
        email="viewer@org.com",
        password_hash="hashed_password",
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
        password_hash="hashed_password",
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
        password_hash="hashed_password",
        role="owner",
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user