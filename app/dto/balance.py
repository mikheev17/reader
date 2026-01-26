"""
Balance-related Data Transfer Objects.
"""

from pydantic import BaseModel, Field
from uuid import UUID
from decimal import Decimal


class BalanceReplenishRequest(BaseModel):
    """Schema for balance replenishment."""
    user_id: UUID = Field(..., description="ID пользователя")
    amount: Decimal = Field(..., gt=0, description="Сумма пополнения (должна быть больше 0)")


class BalanceResponse(BaseModel):
    """Schema for balance response."""
    id: UUID
    user_id: UUID
    balance: Decimal
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
