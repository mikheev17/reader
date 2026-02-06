from __future__ import annotations

"""
Скрипт для инициализации базы данных стандартными данными.

Запуск (из корня проекта):
    python app/init_standard_data.py

Требования:
- в файле app/.env должны быть корректно заполнены переменные подключения к БД
"""

import logging
from decimal import Decimal

from sqlmodel import Session, select

from database.database import get_database_engine, init_db
from models.user import User, UserRole
from services.user_service import create_user_with_balance

logger = logging.getLogger(__name__)


def init_data():
    """
    Инициализировать базу данных стандартными данными.
    """
    logger.info("Инициализация схемы базы данных...")
    init_db(drop_all=True)
    logger.info("Схема базы данных создана.")

    engine = get_database_engine()

    with Session(engine) as session:
        statement = select(User)
        existing_users = session.exec(statement).first()
        if existing_users:
            logger.info("База данных уже содержит данные. Пропускаем инициализацию.")
            return

        logger.info("Создание стандартных данных...")

        # Создаем пользователей с балансами
        user_data = [
            (
                User(
                    email="admin@example.com",
                    password_hash="admin_hash_12345",
                    username="Администратор",
                    english_level="B2",
                    role=UserRole.ADMIN,
                    is_active=True
                ),
                Decimal('1000.00')
            ),
            (
                User(
                    email="user1@example.com",
                    password_hash="user1_hash_12345",
                    username="Иван Иванов",
                    english_level="A2",
                    role=UserRole.USER,
                    is_active=True
                ),
                Decimal('500.00')
            ),
        ]

        users = []
        for user, initial_balance in user_data:
            created_user, created_balance = create_user_with_balance(user, initial_balance, session)
            users.append(created_user)

        logger.info("Создано %s пользователей с балансами.", len(users))
        logger.info("Инициализация базы данных завершена успешно.")