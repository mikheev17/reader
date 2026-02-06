from decimal import Decimal

import pytest
from unittest.mock import patch
from sqlalchemy.pool import StaticPool

import sqlmodel
_real_create_engine = sqlmodel.create_engine


def _mock_create_engine(*args, **kwargs):
    url = args[0] if args else kwargs.get("url", "")
    if url and "postgres" in str(url):
        return _real_create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    return _real_create_engine(*args, **kwargs)


patch.object(sqlmodel, "create_engine", _mock_create_engine).start()

from fastapi.testclient import TestClient
from api import app
from sqlmodel import SQLModel, Session, create_engine
from database.database import get_session
from services.auth.auth import get_current_user, get_current_user_cookie_or_bearer, require_admin
from services.auth.password_service import hash_password
from services.user_service import create_user_with_balance
from models import User, UserRole


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="test_user")
def test_user_fixture(session: Session):
    """Пользователь user@test.ru с балансом 100.00 для тестов API."""
    user = User(
        email="user@test.ru",
        password_hash=hash_password("testpass"),
        username="Test User",
        role=UserRole.USER,
    )
    created_user, _ = create_user_with_balance(user, Decimal("100.00"), session)
    return created_user


@pytest.fixture(name="admin_user")
def admin_user_fixture(session: Session):
    """Пользователь admin@test.ru с ролью ADMIN для тестов /users."""
    user = User(
        email="admin@test.ru",
        password_hash=hash_password("adminpass"),
        username="Admin",
        role=UserRole.ADMIN,
    )
    created_user, _ = create_user_with_balance(user, Decimal("0.00"), session)
    return created_user


@pytest.fixture(name="client")
def client_fixture(session: Session, test_user: User):
    def get_session_override():
        yield session

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_current_user] = lambda: test_user
    app.dependency_overrides[get_current_user_cookie_or_bearer] = lambda: test_user

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="client_admin")
def client_admin_fixture(session: Session, admin_user: User):
    """Клиент с подменённым текущим пользователем — админ (для GET /users)."""
    def get_session_override():
        yield session

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_current_user] = lambda: admin_user
    app.dependency_overrides[get_current_user_cookie_or_bearer] = lambda: admin_user
    app.dependency_overrides[require_admin] = lambda: admin_user

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()