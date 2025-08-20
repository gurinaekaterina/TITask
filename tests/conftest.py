import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import get_db as app_get_db, pwd_context
from app.db.database import Base
from app.db.models import User
from app.main import app


@pytest.fixture(scope="session")
def uploads_dir():
    return os.path.abspath("./uploads")


@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def db_session(test_engine):
    session_local = sessionmaker(
        bind=test_engine, autoflush=False, autocommit=False, future=True
    )
    session = session_local()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    def _get_db_override():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[app_get_db] = _get_db_override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def create_user(db_session):
    def _create(email: str, password: str) -> User:
        user = User(email=email, password_hash=pwd_context.hash(password))
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    return _create
