"""
Модели пользователей и ролей.
"""

from enum import Enum
from typing import Optional

from sqlmodel import Field

from .base import Validatable, BaseSQLModel
from .validation import ValidationResult, ValidationError


class UserRole(str, Enum):
    """
    Роли пользователей.
    """
    USER = "user"
    ADMIN = "admin"


class User(BaseSQLModel, Validatable, table=True):
    """
    Класс пользователя (SQLModel).
    """
    __tablename__ = "users"
    
    email: str = Field(unique=True, index=True)
    password_hash: str
    username: Optional[str] = None
    english_level: Optional[str] = None
    role: UserRole = Field(default=UserRole.USER)
    is_active: bool = Field(default=True)
    
    def activate(self) -> None:
        """
        Активировать пользователя.
        """
        self.is_active = True
        self._update_timestamp()
    
    def deactivate(self) -> None:
        """
        Деактивировать пользователя.
        """
        self.is_active = False
        self._update_timestamp()
    
    def validate(self) -> ValidationResult:
        """
        Валидировать данные пользователя.
        Реализация абстрактного метода из Validatable.
        
        Returns:
            ValidationResult: Результат валидации
        """
        errors = []
        
        if not self.email or '@' not in self.email:
            errors.append(ValidationError("email", "Некорректный email"))
        
        if not self.password_hash:
            errors.append(ValidationError("password_hash", "Пароль не может быть пустым"))
        
        if self.english_level and self.english_level not in ['A1', 'A2', 'B1', 'B2']:
            errors.append(ValidationError("english_level", "Уровень английского должен быть A1, A2, B1 или B2"))
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)
    
    def to_dict(self) -> dict:
        """
        Преобразовать пользователя в словарь.
        
        Returns:
            dict: Словарь с данными пользователя
        """
        return {
            'id': str(self.id),
            'email': self.email,
            'username': self.username,
            'english_level': self.english_level,
            'role': self.role.value if isinstance(self.role, Enum) else self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
