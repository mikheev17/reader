"""Хэширование паролей (bcrypt)."""

import hashlib

import bcrypt


def _to_bcrypt_input(password: str) -> bytes:
    """Convert password to fixed-length input for bcrypt (max 72 bytes)."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest().encode("utf-8")


def hash_password(password: str) -> str:
    """Hash a plain password for storage."""
    data = _to_bcrypt_input(password)
    return bcrypt.hashpw(data, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a stored hash."""
    data = _to_bcrypt_input(plain_password)
    return bcrypt.checkpw(data, hashed_password.encode("utf-8"))
