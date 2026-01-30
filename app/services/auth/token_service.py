"""Создание и проверка JWT-токенов."""

from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

import jwt
from database.config import get_settings


def create_access_token(subject: UUID | str) -> str:
    """Create a JWT access token for the given user id (subject)."""
    settings = get_settings()
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload = {"sub": str(subject), "exp": expire}
    return jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> dict[str, Any]:
    """
    Decode and validate JWT token. Returns payload dict with 'sub' (user id).
    Raises jwt.PyJWTError on invalid or expired token.
    """
    settings = get_settings()
    return jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=[settings.JWT_ALGORITHM],
    )
