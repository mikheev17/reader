"""
Сервис для бизнес-логики работы с документами.
Содержит функции, которые используют несколько репозиториев (CRUD).
"""

import logging
from typing import Optional
from uuid import UUID

from models.task import Task
from services.crud.document import get_document_by_id
from services.task_service import create_task_with_balance_deduction
from sqlmodel import Session

logger = logging.getLogger(__name__)


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
        doc = get_document_by_id(document_id, session)
        if not doc or doc.is_deleted() or doc.is_processed:
            logger.warning("Document not sent for processing: document_id=%s (not found, deleted or already processed)", document_id)
            return None

        task = create_task_with_balance_deduction(
            user_id=doc.user_id,
            session=session,
            document_id=document_id,
            task_cost=processing_cost
        )
        if task:
            logger.info("Document sent for processing: document_id=%s, task_id=%s, user_id=%s", document_id, task.id, doc.user_id)
        else:
            logger.warning("Document processing task not created: insufficient balance for document_id=%s, user_id=%s", document_id, doc.user_id)
        return task
    except Exception:
        logger.exception("Failed to send document for processing: document_id=%s", document_id)
        session.rollback()
        raise
