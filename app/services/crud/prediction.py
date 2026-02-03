from typing import List, Optional, Tuple
from uuid import UUID

from sqlmodel import Session, select

from models import Prediction, Task, TextDocument


def get_predictions_for_user(
    user_id: UUID, session: Session
) -> List[Tuple[Prediction, Task, Optional[TextDocument]]]:
    """Возвращает предсказания пользователя с задачей и документом, по убыванию даты."""
    statement = (
        select(Prediction, Task, TextDocument)
        .join(Task, Prediction.task_id == Task.id)
        .outerjoin(TextDocument, Task.document_id == TextDocument.id)
        .where(Task.user_id == user_id)
        .order_by(Prediction.created_at.desc())
    )
    return list(session.exec(statement).all())


def get_all_predictions(session: Session) -> List[Prediction]:
    statement = select(Prediction)
    return session.exec(statement).all()


def get_prediction_by_id(prediction_id: UUID, session: Session) -> Optional[Prediction]:
    return session.get(Prediction, prediction_id)


def get_predictions_by_task_id(task_id: UUID, session: Session) -> List[Prediction]:
    statement = select(Prediction).where(Prediction.task_id == task_id)
    return session.exec(statement).all()


def create_prediction(prediction: Prediction, session: Session) -> Prediction:
    try:
        session.add(prediction)
        session.commit()
        session.refresh(prediction)
        return prediction
    except Exception:
        session.rollback()
        raise


def delete_prediction(prediction_id: UUID, session: Session) -> bool:
    try:
        pred = session.get(Prediction, prediction_id)
        if pred:
            session.delete(pred)
            session.commit()
            return True
        return False
    except Exception:
        session.rollback()
        raise
