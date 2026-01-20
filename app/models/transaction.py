"""
Модели транзакций и предсказаний.
"""

from decimal import Decimal
from enum import Enum
from typing import Optional, Any
from .base import BaseEntity, Validatable
from .validation import ValidationResult, ValidationError


class TransactionType(Enum):
    """
    Типы транзакций.
    """
    REPLENISHMENT = "replenishment"  # Пополнение баланса
    WITHDRAWAL = "withdrawal"  # Списание за использование ML сервиса


class Transaction(BaseEntity, Validatable):
    """
    Класс транзакции (пополнение или списание баланса).
    """
    
    def __init__(
        self,
        user_id: str,
        transaction_type: TransactionType,
        amount: Decimal,
        task_id: Optional[str] = None,
    ):
        """
        Инициализация транзакции.
        
        Args:
            user_id: ID пользователя
            transaction_type: Тип транзакции
            amount: Сумма транзакции
            task_id: ID задачи, связанной с транзакцией (опционально, для списаний)
        """
        super().__init__()
        self._user_id: str = user_id
        self._transaction_type: TransactionType = transaction_type
        self._amount: Decimal = amount
        self._task_id: Optional[str] = task_id

    @property
    def user_id(self) -> str:
        """
        Получить ID пользователя.
        
        Returns:
            str: ID пользователя
        """
        return self._user_id
    
    @property
    def transaction_type(self) -> TransactionType:
        """
        Получить тип транзакции.
        
        Returns:
            TransactionType: Тип транзакции
        """
        return self._transaction_type
    
    @property
    def amount(self) -> Decimal:
        """
        Получить сумму транзакции.
        
        Returns:
            Decimal: Сумма транзакции
        """
        return self._amount
    
    @property
    def task_id(self) -> Optional[str]:
        """
        Получить ID задачи, связанной с транзакцией.
        
        Returns:
            Optional[str]: ID задачи или None
        """
        return self._task_id

    def validate(self) -> ValidationResult:
        """
        Валидировать транзакцию.
        
        Returns:
            ValidationResult: Результат валидации
        """
        errors = []
        
        if not self._user_id:
            errors.append(ValidationError("user_id", "ID пользователя не может быть пустым"))
        
        if self._amount <= 0:
            errors.append(ValidationError("amount", "Сумма транзакции должна быть положительной"))
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)
    
    def to_dict(self) -> dict:
        """
        Преобразовать транзакцию в словарь.
        
        Returns:
            dict: Словарь с данными транзакции
        """
        return {
            'id': self._id,
            'user_id': self._user_id,
            'transaction_type': self._transaction_type.value,
            'amount': float(self._amount),
            'task_id': self._task_id,
            'created_at': self._created_at.isoformat(),
            'updated_at': self._updated_at.isoformat()
        }