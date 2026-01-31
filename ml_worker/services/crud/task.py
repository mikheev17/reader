"""Task CRUD for ml_worker."""

from uuid import UUID

from psycopg2.extras import RealDictCursor

from database import db_connection


def get_task_by_id(task_id: UUID) -> dict | None:
    """Get task by id. Returns dict with document_id, user_id or None if not found."""
    with db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT document_id, user_id
                FROM tasks
                WHERE id = %s
                """,
                (str(task_id),),
            )
            row = cur.fetchone()
            if not row:
                return None
            return dict(row)


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
