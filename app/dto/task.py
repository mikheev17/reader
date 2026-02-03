"""
Task-related Data Transfer Objects.
"""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class TaskCreateRequest(BaseModel):
    """Schema for creating a prediction task. user_id берётся из JWT."""
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


class PredictionResponse(BaseModel):
    """Schema for prediction (word translations) response."""
    prediction_data: dict = Field(..., description="words list and english_level")


class PredictionHistoryItem(BaseModel):
    """Элемент истории предсказаний пользователя."""
    task_id: UUID
    document_id: Optional[UUID]
    document_name: Optional[str]
    created_at: str
    english_level: Optional[str] = None
    words_count: int = 0
