"""
Фикстуры для тестов. Подключение к БД настраивается в session_fixture (SQLite).
Конфигурация app/database/database и config не изменяется (подмена только в тестах).
"""
# Патчи ДО импорта sqlmodel/api, иначе database.database вызовет create_engine с PostgreSQL
from sqlalchemy.pool import StaticPool
import sqlalchemy.engine as _sa_engine
_orig_create_engine = _sa_engine.create_engine
def _create_engine_for_tests(url, *args, **kwargs):
    if isinstance(url, str) and "sqlite" in url:
        kwargs = {"echo": kwargs.get("echo", False), "connect_args": {"check_same_thread": False}, "poolclass": StaticPool}
    return _orig_create_engine(url, *args, **kwargs)
_sa_engine.create_engine = _create_engine_for_tests

import database.config as _config
class _MockSettings:
    DATABASE_URL_psycopg = "sqlite:///:memory:"
    DEBUG = False
    APP_NAME = None
    APP_DESCRIPTION = None
    API_VERSION = None
    LOG_LEVEL = "INFO"
    JWT_SECRET = "test-secret-for-pytest"
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRE_MINUTES = 60
    COOKIE_NAME = "access_token"
    def validate(self): pass
_mock_settings = _MockSettings()
_orig_get_settings = _config.get_settings
_config.get_settings = lambda: _mock_settings
try:
    _orig_get_settings.cache_clear()
except Exception:
    pass

import database.database as _db
import init_standard_data as _init_data
_db.init_db = lambda drop_all=False: None
_init_data.init_data = lambda: None

from api import app
from database.database import get_session
from services.auth.auth import get_current_user, get_current_user_cookie_or_bearer
from services.user_service import create_user_with_balance
from services.auth.password_service import hash_password
from models import User, UserRole

import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine


@pytest.fixture(name="session")
def session_fixture():
    """Тестовая сессия: SQLite in-memory, свои таблицы. Конфиг app/database не трогаем."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Клиент API с подменой get_session и аутентификации на тестового пользователя."""
    test_user, _ = create_user_with_balance(
        User(
            username="Test User",
            email="test@test.ru",
            password_hash=hash_password("secret"),
            english_level="B1",
        ),
        Decimal("100.00"),
        session,
    )

    async def _get_current_user():
        return test_user

    def _get_session_override():
        yield session

    app.dependency_overrides[get_session] = _get_session_override
    app.dependency_overrides[get_current_user] = _get_current_user
    app.dependency_overrides[get_current_user_cookie_or_bearer] = _get_current_user

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="client_admin")
def client_admin_fixture(session: Session):
    """Клиент API с пользователем-админом (для теста GET /users)."""
    admin_user, _ = create_user_with_balance(
        User(
            username="Admin User",
            email="admin@test.ru",
            password_hash=hash_password("adminsecret"),
            english_level="B1",
            role=UserRole.ADMIN,
        ),
        Decimal("100.00"),
        session,
    )

    async def _get_current_user():
        return admin_user

    def _get_session_override():
        yield session

    app.dependency_overrides[get_session] = _get_session_override
    app.dependency_overrides[get_current_user] = _get_current_user
    app.dependency_overrides[get_current_user_cookie_or_bearer] = _get_current_user

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
