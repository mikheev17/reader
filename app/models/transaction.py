"""
Модели транзакций и предсказаний.
"""

from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import DECIMAL
from sqlmodel import Field, Column

from .base import BaseSQLModel, Validatable
from .validation import ValidationResult, ValidationError


class TransactionType(str, Enum):
    """
    Типы транзакций.
    """
    REPLENISHMENT = "replenishment"  # Пополнение баланса
    WITHDRAWAL = "withdrawal"  # Списание за использование ML сервиса


class Transaction(BaseSQLModel, Validatable, table=True):
    """
    Класс транзакции (пополнение или списание баланса) (SQLModel).
    """
    __tablename__ = "transactions"
    
    user_id: UUID = Field(foreign_key="users.id", index=True)
    transaction_type: TransactionType
    amount: Decimal = Field(sa_column=Column(DECIMAL(10, 2)))
    task_id: Optional[UUID] = Field(default=None, foreign_key="tasks.id")

    def validate(self) -> ValidationResult:
        """
        Валидировать транзакцию.
        
        Returns:
            ValidationResult: Результат валидации
        """
        errors = []
        
        if not self.user_id:
            errors.append(ValidationError("user_id", "ID пользователя не может быть пустым"))
        
        if self.amount <= 0:
            errors.append(ValidationError("amount", "Сумма транзакции должна быть положительной"))
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)
    
    def to_dict(self) -> dict:
        """
        Преобразовать транзакцию в словарь.
        
        Returns:
            dict: Словарь с данными транзакции
        """
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'transaction_type': self.transaction_type.value if isinstance(self.transaction_type, Enum) else self.transaction_type,
            'amount': float(self.amount),
            'task_id': str(self.task_id) if self.task_id else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
