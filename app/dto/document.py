"""
Document-related Data Transfer Objects.
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from uuid import UUID


DocumentTypeStr = Literal["txt", "epub"]


class CreateDocumentRequest(BaseModel):
    """Schema for creating a document and task for its processing."""
    user_id: UUID = Field(..., description="ID пользователя")
    content: str = Field(..., min_length=1, description="Содержимое документа")
    document_type: DocumentTypeStr = Field(..., description="Тип документа: txt или epub")
    filename: Optional[str] = Field(None, description="Имя файла (опционально)")


class DocumentResponse(BaseModel):
    """Schema for document response."""
    id: UUID
    user_id: UUID
    document_type: str
    filename: Optional[str]
    is_processed: bool
    content_length: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class CreateDocumentResponse(BaseModel):
    """Schema for create_document response (document + task)."""
    document: DocumentResponse
    task_id: UUID
    task_status: str
