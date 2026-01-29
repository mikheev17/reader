"""
Balance-related Data Transfer Objects.
"""

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class BalanceReplenishRequest(BaseModel):
    """Schema for balance replenishment. user_id берётся из JWT."""
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
