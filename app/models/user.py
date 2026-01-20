"""
Модели пользователей и ролей.
"""

from enum import Enum
from typing import Optional
from .base import BaseEntity, Validatable
from .validation import ValidationResult, ValidationError


class UserRole(Enum):
    """
    Роли пользователей.
    """
    USER = "user"
    ADMIN = "admin"


class User(BaseEntity, Validatable):
    """
    Класс пользователя.
    """
    
    def __init__(
        self,
        email: str,
        password_hash: str,
        username: Optional[str] = None,
        english_level: Optional[str] = None
    ):
        """
        Инициализация пользователя.
        
        Args:
            email: Email пользователя
            password_hash: Хеш пароля
            username: Имя пользователя (опционально)
            english_level: Уровень английского языка (A1-B2, опционально)
        """
        super().__init__()
        self._email: str = email
        self._password_hash: str = password_hash
        self._username: Optional[str] = username
        self._english_level: Optional[str] = english_level
        self._role: UserRole = UserRole.USER
        self._is_active: bool = True
    
    @property
    def email(self) -> str:
        """
        Получить email пользователя.
        
        Returns:
            str: Email пользователя
        """
        return self._email
    
    @email.setter
    def email(self, value: str) -> None:
        """
        Установить email пользователя.
        
        Args:
            value: Новый email
        """
        self._email = value
        self._update_timestamp()
    
    @property
    def password_hash(self) -> str:
        """
        Получить хеш пароля.
        
        Returns:
            str: Хеш пароля
        """
        return self._password_hash
    
    @password_hash.setter
    def password_hash(self, value: str) -> None:
        """
        Установить хеш пароля.
        
        Args:
            value: Новый хеш пароля
        """
        self._password_hash = value
        self._update_timestamp()
    
    @property
    def username(self) -> Optional[str]:
        """
        Получить имя пользователя.
        
        Returns:
            Optional[str]: Имя пользователя или None
        """
        return self._username
    
    @username.setter
    def username(self, value: Optional[str]) -> None:
        """
        Установить имя пользователя.
        
        Args:
            value: Новое имя пользователя
        """
        self._username = value
        self._update_timestamp()
    
    @property
    def english_level(self) -> Optional[str]:
        """
        Получить уровень английского языка.
        
        Returns:
            Optional[str]: Уровень английского (A1-B2) или None
        """
        return self._english_level
    
    @english_level.setter
    def english_level(self, value: Optional[str]) -> None:
        """
        Установить уровень английского языка.
        
        Args:
            value: Уровень английского (A1-B2) или None
        """
        self._english_level = value
        self._update_timestamp()
    
    @property
    def role(self) -> UserRole:
        """
        Получить роль пользователя.
        
        Returns:
            UserRole: Роль пользователя
        """
        return self._role
    
    @property
    def is_active(self) -> bool:
        """
        Проверить, активен ли пользователь.
        
        Returns:
            bool: True если пользователь активен
        """
        return self._is_active
    
    def activate(self) -> None:
        """
        Активировать пользователя.
        """
        self._is_active = True
        self._update_timestamp()
    
    def deactivate(self) -> None:
        """
        Деактивировать пользователя.
        """
        self._is_active = False
        self._update_timestamp()
    
    def validate(self) -> ValidationResult:
        """
        Валидировать данные пользователя.
        Реализация абстрактного метода из Validatable.
        
        Returns:
            ValidationResult: Результат валидации
        """
        errors = []
        
        if not self._email or '@' not in self._email:
            errors.append(ValidationError("email", "Некорректный email"))
        
        if not self._password_hash:
            errors.append(ValidationError("password_hash", "Пароль не может быть пустым"))
        
        if self._english_level and self._english_level not in ['A1', 'A2', 'B1', 'B2']:
            errors.append(ValidationError("english_level", "Уровень английского должен быть A1, A2, B1 или B2"))
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)
    
    def to_dict(self) -> dict:
        """
        Преобразовать пользователя в словарь.
        
        Returns:
            dict: Словарь с данными пользователя
        """
        return {
            'id': self._id,
            'email': self._email,
            'username': self._username,
            'english_level': self._english_level,
            'role': self._role.value,
            'is_active': self._is_active,
            'created_at': self._created_at.isoformat(),
            'updated_at': self._updated_at.isoformat()
        }