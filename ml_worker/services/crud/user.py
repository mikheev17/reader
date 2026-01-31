"""User CRUD for ml_worker."""

from uuid import UUID

from psycopg2.extras import RealDictCursor

from database import db_connection


def get_user_english_level(user_id: UUID) -> str | None:
    """Get user english_level (A1, A2, B1, B2). Returns None if not set."""
    with db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT english_level
                FROM users
                WHERE id = %s
                """,
                (str(user_id),),
            )
            row = cur.fetchone()
            return row["english_level"] if row and row["english_level"] else None
