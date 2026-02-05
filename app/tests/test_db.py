"""
Тесты работы с БД напрямую (модели User, создание/удаление).
Подключение настраивается в session_fixture (conftest).
"""
import pytest
from sqlmodel import Session

from models import User
from services.auth.password_service import hash_password
from services.crud.user import create_user
from services.user_service import create_user_with_balance
from decimal import Decimal


def test_create_user(session: Session) -> None:
    """Создание пользователя с валидными данными."""
    user = User(
        email="test@mail.ru",
        password_hash=hash_password("password123"),
        username="Test",
        english_level="B1",
    )
    created = create_user(user, session)
    assert created.id is not None
    assert created.email == "test@mail.ru"


def test_create_user_with_balance(session: Session) -> None:
    """Создание пользователя с балансом через user_service."""
    user = User(
        email="balance_user@mail.ru",
        password_hash=hash_password("pass"),
        username="Balance User",
        english_level="A2",
    )
    created_user, balance = create_user_with_balance(user, Decimal("50.00"), session)
    assert created_user.id is not None
    assert balance.user_id == created_user.id
    assert balance.balance == Decimal("50.00")


def test_fail_create_user_duplicate_email(session: Session) -> None:
    """Создание второго пользователя с тем же email вызывает ошибку (unique)."""
    user = User(
        email="dup@mail.ru",
        password_hash=hash_password("pass"),
        username="First",
        english_level="B1",
    )
    create_user(user, session)

    user2 = User(
        email="dup@mail.ru",
        password_hash=hash_password("other"),
        username="Second",
        english_level="B1",
    )
    with pytest.raises(Exception):
        create_user(user2, session)


def test_delete_user(session: Session) -> None:
    """Удаление пользователя по id."""
    user = User(
        email="todelete@mail.ru",
        password_hash=hash_password("pass"),
        username="ToDelete",
        english_level="B1",
    )
    created = create_user(user, session)
    user_id = created.id

    from services.crud.user import delete_user
    ok = delete_user(user_id, session)
    assert ok is True

    deleted = session.get(User, user_id)
    assert deleted is None
