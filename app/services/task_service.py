"""
Сервис для бизнес-логики работы с задачами.
Содержит функции, которые используют несколько репозиториев (CRUD).
"""

from typing import Optional
from uuid import UUID
from decimal import Decimal
from sqlmodel import Session

from models.task import Task, TaskStatus
from models.transaction import Transaction, TransactionType
from services.crud.balance import get_balance_by_user_id


# Фиксированная стоимость создания задачи
TASK_CREATION_COST = Decimal("10.00")


def create_task_with_balance_deduction(
    user_id: UUID,
    session: Session,
    document_id: Optional[UUID] = None,
    task_cost: Optional[Decimal] = None
) -> Optional[Task]:
    """
    Создать задачу с автоматическим списанием фиксированной суммы с баланса.

    Все операции (списание баланса, создание задачи, создание транзакции)
    выполняются в одной транзакции БД — при любой ошибке откатывается всё.
    
    Args:
        user_id: ID пользователя
        document_id: ID документа (опционально)
        task_cost: Стоимость создания задачи (если не указана, используется TASK_CREATION_COST)
        session: Сессия базы данных
        
    Returns:
        Optional[Task]: Созданная задача или None если недостаточно средств
    """
    if task_cost is None:
        task_cost = TASK_CREATION_COST

    balance = get_balance_by_user_id(user_id, session)
    if not balance or not balance.has_sufficient_balance(task_cost):
        return None

    try:
        balance.withdraw(task_cost)
        session.add(balance)

        task = Task(
            user_id=user_id,
            document_id=document_id,
            status=TaskStatus.PENDING
        )
        session.add(task)
        session.flush()

        transaction = Transaction(
            user_id=user_id,
            transaction_type=TransactionType.WITHDRAWAL,
            amount=task_cost,
            task_id=task.id
        )
        session.add(transaction)

        session.commit()
        session.refresh(task)
        return task
    except Exception:
        session.rollback()
        raise
