from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select

from models import Transaction


def get_all_transactions(session: Session) -> List[Transaction]:
    statement = select(Transaction)
    return session.exec(statement).all()


def get_transaction_by_id(transaction_id: UUID, session: Session) -> Optional[Transaction]:
    return session.get(Transaction, transaction_id)


def get_transactions_by_user_id(user_id: UUID, session: Session) -> List[Transaction]:
    statement = select(Transaction).where(Transaction.user_id == user_id)
    return session.exec(statement).all()


def create_transaction(transaction: Transaction, session: Session) -> Transaction:
    try:
        session.add(transaction)
        session.commit()
        session.refresh(transaction)
        return transaction
    except Exception:
        session.rollback()
        raise
