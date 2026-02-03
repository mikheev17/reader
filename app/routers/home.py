from decimal import Decimal
from typing import Dict
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from database.database import get_session
from services.auth.auth import authenticate_cookie
from services.crud.balance import get_balance_by_user_id
from services.crud.user import get_user_by_id

home_route = APIRouter()
templates = Jinja2Templates(directory="views")

@home_route.get("/", response_class=HTMLResponse)
async def index(request: Request):
    user = None
    context = {
        "login": user,
        "request": request
    }
    return templates.TemplateResponse("index.html", context)


@home_route.get(
    "/health",
    response_model=Dict[str, str],
    summary="Health check endpoint",
    description="Returns service health status"
)
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint for monitoring.

    Returns:
        Dict[str, str]: Health status message
    
    Raises:
        HTTPException: If service is unhealthy
    """
    try:
        # Add actual health checks here
        return {"status": "healthy"}
    except Exception as e:
        raise HTTPException(
            status_code=503, 
            detail="Service unavailable"
        )

@home_route.get("/dashboard", response_class=HTMLResponse)
async def get_private(
    request: Request,
    user_id: str = Depends(authenticate_cookie),
    session=Depends(get_session),
):
    user = get_user_by_id(UUID(user_id), session)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    balance_record = get_balance_by_user_id(user.id, session)
    balance_value = balance_record.balance if balance_record else Decimal("0")
    context = {
        "name": user.username or user.email,
        "email": user.email,
        "balance": float(balance_value),
        "request": request,
    }
    return templates.TemplateResponse("dashboard.html", context)

