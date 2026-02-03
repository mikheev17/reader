"""
Роутер для работы с задачами на предсказания.
"""

import logging
from typing import List
from uuid import UUID

from database.database import get_session
from dto import TaskCreateRequest, TaskResponse, PredictionResponse, PredictionHistoryItem
from fastapi import APIRouter, HTTPException, status, Depends
from models import User
from services.auth.auth import get_current_user, get_current_user_cookie_or_bearer
from services.crud.task import get_tasks_by_user_id, get_task_by_id
from services.crud.prediction import get_predictions_by_task_id, get_predictions_for_user
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
    current_user: User = Depends(get_current_user_cookie_or_bearer),
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
    current_user: User = Depends(get_current_user_cookie_or_bearer),
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


@task_route.get(
    "/predictions",
    response_model=List[PredictionHistoryItem],
    summary="История предсказаний",
    description="Возвращает список предсказаний текущего пользователя",
)
async def get_predictions_history(
    session=Depends(get_session),
    current_user: User = Depends(get_current_user_cookie_or_bearer),
) -> List[PredictionHistoryItem]:
    """Получить историю предсказаний текущего пользователя."""
    try:
        rows = get_predictions_for_user(current_user.id, session)
        result = []
        for pred, task, doc in rows:
            data = pred.prediction_data or {}
            words = data.get("words") or []
            result.append(
                PredictionHistoryItem(
                    task_id=task.id,
                    document_id=task.document_id,
                    document_name=doc.filename if doc else None,
                    created_at=pred.created_at.isoformat(),
                    english_level=data.get("english_level"),
                    words_count=len(words),
                )
            )
        return result
    except Exception as e:
        logger.error(f"Error retrieving predictions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении истории предсказаний"
        )


@task_route.get(
    "/tasks/{task_id}/prediction",
    response_model=PredictionResponse,
    summary="Получить предсказание по задаче",
    description="Возвращает результат обработки (перевод слов) для задачи",
)
async def get_task_prediction(
    task_id: UUID,
    session=Depends(get_session),
    current_user: User = Depends(get_current_user_cookie_or_bearer),
) -> PredictionResponse:
    """
    Получить предсказание по ID задачи. Доступ только к своим задачам.
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
    predictions = get_predictions_by_task_id(task_id, session)
    if not predictions or not predictions[0].prediction_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Результат обработки ещё не готов"
        )
    return PredictionResponse(prediction_data=predictions[0].prediction_data)
