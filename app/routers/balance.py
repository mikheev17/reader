"""
Роутер для работы с балансом пользователя.
"""

import logging

from database.database import get_session
from dto import BalanceReplenishRequest, BalanceResponse
from fastapi import APIRouter, HTTPException, status, Depends
from models import Balance
from models import User
from services.auth.auth import get_current_user, get_current_user_cookie_or_bearer
from services.crud.balance import get_balance_by_user_id, replenish_balance

logger = logging.getLogger(__name__)

balance_route = APIRouter()


@balance_route.get(
    "/balance",
    response_model=BalanceResponse,
    summary="Получить баланс пользователя",
    description="Возвращает текущий баланс текущего пользователя (JWT)"
)
async def get_balance(
    session=Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> BalanceResponse:
    """
    Получить баланс текущего пользователя. Требуется JWT.

    Args:
        session: Сессия базы данных
        current_user: Текущий пользователь (из JWT)

    Returns:
        BalanceResponse: Баланс пользователя

    Raises:
        HTTPException: Если баланс не найден
    """
    try:
        balance = get_balance_by_user_id(current_user.id, session)

        if balance is None:
            logger.warning(f"Balance not found for user {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Баланс не найден для данного пользователя"
            )

        logger.info(f"Retrieved balance for user {current_user.id}: {balance.balance}")
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
    description="Пополняет баланс текущего пользователя (JWT) на указанную сумму"
)
async def replenish_balance_endpoint(
    data: BalanceReplenishRequest,
    session=Depends(get_session),
    current_user: User = Depends(get_current_user_cookie_or_bearer),
) -> BalanceResponse:
    """
    Пополнить баланс текущего пользователя. Требуется JWT.

    Args:
        data: Данные для пополнения (сумма)
        session: Сессия базы данных
        current_user: Текущий пользователь (из JWT)

    Returns:
        BalanceResponse: Обновленный баланс

    Raises:
        HTTPException: Если баланс не найден или произошла ошибка
    """
    try:
        success = replenish_balance(current_user.id, data.amount, session)

        if not success:
            logger.warning(f"Failed to replenish balance for user {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Баланс не найден для данного пользователя"
            )

        # Получаем обновленный баланс
        balance = get_balance_by_user_id(current_user.id, session)
        if balance is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при получении обновленного баланса"
            )

        logger.info(f"Balance replenished for user {current_user.id}: +{data.amount}, new balance: {balance.balance}")
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
