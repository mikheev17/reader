"""
Database connection for ml_worker.
Uses same env vars as app: DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME.
Set them in .env (see .env.template).
"""

import os
from contextlib import contextmanager

import psycopg2

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_NAME = os.environ.get("DB_NAME")


def _validate_db_config() -> None:
    if not all([DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME]):
        raise ValueError(
            "Missing required DB env vars: DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME. "
            "Copy .env.template to .env and set values."
        )


def _connection_params():
    _validate_db_config()
    return {
        "host": DB_HOST,
        "port": int(DB_PORT),
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
