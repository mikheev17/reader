"""Prediction CRUD for ml_worker."""

import json
from uuid import UUID, uuid4

from database import db_connection


def create_prediction(task_id: UUID, prediction_data: dict) -> None:
    """Insert a prediction for the given task."""
    with db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO predictions (id, task_id, prediction_data, created_at, updated_at)
                VALUES (%s, %s, %s::jsonb, NOW(), NOW())
                """,
                (str(uuid4()), str(task_id), json.dumps(prediction_data)),
            )
