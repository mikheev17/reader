"""
Роутер для работы с транзакциями пользователя.
"""

import logging

from database.database import get_session
from dto import TransactionResponse
from fastapi import APIRouter, HTTPException, status, Depends
from models import User
from services.auth.auth import get_current_user_cookie_or_bearer
from services.crud.transaction import get_transactions_by_user_id

logger = logging.getLogger(__name__)

transaction_route = APIRouter()


@transaction_route.get(
    "/transactions",
    response_model=list[TransactionResponse],
    summary="Список транзакций пользователя",
    description="Возвращает историю транзакций текущего пользователя (JWT)"
)
async def get_transactions(
    session=Depends(get_session),
    current_user: User = Depends(get_current_user_cookie_or_bearer),
) -> list[TransactionResponse]:
    """
    Получить список транзакций текущего пользователя.
    """
    try:
        transactions = get_transactions_by_user_id(current_user.id, session)
        return [
            TransactionResponse(
                id=t.id,
                user_id=t.user_id,
                transaction_type=t.transaction_type.value if hasattr(t.transaction_type, "value") else t.transaction_type,
                amount=t.amount,
                task_id=t.task_id,
                created_at=t.created_at.isoformat(),
                updated_at=t.updated_at.isoformat(),
            )
            for t in transactions
        ]
    except Exception as e:
        logger.error(f"Error retrieving transactions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении транзакций"
        )
