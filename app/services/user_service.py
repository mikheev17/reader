"""
Сервис для бизнес-логики работы с пользователями.
Содержит функции, которые используют несколько репозиториев (CRUD).
"""

from decimal import Decimal
from typing import Tuple

from models.balance import Balance
from models.user import User
from sqlmodel import Session


def create_user_with_balance(user: User, initial_balance: Decimal, session: Session) -> Tuple[User, Balance]:
    """
    Создать пользователя и баланс одновременно в одной транзакции.
    
    Эта функция объединяет несколько операций:
    - Создание пользователя
    - Создание баланса для пользователя
    
    Args:
        user: Объект пользователя для создания
        initial_balance: Начальный баланс
        session: Сессия базы данных
        
    Returns:
        tuple[User, Balance]: Кортеж из созданного пользователя и баланса
    """
    try:
        # Создаем пользователя
        session.add(user)
        session.flush()  # Получаем ID пользователя без коммита
        
        # Создаем баланс
        balance = Balance(user_id=user.id, balance=Decimal(str(initial_balance)))
        session.add(balance)
        
        session.commit()
        session.refresh(user)
        session.refresh(balance)
        return user, balance
    except Exception:
        session.rollback()
        raise
