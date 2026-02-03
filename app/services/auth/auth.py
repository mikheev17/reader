"""JWT authentication dependency for FastAPI."""

from uuid import UUID

import jwt
from database.database import get_session
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer,HTTPAuthorizationCredentials, HTTPBearer
from models import User
from services.auth.token_service import decode_access_token
from services.crud import user as UserService

security = HTTPBearer(auto_error=False)

from dto.auth.cookie_auth import OAuth2PasswordBearerWithCookie

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")

async def authenticate(token: str = Depends(oauth2_scheme)) -> str:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sign in for access",
        )
    try:
        payload = decode_access_token(token)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    return sub

oauth2_scheme_cookie = OAuth2PasswordBearerWithCookie(tokenUrl="/home/token")

async def authenticate_cookie(token: str = Depends(oauth2_scheme_cookie)) -> str:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sign in for access",
        )
    token = token.removeprefix("Bearer ")
    try:
        payload = decode_access_token(token)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    return sub

async def get_current_user_cookie_or_bearer(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    session=Depends(get_session),
) -> User:
    """
    Get current User from Authorization: Bearer <token> or from cookie (for dashboard).
    """
    token = None
    if credentials is not None:
        token = credentials.credentials
    if token is None:
        from database.config import get_settings
        settings = get_settings()
        cookie_name = getattr(settings, "COOKIE_NAME", "access_token")
        raw = request.cookies.get(cookie_name)
        if raw:
            token = raw.removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = decode_access_token(token)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        user_id = UUID(sub)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = UserService.get_user_by_id(user_id, session)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not getattr(user, "is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is deactivated",
        )
    return user


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    session=Depends(get_session),
) -> User:
    """
    Validate JWT from Authorization: Bearer <token> and return the current User.
    Raises 401 if token is missing or invalid.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials
    try:
        payload = decode_access_token(token)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        user_id = UUID(sub)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = UserService.get_user_by_id(user_id, session)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not getattr(user, "is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is deactivated",
        )
    return user


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Require the current user to have the ADMIN role.
    Raises 403 if the user is not an admin.
    """
    from models import UserRole

    if getattr(current_user, "role", None) != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )
    return current_user