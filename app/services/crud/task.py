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
