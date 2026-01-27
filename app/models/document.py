"""
Модели документов и текстовых файлов.
"""

from enum import Enum
from typing import Optional
from datetime import datetime
from sqlmodel import Field, Column, Text
from uuid import UUID
from .base import BaseSQLModel, Validatable
from .validation import ValidationResult, ValidationError


class DocumentType(str, Enum):
    """
    Типы поддерживаемых документов.
    """
    TXT = "txt"
    EPUB = "epub"


class TextDocument(BaseSQLModel, Validatable, table=True):
    """
    Класс текстового документа (SQLModel).
    """
    __tablename__ = "text_documents"
    
    user_id: UUID = Field(foreign_key="users.id", index=True)
    document_type: DocumentType
    content: str = Field(sa_column=Column(Text))
    filename: Optional[str] = None
    is_processed: bool = Field(default=False)
    deleted_at: Optional[datetime] = Field(default=None)
    
    def mark_as_processed(self) -> None:
        """
        Отметить документ как обработанный.
        """
        self.is_processed = True
        self._update_timestamp()
    
    def soft_delete(self) -> None:
        """
        Выполнить мягкое удаление документа.
        """
        self.deleted_at = datetime.now()
        self._update_timestamp()
    
    def is_deleted(self) -> bool:
        """
        Проверить, удален ли документ.
        
        Returns:
            bool: True если документ удален
        """
        return self.deleted_at is not None
    
    def validate(self) -> ValidationResult:
        """
        Валидировать документ.
        
        Returns:
            ValidationResult: Результат валидации
        """
        errors = []
        
        if not self.user_id:
            errors.append(ValidationError("user_id", "ID пользователя не может быть пустым"))
        
        if not self.content or len(self.content.strip()) == 0:
            errors.append(ValidationError("content", "Содержимое документа не может быть пустым"))
        
        if self.document_type not in DocumentType:
            errors.append(ValidationError("document_type", "Неподдерживаемый тип документа"))
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)
    
    def to_dict(self) -> dict:
        """
        Преобразовать документ в словарь.
        
        Returns:
            dict: Словарь с данными документа
        """
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'document_type': self.document_type.value if isinstance(self.document_type, Enum) else self.document_type,
            'filename': self.filename,
            'is_processed': self.is_processed,
            'content_length': len(self.content),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
