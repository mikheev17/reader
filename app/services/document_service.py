"""
Сервис для бизнес-логики работы с документами.
Содержит функции, которые используют несколько репозиториев (CRUD).
"""

from typing import Optional
from uuid import UUID

from models.task import Task
from services.crud.document import get_document_by_id
from services.task_service import create_task_with_balance_deduction
from sqlmodel import Session


def send_document_for_processing(document_id: UUID, processing_cost, session: Session) -> Optional[Task]:
    """
    Отправить документ на обработку: списать баланс и создать задачу.
    
    Эта функция объединяет несколько операций:
    - Проверка документа
    - Создание задачи с автоматическим списанием баланса
    
    Args:
        document_id: ID документа для обработки
        processing_cost: Стоимость обработки (Decimal)
        session: Сессия базы данных
        
    Returns:
        Optional[Task]: Созданная задача или None если недостаточно средств или документ невалиден
    """
    try:
        # Получаем документ
        doc = get_document_by_id(document_id, session)
        if not doc or doc.is_deleted() or doc.is_processed:
            return None
        
        # Создаем задачу с автоматическим списанием баланса
        task = create_task_with_balance_deduction(
            user_id=doc.user_id,
            session=session,
            document_id=document_id,
            task_cost=processing_cost
        )
        
        return task
    except Exception:
        session.rollback()
        raise
