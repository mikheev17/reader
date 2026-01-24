from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select

from models import Balance


def get_all_balances(session: Session) -> List[Balance]:
    statement = select(Balance)
    return session.exec(statement).all()


def get_balance_by_id(balance_id: UUID, session: Session) -> Optional[Balance]:
    return session.get(Balance, balance_id)


def get_balance_by_user_id(user_id: UUID, session: Session) -> Optional[Balance]:
    statement = select(Balance).where(Balance.user_id == user_id)
    return session.exec(statement).first()


def create_balance(balance: Balance, session: Session) -> Balance:
    try:
        session.add(balance)
        session.commit()
        session.refresh(balance)
        return balance
    except Exception:
        session.rollback()
        raise


def delete_balance(balance_id: UUID, session: Session) -> bool:
    try:
        balance = session.get(Balance, balance_id)
        if balance:
            session.delete(balance)
            session.commit()
            return True
        return False
    except Exception:
        session.rollback()
        raise
