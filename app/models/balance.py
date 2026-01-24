"""
Модель баланса пользователя.
"""

from decimal import Decimal
from uuid import UUID

from sqlalchemy import DECIMAL
from sqlmodel import Field, Column

from .base import BaseSQLModel, Validatable
from .validation import ValidationResult, ValidationError


class Balance(BaseSQLModel, Validatable, table=True):
    """
    Класс баланса пользователя в условных кредитах (SQLModel).
    """
    __tablename__ = "balances"
    
    user_id: UUID = Field(foreign_key="users.id", unique=True, index=True)
    balance: Decimal = Field(default=Decimal('0.00'), sa_column=Column(DECIMAL(10, 2)))
    
    def replenish(self, amount: Decimal) -> bool:
        """
        Пополнить баланс.
        
        Args:
            amount: Сумма пополнения
            
        Returns:
            bool: True если пополнение успешно
        """
        if amount <= 0:
            return False
        
        self.balance += amount
        self._update_timestamp()
        return True
    
    def withdraw(self, amount: Decimal) -> bool:
        """
        Списать средства с баланса.
        
        Args:
            amount: Сумма списания
            
        Returns:
            bool: True если списание успешно (баланс достаточен)
        """
        if amount <= 0:
            return False
        
        if self.balance < amount:
            return False
        
        self.balance -= amount
        self._update_timestamp()
        return True
    
    def has_sufficient_balance(self, amount: Decimal) -> bool:
        """
        Проверить, достаточно ли средств на балансе.
        
        Args:
            amount: Требуемая сумма
            
        Returns:
            bool: True если баланс достаточен
        """
        return self.balance >= amount
    
    def validate(self) -> ValidationResult:
        """
        Валидировать баланс.
        
        Returns:
            ValidationResult: Результат валидации
        """
        errors = []
        
        if not self.user_id:
            errors.append(ValidationError("user_id", "ID пользователя не может быть пустым"))
        
        if self.balance < 0:
            errors.append(ValidationError("balance", "Баланс не может быть отрицательным"))
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)
    
    def to_dict(self) -> dict:
        """
        Преобразовать баланс в словарь.
        
        Returns:
            dict: Словарь с данными баланса
        """
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'balance': float(self.balance),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
