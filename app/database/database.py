import logging
from typing import Generator

from sqlmodel import Session, SQLModel, create_engine

from .config import get_settings

logger = logging.getLogger(__name__)


def get_database_engine():
    settings = get_settings()
    return create_engine(
        url=settings.DATABASE_URL_psycopg,
        echo=settings.DEBUG,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=3600,
    )


engine = get_database_engine()


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def init_db(drop_all: bool = False) -> None:
    if drop_all:
        logger.info("Dropping all database tables")
        SQLModel.metadata.drop_all(engine)
    logger.info("Creating database tables")
    SQLModel.metadata.create_all(engine)