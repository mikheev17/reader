"""
Модель баланса пользователя.
"""

from decimal import Decimal
from .base import BaseEntity, Validatable
from .validation import ValidationResult, ValidationError


class Balance(BaseEntity, Validatable):
    """
    Класс баланса пользователя в условных кредитах.
    """
    
    def __init__(self, user_id: str, initial_balance: Decimal = Decimal('0.00')):
        """
        Инициализация баланса.
        
        Args:
            user_id: ID пользователя
            initial_balance: Начальный баланс (по умолчанию 0.00)
        """
        super().__init__()
        self._user_id: str = user_id
        self._balance: Decimal = initial_balance
    
    @property
    def user_id(self) -> str:
        """
        Получить ID пользователя.
        
        Returns:
            str: ID пользователя
        """
        return self._user_id
    
    @property
    def balance(self) -> Decimal:
        """
        Получить текущий баланс.
        
        Returns:
            Decimal: Текущий баланс
        """
        return self._balance
    
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
        
        self._balance += amount
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
        
        if self._balance < amount:
            return False
        
        self._balance -= amount
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
        return self._balance >= amount
    
    def validate(self) -> ValidationResult:
        """
        Валидировать баланс.
        
        Returns:
            ValidationResult: Результат валидации
        """
        errors = []
        
        if not self._user_id:
            errors.append(ValidationError("user_id", "ID пользователя не может быть пустым"))
        
        if self._balance < 0:
            errors.append(ValidationError("balance", "Баланс не может быть отрицательным"))
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)
    
    def to_dict(self) -> dict:
        """
        Преобразовать баланс в словарь.
        
        Returns:
            dict: Словарь с данными баланса
        """
        return {
            'id': self._id,
            'user_id': self._user_id,
            'balance': float(self._balance),
            'created_at': self._created_at.isoformat(),
            'updated_at': self._updated_at.isoformat()
        }
