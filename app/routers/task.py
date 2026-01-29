"""
Роутер для работы с задачами на предсказания.
"""

import logging
from typing import List
from uuid import UUID

from database.database import get_session
from dto import TaskCreateRequest, TaskResponse
from fastapi import APIRouter, HTTPException, status, Depends
from models import User
from services.auth.auth import get_current_user
from services.crud.task import get_tasks_by_user_id, get_task_by_id
from services.task_service import create_task_with_balance_deduction, TASK_CREATION_COST

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
    session=Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> TaskResponse:
    """
    Создать задачу на предсказание. Требуется JWT. user_id берётся из токена.

    Args:
        data: Данные для создания задачи
        session: Сессия базы данных
        current_user: Текущий пользователь (из JWT)

    Returns:
        TaskResponse: Созданная задача

    Raises:
        HTTPException: Если недостаточно средств на балансе или произошла ошибка
    """
    try:
        task = create_task_with_balance_deduction(
            user_id=current_user.id,
            session=session,
            document_id=data.document_id,
            task_cost=TASK_CREATION_COST
        )

        if task is None:
            logger.warning(f"Failed to create task for user {current_user.id}: insufficient balance")
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Недостаточно средств на балансе для создания задачи"
            )

        logger.info(f"Task created: {task.id} for user {current_user.id}")
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
    "/tasks/{task_id}",
    response_model=TaskResponse,
    summary="Получить задачу по ID",
    description="Возвращает задачу по её идентификатору"
)
async def get_task(
    task_id: UUID,
    session=Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> TaskResponse:
    """
    Получить задачу по ID. Требуется JWT. Доступ только к своим задачам.

    Args:
        task_id: ID задачи
        session: Сессия базы данных
        current_user: Текущий пользователь (из JWT)

    Returns:
        TaskResponse: Задача

    Raises:
        HTTPException: 404 если задача не найдена или не принадлежит пользователю
    """
    task = get_task_by_id(task_id, session)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена"
        )
    if task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена"
        )
    return TaskResponse(
        id=task.id,
        user_id=task.user_id,
        document_id=task.document_id,
        status=task.status.value,
        error_message=task.error_message,
        created_at=task.created_at.isoformat(),
        updated_at=task.updated_at.isoformat()
    )


@task_route.get(
    "/tasks",
    response_model=List[TaskResponse],
    summary="Получить историю задач",
    description="Возвращает список всех задач пользователя (история запросов на предсказания)"
)
async def get_tasks_history(
    session=Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> List[TaskResponse]:
    """
    Получить историю задач текущего пользователя. Требуется JWT.

    Args:
        session: Сессия базы данных
        current_user: Текущий пользователь (из JWT)

    Returns:
        List[TaskResponse]: Список задач пользователя
    """
    try:
        tasks = get_tasks_by_user_id(current_user.id, session)
        logger.info(f"Retrieved {len(tasks)} tasks for user {current_user.id}")

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
