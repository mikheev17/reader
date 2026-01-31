"""
Database connection and task status updates for ml_worker.
Uses same env vars as app: DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME.
"""

import os
from contextlib import contextmanager
from uuid import UUID

import psycopg2

DB_HOST = os.environ.get("DB_HOST", "database")
DB_PORT = int(os.environ.get("DB_PORT", "5432"))
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASS = os.environ.get("DB_PASS", "postgres")
DB_NAME = os.environ.get("DB_NAME", "postgres")


def _connection_params():
    return {
        "host": DB_HOST,
        "port": DB_PORT,
        "user": DB_USER,
        "password": DB_PASS,
        "dbname": DB_NAME,
    }


@contextmanager
def db_connection():
    conn = psycopg2.connect(**_connection_params())
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def update_task_status(task_id: UUID, status: str, error_message: str | None = None) -> bool:
    """
    Update task status in the database.
    Status must be one of: PENDING, PROCESSING, COMPLETED, FAILED (PostgreSQL enum names).
    """
    with db_connection() as conn:
        with conn.cursor() as cur:
            if error_message and status == "FAILED":
                cur.execute(
                    """
                    UPDATE tasks
                    SET status = %s, error_message = %s, updated_at = NOW()
                    WHERE id = %s
                    """,
                    (status, error_message, str(task_id)),
                )
            else:
                cur.execute(
                    """
                    UPDATE tasks
                    SET status = %s, updated_at = NOW()
                    WHERE id = %s
                    """,
                    (status, str(task_id)),
                )
            return cur.rowcount > 0
