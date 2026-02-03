"""
Сервис для операций с балансом с одновременным созданием транзакций.
Пополнение и снятие всегда создают запись Transaction.
"""

from decimal import Decimal
from typing import Optional
from uuid import UUID

from models import Balance, Transaction, TransactionType
from services.crud.balance import get_balance_by_user_id
from sqlmodel import Session


def replenish(
    user_id: UUID,
    amount: Decimal,
    session: Session,
    *,
    commit: bool = True,
) -> Optional[Balance]:
    """
    Пополнить баланс пользователя и создать транзакцию типа REPLENISHMENT.

    Args:
        user_id: ID пользователя
        amount: Сумма пополнения
        session: Сессия БД
        commit: Если True — выполнить commit в конце (для вызова из API).
                Если False — только добавить в session (для атомарности с другими операциями).

    Returns:
        Обновлённый Balance или None, если баланс не найден или сумма <= 0.
    """
    if amount <= 0:
        return None

    balance = get_balance_by_user_id(user_id, session)
    if not balance:
        return None

    balance.replenish(amount)
    session.add(balance)

    transaction = Transaction(
        user_id=user_id,
        transaction_type=TransactionType.REPLENISHMENT,
        amount=amount,
        task_id=None,
    )
    session.add(transaction)

    if commit:
        session.commit()
        session.refresh(balance)
    return balance


def withdraw(
    user_id: UUID,
    amount: Decimal,
    session: Session,
    *,
    task_id: Optional[UUID] = None,
    commit: bool = True,
) -> Optional[Balance]:
    """
    Снять средства с баланса пользователя и создать транзакцию типа WITHDRAWAL.

    Args:
        user_id: ID пользователя
        amount: Сумма списания
        session: Сессия БД
        task_id: ID задачи (опционально, для привязки списания к задаче)
        commit: Если True — выполнить commit. Если False — только добавить в session.

    Returns:
        Обновлённый Balance или None при недостатке средств / отсутствии баланса / сумма <= 0.
    """
    if amount <= 0:
        return None

    balance = get_balance_by_user_id(user_id, session)
    if not balance or not balance.has_sufficient_balance(amount):
        return None

    balance.withdraw(amount)
    session.add(balance)

    transaction = Transaction(
        user_id=user_id,
        transaction_type=TransactionType.WITHDRAWAL,
        amount=amount,
        task_id=task_id,
    )
    session.add(transaction)

    if commit:
        session.commit()
        session.refresh(balance)
    return balance
