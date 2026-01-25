from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select

from models import Task


def get_all_tasks(session: Session) -> List[Task]:
    statement = select(Task)
    return session.exec(statement).all()


def get_task_by_id(task_id: UUID, session: Session) -> Optional[Task]:
    return session.get(Task, task_id)


def get_tasks_by_user_id(user_id: UUID, session: Session) -> List[Task]:
    statement = select(Task).where(Task.user_id == user_id)
    return session.exec(statement).all()


def get_tasks_by_document_id(document_id: UUID, session: Session) -> List[Task]:
    statement = select(Task).where(Task.document_id == document_id)
    return session.exec(statement).all()


def create_task(task: Task, session: Session) -> Task:
    try:
        session.add(task)
        session.commit()
        session.refresh(task)
        return task
    except Exception:
        session.rollback()
        raise


def delete_task(task_id: UUID, session: Session) -> bool:
    try:
        task = session.get(Task, task_id)
        if task:
            session.delete(task)
            session.commit()
            return True
        return False
    except Exception:
        session.rollback()
        raise

def update_task_status(task_id: UUID, status, session: Session, error_message: Optional[str] = None) -> Optional[Task]:
    """
    Обновить статус задачи.
    
    Args:
        task_id: ID задачи
        status: Новый статус
        error_message: Сообщение об ошибке (если статус FAILED)
        session: Сессия базы данных
        
    Returns:
        Optional[Task]: Обновленная задача или None если не найдена
    """
    from models.task import TaskStatus
    
    try:
        task = session.get(Task, task_id)
        if not task:
            return None
        
        task.set_status(status)
        if error_message and status == TaskStatus.FAILED:
            task.set_error(error_message)
        
        session.add(task)
        session.commit()
        session.refresh(task)
        return task
    except Exception:
        session.rollback()
        raise


def complete_task_with_prediction(task_id: UUID, prediction_data: dict, session: Session):
    """
    Завершить задачу и создать предсказание.
    
    Args:
        task_id: ID задачи
        prediction_data: Данные предсказания
        session: Сессия базы данных
        
    Returns:
        Optional[Prediction]: Созданное предсказание или None если задача не найдена
    """
    from models.task import TaskStatus, Prediction
    from services.crud.prediction import create_prediction
    from services.crud.document import get_document_by_id
    
    try:
        task = session.get(Task, task_id)
        if not task:
            return None
        
        # Обновляем статус задачи
        task.set_status(TaskStatus.COMPLETED)
        session.add(task)
        
        # Создаем предсказание
        prediction = Prediction(
            task_id=task_id,
            prediction_data=prediction_data
        )
        prediction = create_prediction(prediction, session)
        
        # Помечаем документ как обработанный, если он есть
        if task.document_id:
            doc = get_document_by_id(task.document_id, session)
            if doc:
                doc.mark_as_processed()
                session.add(doc)
        
        session.commit()
        session.refresh(prediction)
        return prediction
    except Exception:
        session.rollback()
        raise
