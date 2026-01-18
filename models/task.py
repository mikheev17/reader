"""
Модели ML сервиса и задач.
"""

from enum import Enum
from typing import Optional, Any
from base import BaseEntity, Validatable
from validation import ValidationResult, ValidationError


class TaskStatus(Enum):
    """
    Статусы выполнения задачи ML модели.
    """
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Task(BaseEntity, Validatable):
    """
    Класс задачи для ML модели.
    """
    
    def __init__(
        self,
        user_id: str,
        document_id: Optional[str] = None
    ):
        """
        Инициализация задачи.
        
        Args:
            user_id: ID пользователя, создавшего задачу
            document_id: ID документа (опционально)
        """
        super().__init__()
        self._user_id: str = user_id
        self._document_id: Optional[str] = document_id
        self._status: TaskStatus = TaskStatus.PENDING
        self._error_message: Optional[str] = None
    
    @property
    def user_id(self) -> str:
        """
        Получить ID пользователя.
        
        Returns:
            str: ID пользователя
        """
        return self._user_id
    
    @property
    def document_id(self) -> Optional[str]:
        """
        Получить ID документа.
        
        Returns:
            Optional[str]: ID документа или None
        """
        return self._document_id
    
    @property
    def status(self) -> TaskStatus:
        """
        Получить статус задачи.
        
        Returns:
            TaskStatus: Статус задачи
        """
        return self._status
    
    def set_status(self, status: TaskStatus) -> None:
        """
        Установить статус задачи.
        
        Args:
            status: Новый статус
        """
        self._status = status
        self._update_timestamp()

    @property
    def error_message(self) -> Optional[str]:
        """
        Получить сообщение об ошибке.
        
        Returns:
            Optional[str]: Сообщение об ошибке или None
        """
        return self._error_message
    
    def set_error(self, error_message: str) -> None:
        """
        Установить ошибку выполнения задачи.
        
        Args:
            error_message: Сообщение об ошибке
        """
        self._error_message = error_message
        self._status = TaskStatus.FAILED
        self._update_timestamp()
    
    def is_completed(self) -> bool:
        """
        Проверить, завершена ли задача.
        
        Returns:
            bool: True если задача завершена
        """
        return self._status == TaskStatus.COMPLETED
    
    def is_failed(self) -> bool:
        """
        Проверить, завершилась ли задача с ошибкой.
        
        Returns:
            bool: True если задача завершилась с ошибкой
        """
        return self._status == TaskStatus.FAILED
    
    def validate(self) -> ValidationResult:
        """
        Валидировать задачу.
        
        Returns:
            ValidationResult: Результат валидации
        """
        errors = []
        
        if not self._user_id:
            errors.append(ValidationError("user_id", "ID пользователя не может быть пустым"))
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)
    
    def to_dict(self) -> dict:
        """
        Преобразовать задачу в словарь.
        
        Returns:
            dict: Словарь с данными задачи
        """
        return {
            'id': self._id,
            'user_id': self._user_id,
            'document_id': self._document_id,
            'status': self._status.value,
            'error_message': self._error_message,
            'created_at': self._created_at.isoformat(),
            'updated_at': self._updated_at.isoformat()
        }

class Prediction(BaseEntity, Validatable):
    """
    Класс предсказания/результата работы ML модели.
    """

    def __init__(
            self,
            task_id: str,
            prediction_data: Any,
    ):
        """
        Инициализация предсказания.

        Args:
            task_id: ID задачи, которая создала предсказание
            prediction_data: Данные предсказания
        """
        super().__init__()
        self._task_id: str = task_id
        self._prediction_data: Any = prediction_data


    @property
    def task_id(self) -> str:
        """
        Получить ID задачи.

        Returns:
            str: ID задачи
        """
        return self._task_id

    @property
    def prediction_data(self) -> Any:
        """
        Получить данные предсказания.

        Returns:
            Any: Данные предсказания
        """
        return self._prediction_data

    def validate(self) -> ValidationResult:
        """
        Валидировать предсказание.
        Реализация абстрактного метода из Validatable.

        Returns:
            ValidationResult: Результат валидации
        """
        errors = []

        if not self._task_id:
            errors.append(ValidationError("task_id", "ID задачи не может быть пустым"))

        return ValidationResult(is_valid=len(errors) == 0, errors=errors)

    def to_dict(self) -> dict:
        """
        Преобразовать предсказание в словарь.

        Returns:
            dict: Словарь с данными предсказания
        """
        return {
            'id': self._id,
            'task_id': self._task_id,
            'has_prediction_data': self._prediction_data is not None,
            'created_at': self._created_at.isoformat(),
            'updated_at': self._updated_at.isoformat()
        }
