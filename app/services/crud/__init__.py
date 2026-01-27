"""CRUD service layer for application models."""

# Expose commonly used CRUD modules for convenience
from . import user as user_crud
from . import balance as balance_crud
from . import document as document_crud
from . import task as task_crud
from . import prediction as prediction_crud
from . import transaction as transaction_crud

__all__ = [
    "user_crud",
    "balance_crud",
    "document_crud",
    "task_crud",
    "prediction_crud",
    "transaction_crud",
]
