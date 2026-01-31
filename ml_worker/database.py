"""
Database connection for ml_worker.
Uses same env vars as app: DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME.
"""

import os
from contextlib import contextmanager

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
