"""
Роутер для работы с задачами на предсказания.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from database.database import get_session
from services.task_service import create_task_with_balance_deduction, TASK_CREATION_COST
from services.crud.task import get_tasks_by_user_id
from dto import TaskCreateRequest, TaskResponse
from typing import List
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

task_route = APIRouter()


@task_route.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать задачу на предсказание",
    description="Создает задачу на предсказание с автоматическим списанием баланса"
)
async def create_task(
    data: TaskCreateRequest,
    session=Depends(get_session)
) -> TaskResponse:
    """
    Создать задачу на предсказание.

    Args:
        data: Данные для создания задачи
        session: Сессия базы данных

    Returns:
        TaskResponse: Созданная задача

    Raises:
        HTTPException: Если недостаточно средств на балансе или произошла ошибка
    """
    try:
        task = create_task_with_balance_deduction(
            user_id=data.user_id,
            session=session,
            document_id=data.document_id,
            task_cost=TASK_CREATION_COST
        )

        if task is None:
            logger.warning(f"Failed to create task for user {data.user_id}: insufficient balance")
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Недостаточно средств на балансе для создания задачи"
            )

        logger.info(f"Task created: {task.id} for user {data.user_id}")
        return TaskResponse(
            id=task.id,
            user_id=task.user_id,
            document_id=task.document_id,
            status=task.status.value,
            error_message=task.error_message,
            created_at=task.created_at.isoformat(),
            updated_at=task.updated_at.isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при создании задачи"
        )


@task_route.get(
    "/tasks",
    response_model=List[TaskResponse],
    summary="Получить историю задач",
    description="Возвращает список всех задач пользователя (история запросов на предсказания)"
)
async def get_tasks_history(
    user_id: UUID = Query(..., description="ID пользователя"),
    session=Depends(get_session)
) -> List[TaskResponse]:
    """
    Получить историю задач пользователя.

    Args:
        user_id: ID пользователя
        session: Сессия базы данных

    Returns:
        List[TaskResponse]: Список задач пользователя
    """
    try:
        tasks = get_tasks_by_user_id(user_id, session)
        logger.info(f"Retrieved {len(tasks)} tasks for user {user_id}")

        return [
            TaskResponse(
                id=task.id,
                user_id=task.user_id,
                document_id=task.document_id,
                status=task.status.value,
                error_message=task.error_message,
                created_at=task.created_at.isoformat(),
                updated_at=task.updated_at.isoformat()
            )
            for task in tasks
        ]

    except Exception as e:
        logger.error(f"Error retrieving tasks: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении истории задач"
        )
