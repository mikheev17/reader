"""
Базовые абстрактные классы.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from uuid import uuid4, UUID

from sqlmodel import SQLModel, Field


class Validatable(ABC):
    """
    Базовый абстрактный класс для объектов, которые могут быть валидированы.
    """
    
    @abstractmethod
    def validate(self) -> 'ValidationResult':
        """
        Валидировать объект.
        
        Returns:
            ValidationResult: Результат валидации
        """
        pass


class BaseSQLModel(SQLModel):
    """
    Базовая SQLModel для всех сущностей системы.
    Реализует общую функциональность: ID, дата создания, дата обновления.
    """
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    def _update_timestamp(self) -> None:
        """
        Обновить метку времени последнего изменения.
        """
        self.updated_at = datetime.now()
