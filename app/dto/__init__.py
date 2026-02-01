"""
Data Transfer Objects (DTOs) for the application.
"""

from .user import UserSignupRequest, UserSigninRequest
from .task import TaskCreateRequest, TaskResponse, PredictionResponse, PredictionHistoryItem
from .balance import BalanceReplenishRequest, BalanceResponse, TransactionResponse
from .document import CreateDocumentRequest, CreateDocumentResponse, DocumentResponse, DocumentDetailResponse

__all__ = [
    "UserSignupRequest",
    "UserSigninRequest",
    "TaskCreateRequest",
    "TaskResponse",
    "PredictionResponse",
    "PredictionHistoryItem",
    "BalanceReplenishRequest",
    "BalanceResponse",
    "TransactionResponse",
    "CreateDocumentRequest",
    "CreateDocumentResponse",
    "DocumentResponse",
    "DocumentDetailResponse",
]
