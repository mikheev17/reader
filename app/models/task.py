"""
Модели ML сервиса и задач.
"""

from enum import Enum
from typing import Optional, Any
from sqlmodel import Field, Column, JSON
from uuid import UUID
from .base import BaseSQLModel, Validatable
from .validation import ValidationResult, ValidationError


class TaskStatus(str, Enum):
    """
    Статусы выполнения задачи ML модели.
    """
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Task(BaseSQLModel, Validatable, table=True):
    """
    Класс задачи для ML модели (SQLModel).
    """
    __tablename__ = "tasks"
    
    user_id: UUID = Field(foreign_key="users.id", index=True)
    document_id: Optional[UUID] = Field(default=None, foreign_key="text_documents.id")
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    error_message: Optional[str] = None
    
    def set_status(self, status: TaskStatus) -> None:
        """
        Установить статус задачи.
        
        Args:
            status: Новый статус
        """
        self.status = status
        self._update_timestamp()

    def set_error(self, error_message: str) -> None:
        """
        Установить ошибку выполнения задачи.
        
        Args:
            error_message: Сообщение об ошибке
        """
        self.error_message = error_message
        self.status = TaskStatus.FAILED
        self._update_timestamp()
    
    def is_completed(self) -> bool:
        """
        Проверить, завершена ли задача.
        
        Returns:
            bool: True если задача завершена
        """
        return self.status == TaskStatus.COMPLETED
    
    def is_failed(self) -> bool:
        """
        Проверить, завершилась ли задача с ошибкой.
        
        Returns:
            bool: True если задача завершилась с ошибкой
        """
        return self.status == TaskStatus.FAILED
    
    def validate(self) -> ValidationResult:
        """
        Валидировать задачу.
        
        Returns:
            ValidationResult: Результат валидации
        """
        errors = []
        
        if not self.user_id:
            errors.append(ValidationError("user_id", "ID пользователя не может быть пустым"))
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)
    
    def to_dict(self) -> dict:
        """
        Преобразовать задачу в словарь.
        
        Returns:
            dict: Словарь с данными задачи
        """
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'document_id': str(self.document_id) if self.document_id else None,
            'status': self.status.value if isinstance(self.status, Enum) else self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Prediction(BaseSQLModel, Validatable, table=True):
    """
    Класс предсказания/результата работы ML модели (SQLModel).
    """
    __tablename__ = "predictions"
    
    task_id: UUID = Field(foreign_key="tasks.id", index=True)
    prediction_data: Optional[Any] = Field(default=None, sa_column=Column(JSON))

    def validate(self) -> ValidationResult:
        """
        Валидировать предсказание.
        Реализация абстрактного метода из Validatable.
        
        Returns:
            ValidationResult: Результат валидации
        """
        errors = []
        
        if not self.task_id:
            errors.append(ValidationError("task_id", "ID задачи не может быть пустым"))
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)
    
    def to_dict(self) -> dict:
        """
        Преобразовать предсказание в словарь.
        
        Returns:
            dict: Словарь с данными предсказания
        """
        return {
            'id': str(self.id),
            'task_id': str(self.task_id),
            'has_prediction_data': self.prediction_data is not None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
