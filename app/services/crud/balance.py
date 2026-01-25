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


def withdraw_balance(user_id: UUID, amount, session: Session) -> bool:
    """
    Списать средства с баланса пользователя.
    
    Args:
        user_id: ID пользователя
        amount: Сумма для списания
        session: Сессия базы данных
        
    Returns:
        bool: True если списание успешно, False если недостаточно средств
    """
    from decimal import Decimal
    
    try:
        balance = get_balance_by_user_id(user_id, session)
        if not balance:
            return False
        
        if balance.withdraw(Decimal(str(amount))):
            session.add(balance)
            session.commit()
            return True
        return False
    except Exception:
        session.rollback()
        raise


def replenish_balance(user_id: UUID, amount, session: Session) -> bool:
    """
    Пополнить баланс пользователя.
    
    Args:
        user_id: ID пользователя
        amount: Сумма для пополнения
        session: Сессия базы данных
        
    Returns:
        bool: True если пополнение успешно
    """
    from decimal import Decimal
    
    try:
        balance = get_balance_by_user_id(user_id, session)
        if not balance:
            return False
        
        if balance.replenish(Decimal(str(amount))):
            session.add(balance)
            session.commit()
            return True
        return False
    except Exception:
        session.rollback()
        raise