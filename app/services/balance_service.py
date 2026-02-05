"""
Сервис для операций с балансом с одновременным созданием транзакций.
Пополнение и снятие всегда создают запись Transaction.
"""

import logging
from decimal import Decimal
from typing import Optional
from uuid import UUID

from models import Balance, Transaction, TransactionType
from services.crud.balance import get_balance_by_user_id
from sqlmodel import Session

logger = logging.getLogger(__name__)


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
        logger.warning("Replenish skipped: amount <= 0 for user_id=%s", user_id)
        return None

    balance = get_balance_by_user_id(user_id, session)
    if not balance:
        logger.warning("Replenish skipped: balance not found for user_id=%s", user_id)
        return None

    balance.replenish(amount)
    logger.info("Balance replenished: user_id=%s, amount=%s, new_balance=%s", user_id, amount, balance.balance)
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
        logger.warning("Withdraw skipped: amount <= 0 for user_id=%s", user_id)
        return None

    balance = get_balance_by_user_id(user_id, session)
    if not balance or not balance.has_sufficient_balance(amount):
        logger.warning("Withdraw skipped: insufficient balance or not found for user_id=%s, amount=%s", user_id, amount)
        return None

    balance.withdraw(amount)
    logger.info("Balance withdrawn: user_id=%s, amount=%s, task_id=%s, new_balance=%s", user_id, amount, task_id, balance.balance)
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
