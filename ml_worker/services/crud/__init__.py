"""CRUD layer for ml_worker (raw psycopg2)."""

from .task import get_task_by_id, update_task_status
from .document import get_document_content, mark_document_processed
from .user import get_user_english_level
from .prediction import create_prediction

__all__ = [
    "get_task_by_id",
    "update_task_status",
    "get_document_content",
    "mark_document_processed",
    "get_user_english_level",
    "create_prediction",
]
