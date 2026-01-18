"""
Базовые абстрактные классы.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from uuid import uuid4


class BaseEntity(ABC):
    """
    Базовый абстрактный класс для всех сущностей системы.
    Реализует общую функциональность: ID, дата создания, дата обновления.
    """
    
    def __init__(self):
        self._id: str = str(uuid4())
        self._created_at: datetime = datetime.now()
        self._updated_at: datetime = datetime.now()
    
    @property
    def id(self) -> str:
        """
        Получить уникальный идентификатор сущности.
        
        Returns:
            str: Уникальный идентификатор
        """
        return self._id
    
    @property
    def created_at(self) -> datetime:
        """
        Получить дату создания сущности.
        
        Returns:
            datetime: Дата создания
        """
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        """
        Получить дату последнего обновления сущности.
        
        Returns:
            datetime: Дата обновления
        """
        return self._updated_at
    
    def _update_timestamp(self) -> None:
        """
        Обновить метку времени последнего изменения.
        """
        self._updated_at = datetime.now()


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
