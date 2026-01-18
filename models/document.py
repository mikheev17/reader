"""
Модели документов и текстовых файлов.
"""

from enum import Enum
from typing import Optional
from base import BaseEntity, Validatable
from validation import ValidationResult, ValidationError


class DocumentType(Enum):
    """
    Типы поддерживаемых документов.
    """
    TXT = "txt"
    EPUB = "epub"


class TextDocument(BaseEntity, Validatable):
    """
    Класс текстового документа.
    """
    
    def __init__(
        self,
        user_id: str,
        document_type: DocumentType,
        content: str,
        filename: Optional[str] = None
    ):
        """
        Инициализация текстового документа.
        
        Args:
            user_id: ID пользователя, загрузившего документ
            document_type: Тип документа (txt/epub)
            content: Содержимое документа
            filename: Имя файла (опционально)
        """
        super().__init__()
        self._user_id: str = user_id
        self._document_type: DocumentType = document_type
        self._content: str = content
        self._filename: Optional[str] = filename
        self._is_processed: bool = False
    
    @property
    def user_id(self) -> str:
        """
        Получить ID пользователя.
        
        Returns:
            str: ID пользователя
        """
        return self._user_id
    
    @property
    def document_type(self) -> DocumentType:
        """
        Получить тип документа.
        
        Returns:
            DocumentType: Тип документа
        """
        return self._document_type
    
    @property
    def content(self) -> str:
        """
        Получить содержимое документа.
        
        Returns:
            str: Содержимое документа
        """
        return self._content
    
    @content.setter
    def content(self, value: str) -> None:
        """
        Установить содержимое документа.
        
        Args:
            value: Новое содержимое
        """
        self._content = value
        self._update_timestamp()
    
    @property
    def filename(self) -> Optional[str]:
        """
        Получить имя файла.
        
        Returns:
            Optional[str]: Имя файла или None
        """
        return self._filename
    
    @property
    def is_processed(self) -> bool:
        """
        Проверить, обработан ли документ.
        
        Returns:
            bool: True если документ обработан
        """
        return self._is_processed
    
    def mark_as_processed(self) -> None:
        """
        Отметить документ как обработанный.
        """
        self._is_processed = True
        self._update_timestamp()
    
    def validate(self) -> ValidationResult:
        """
        Валидировать документ.
        
        Returns:
            ValidationResult: Результат валидации
        """
        errors = []
        
        if not self._user_id:
            errors.append(ValidationError("user_id", "ID пользователя не может быть пустым"))
        
        if not self._content or len(self._content.strip()) == 0:
            errors.append(ValidationError("content", "Содержимое документа не может быть пустым"))
        
        if self._document_type not in DocumentType:
            errors.append(ValidationError("document_type", "Неподдерживаемый тип документа"))
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)
    
    def to_dict(self) -> dict:
        """
        Преобразовать документ в словарь.
        
        Returns:
            dict: Словарь с данными документа
        """
        return {
            'id': self._id,
            'user_id': self._user_id,
            'document_type': self._document_type.value,
            'filename': self._filename,
            'is_processed': self._is_processed,
            'content_length': len(self._content),
            'created_at': self._created_at.isoformat(),
            'updated_at': self._updated_at.isoformat()
        }
