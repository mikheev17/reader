from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select

from models import TextDocument


def get_all_documents(session: Session) -> List[TextDocument]:
    statement = select(TextDocument)
    return session.exec(statement).all()


def get_document_by_id(document_id: UUID, session: Session) -> Optional[TextDocument]:
    return session.get(TextDocument, document_id)


def get_documents_by_user_id(user_id: UUID, session: Session) -> List[TextDocument]:
    statement = select(TextDocument).where(TextDocument.user_id == user_id)
    return session.exec(statement).all()


def create_document(document: TextDocument, session: Session) -> TextDocument:
    try:
        session.add(document)
        session.commit()
        session.refresh(document)
        return document
    except Exception:
        session.rollback()
        raise


def delete_document(document_id: UUID, session: Session) -> bool:
    """
    Жесткое удаление документа (старая функция для обратной совместимости).
    """
    try:
        doc = session.get(TextDocument, document_id)
        if doc:
            session.delete(doc)
            session.commit()
            return True
        return False
    except Exception:
        session.rollback()
        raise


def soft_delete_document(document_id: UUID, session: Session) -> bool:
    """
    Мягкое удаление документа с обработкой связанных сущностей.
    Помечает документ как удаленный и связанные задачи как failed.
    
    Args:
        document_id: ID документа для удаления
        session: Сессия базы данных
        
    Returns:
        bool: True если удаление успешно
    """
    from models.task import Task, TaskStatus
    
    try:
        doc = session.get(TextDocument, document_id)
        if not doc or doc.is_deleted():
            return False
        
        # Помечаем документ как удаленный
        doc.soft_delete()
        session.add(doc)
        
        # Помечаем связанные задачи как failed
        from services.crud.task import get_tasks_by_document_id
        related_tasks = get_tasks_by_document_id(document_id, session)
        for task in related_tasks:
            if task.status != TaskStatus.COMPLETED:
                task.set_status(TaskStatus.FAILED)
                task.set_error("Документ был удален")
                session.add(task)
        
        session.commit()
        return True
    except Exception:
        session.rollback()
        raise


def get_active_documents_by_user_id(user_id: UUID, session: Session) -> List[TextDocument]:
    """
    Получить все активные (не удаленные) документы пользователя.
    
    Args:
        user_id: ID пользователя
        session: Сессия базы данных
        
    Returns:
        List[TextDocument]: Список активных документов
    """
    statement = select(TextDocument).where(
        TextDocument.user_id == user_id,
        TextDocument.deleted_at.is_(None)
    )
    return session.exec(statement).all()
