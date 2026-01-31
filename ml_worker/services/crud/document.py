"""Document CRUD for ml_worker."""

from uuid import UUID

from psycopg2.extras import RealDictCursor

from database import db_connection


def get_document_content(document_id: UUID) -> str | None:
    """Get document text content by id. Returns None if not found or deleted."""
    with db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT content
                FROM text_documents
                WHERE id = %s AND deleted_at IS NULL
                """,
                (str(document_id),),
            )
            row = cur.fetchone()
            return row["content"] if row else None


def mark_document_processed(document_id: UUID) -> bool:
    """Mark document as processed (is_processed = true)."""
    with db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE text_documents
                SET is_processed = true, updated_at = NOW()
                WHERE id = %s AND deleted_at IS NULL
                """,
                (str(document_id),),
            )
            return cur.rowcount > 0
