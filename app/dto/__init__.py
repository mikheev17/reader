"""
Data Transfer Objects (DTOs) for the application.
"""

from .user import UserSignupRequest, UserSigninRequest
from .task import TaskCreateRequest, TaskResponse, PredictionResponse
from .balance import BalanceReplenishRequest, BalanceResponse
from .document import CreateDocumentRequest, CreateDocumentResponse, DocumentResponse, DocumentDetailResponse

__all__ = [
    "UserSignupRequest",
    "UserSigninRequest",
    "TaskCreateRequest",
    "TaskResponse",
    "PredictionResponse",
    "BalanceReplenishRequest",
    "BalanceResponse",
    "CreateDocumentRequest",
    "CreateDocumentResponse",
    "DocumentResponse",
    "DocumentDetailResponse",
]
