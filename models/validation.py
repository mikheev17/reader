"""
Модели для валидации данных.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ValidationError:
    """
    Класс ошибки валидации.
    """
    field: str
    message: str


class ValidationResult:
    """
    Класс результата валидации.
    """
    
    def __init__(self, is_valid: bool, errors: Optional[List[ValidationError]] = None):
        """
        Инициализация результата валидации.
        
        Args:
            is_valid: True если валидация прошла успешно
            errors: Список ошибок валидации
        """
        self._is_valid: bool = is_valid
        self._errors: List[ValidationError] = errors or []
    
    @property
    def is_valid(self) -> bool:
        """
        Проверить, прошла ли валидация успешно.
        
        Returns:
            bool: True если валидация успешна
        """
        return self._is_valid
    
    @property
    def errors(self) -> List[ValidationError]:
        """
        Получить список ошибок валидации.
        
        Returns:
            List[ValidationError]: Список ошибок
        """
        return self._errors.copy()
    
    def has_errors(self) -> bool:
        """
        Проверить, есть ли ошибки валидации.
        
        Returns:
            bool: True если есть ошибки
        """
        return len(self._errors) > 0
    
    def get_error_messages(self) -> List[str]:
        """
        Получить список сообщений об ошибках.
        
        Returns:
            List[str]: Список сообщений
        """
        return [error.message for error in self._errors]
    
    def to_dict(self) -> dict:
        """
        Преобразовать результат валидации в словарь.
        
        Returns:
            dict: Словарь с результатом валидации
        """
        return {
            'is_valid': self._is_valid,
            'errors': [
                {'field': error.field, 'message': error.message}
                for error in self._errors
            ]
        }
