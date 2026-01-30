"""
Data Transfer Objects (DTOs) for the application.
"""

from .user import UserSignupRequest, UserSigninRequest
from .task import TaskCreateRequest, TaskResponse
from .balance import BalanceReplenishRequest, BalanceResponse
from .document import CreateDocumentRequest, CreateDocumentResponse, DocumentResponse

__all__ = [
    "UserSignupRequest",
    "UserSigninRequest",
    "TaskCreateRequest",
    "TaskResponse",
    "BalanceReplenishRequest",
    "BalanceResponse",
    "CreateDocumentRequest",
    "CreateDocumentResponse",
    "DocumentResponse",
]
