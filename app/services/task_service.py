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
from services.crud.balance import get_balance_by_user_id, withdraw_balance
from services.crud.task import create_task
from services.crud.transaction import create_transaction


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
    
    Эта функция объединяет несколько операций:
    - Проверка баланса пользователя
    - Списание фиксированной суммы с баланса
    - Создание задачи на обработку
    - Создание транзакции на списание
    
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
    
    try:
        # Проверяем наличие баланса
        balance = get_balance_by_user_id(user_id, session)
        if not balance:
            return None
        
        # Проверяем и списываем баланс
        if not withdraw_balance(user_id, task_cost, session):
            return None
        
        # Создаем задачу
        task = Task(
            user_id=user_id,
            document_id=document_id,
            status=TaskStatus.PENDING
        )
        task = create_task(task, session)
        
        # Создаем транзакцию на списание и связываем с задачей
        transaction = Transaction(
            user_id=user_id,
            transaction_type=TransactionType.WITHDRAWAL,
            amount=task_cost,
            task_id=task.id
        )
        create_transaction(transaction, session)
        
        return task
    except Exception:
        session.rollback()
        raise
