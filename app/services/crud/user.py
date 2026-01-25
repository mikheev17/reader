from typing import List, Optional
from uuid import UUID
from sqlmodel import Session, select
from models import User


def get_all_users(session: Session) -> List[User]:
    statement = select(User)
    return session.exec(statement).all()


def get_user_by_id(user_id: UUID, session: Session) -> Optional[User]:
    return session.get(User, user_id)


def get_user_by_email(email: str, session: Session) -> Optional[User]:
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def create_user(user: User, session: Session) -> User:
    try:
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    except Exception:
        session.rollback()
        raise


def delete_user(user_id: UUID, session: Session) -> bool:
    try:
        user = session.get(User, user_id)
        if user:
            session.delete(user)
            session.commit()
            return True
        return False
    except Exception:
        session.rollback()
        raise

def update_user(user_id: UUID, user_data: dict, session: Session) -> Optional[User]:
    """
    Обновить данные пользователя.
    
    Args:
        user_id: ID пользователя для обновления
        user_data: Словарь с данными для обновления
        session: Сессия базы данных
        
    Returns:
        Optional[User]: Обновленный пользователь или None если не найден
    """
    try:
        user = session.get(User, user_id)
        if not user:
            return None
        
        # Обновляем только переданные поля
        for key, value in user_data.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        
        user._update_timestamp()
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    except Exception:
        session.rollback()
        raise