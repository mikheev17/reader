"""
Task-related Data Transfer Objects.
"""

from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID


class TaskCreateRequest(BaseModel):
    """Schema for creating a prediction task."""
    user_id: UUID = Field(..., description="ID пользователя")
    document_id: Optional[UUID] = Field(None, description="ID документа (опционально)")


class TaskResponse(BaseModel):
    """Schema for task response."""
    id: UUID
    user_id: UUID
    document_id: Optional[UUID]
    status: str
    error_message: Optional[str]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
