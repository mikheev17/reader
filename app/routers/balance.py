"""
Роутер для работы с балансом пользователя.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from database.database import get_session
from models import Balance
from services.crud.balance import get_balance_by_user_id, replenish_balance
from dto import BalanceReplenishRequest, BalanceResponse
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

balance_route = APIRouter()


@balance_route.get(
    "/balance",
    response_model=BalanceResponse,
    summary="Получить баланс пользователя",
    description="Возвращает текущий баланс пользователя"
)
async def get_balance(
    user_id: UUID = Query(..., description="ID пользователя"),
    session=Depends(get_session)
) -> BalanceResponse:
    """
    Получить баланс пользователя.

    Args:
        user_id: ID пользователя
        session: Сессия базы данных

    Returns:
        BalanceResponse: Баланс пользователя

    Raises:
        HTTPException: Если баланс не найден
    """
    try:
        balance = get_balance_by_user_id(user_id, session)

        if balance is None:
            logger.warning(f"Balance not found for user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Баланс не найден для данного пользователя"
            )

        logger.info(f"Retrieved balance for user {user_id}: {balance.balance}")
        return BalanceResponse(
            id=balance.id,
            user_id=balance.user_id,
            balance=balance.balance,
            created_at=balance.created_at.isoformat(),
            updated_at=balance.updated_at.isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving balance: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении баланса"
        )


@balance_route.post(
    "/balance/replenish",
    response_model=BalanceResponse,
    summary="Пополнить баланс",
    description="Пополняет баланс пользователя на указанную сумму"
)
async def replenish_balance_endpoint(
    data: BalanceReplenishRequest,
    session=Depends(get_session)
) -> BalanceResponse:
    """
    Пополнить баланс пользователя.

    Args:
        data: Данные для пополнения баланса
        session: Сессия базы данных

    Returns:
        BalanceResponse: Обновленный баланс

    Raises:
        HTTPException: Если баланс не найден или произошла ошибка
    """
    try:
        success = replenish_balance(data.user_id, data.amount, session)

        if not success:
            logger.warning(f"Failed to replenish balance for user {data.user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Баланс не найден для данного пользователя"
            )

        # Получаем обновленный баланс
        balance = get_balance_by_user_id(data.user_id, session)
        if balance is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при получении обновленного баланса"
            )

        logger.info(f"Balance replenished for user {data.user_id}: +{data.amount}, new balance: {balance.balance}")
        return BalanceResponse(
            id=balance.id,
            user_id=balance.user_id,
            balance=balance.balance,
            created_at=balance.created_at.isoformat(),
            updated_at=balance.updated_at.isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error replenishing balance: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при пополнении баланса"
        )
