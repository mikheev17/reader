import logging
from decimal import Decimal
from typing import List, Dict

from database.config import get_settings
from database.database import get_session
from dto import UserSignupRequest, UserSigninRequest
from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from models import User
from services.auth.auth import get_current_user, require_admin
from services.auth.password_service import hash_password, verify_password
from services.auth.token_service import create_access_token
from services.crud import user as UserService
from services.user_service import create_user_with_balance

from dto.auth.register_form import RegisterForm
from starlette.responses import RedirectResponse

from dto.auth.login_form import LoginForm

# Configure logging
logger = logging.getLogger(__name__)
settings = get_settings()

user_route = APIRouter()
templates = Jinja2Templates(directory="views")

@user_route.get("/signup", response_class=HTMLResponse)
async def signup_get(request: Request):
    context = {
        "request": request,
    }
    return templates.TemplateResponse("register.html", context)


@user_route.post(
    '/signup',
    response_class=HTMLResponse)
async def signup(request: Request, session=Depends(get_session)):
    """
    Create new user account.

    Args:
        session: Database session

    Returns:
        dict: Success message

    Raises:
        HTTPException: If user already exists
        :param session:
        :param request:
    """
    form = RegisterForm(request)
    await form.load_data()

    if not await form.is_valid():
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "errors": form.errors,
                "name": form.name,
                "email": form.email,
            },
        )
    try:
        if UserService.get_user_by_email(form.email, session):
            logger.warning(f"Signup attempt with existing email: {form.email}")
            return templates.TemplateResponse(
                "register.html",
                {
                    "request": request,
                    "errors": ["Пользователь уже существует"],
                    "name": form.name,
                    "email": form.email,
                },
            )

        user = User(
            username=form.name,
            email=form.email,
            password_hash=hash_password(form.password),
            english_level="B1",
        )
        validation = user.validate()
        if not validation.is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"validation_errors": [e.message for e in validation.errors]},
            )
        create_user_with_balance(user, Decimal('100.00'), session)
        logger.info(f"New user registered: {form.email}")
        return RedirectResponse("/signin", status_code=302)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during signup: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user"
        )

@user_route.get("/signin", response_class=HTMLResponse)
async def signin_get(request: Request):
    context = {
        "request": request,
    }
    return templates.TemplateResponse("login.html", context)


@user_route.post('/signin')
async def signin(request: Request, session=Depends(get_session)):
    """
    Authenticate existing user and return JWT access token.

    Args:
        request: Request with form data
        session: Database session

    Returns:
        Redirect to dashboard on success, or login template with errors
    """
    form = LoginForm(request)
    await form.load_data()

    if not await form.is_valid():
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "errors": form.errors, "email": form.email or ""},
        )

    user = UserService.get_user_by_email(form.email, session)
    if user is None:
        logger.warning(f"Login attempt with non-existent email: {form.email}")
        form.errors.append("Неверный email или пароль")
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "errors": form.errors, "email": form.email or ""},
        )

    if not verify_password(form.password, user.password_hash):
        logger.warning(f"Failed login attempt for user: {form.email}")
        form.errors.append("Неверный email или пароль")
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "errors": form.errors, "email": form.email or ""},
        )

    access_token = create_access_token(user.id)
    response = RedirectResponse("/dashboard", status_code=302)
    cookie_name = getattr(settings, "COOKIE_NAME", "access_token")
    response.set_cookie(
        key=cookie_name,
        value=f"Bearer {access_token}",
        httponly=True,
    )
    return response


@user_route.get("/logout")
async def logout():
    """Clear auth cookie and redirect to signin."""
    response = RedirectResponse("/signin", status_code=302)
    cookie_name = getattr(settings, "COOKIE_NAME", "access_token")
    response.delete_cookie(key=cookie_name)
    return response


@user_route.get(
    "/users",
    response_model=List[User],
    summary="Get all users",
    response_description="List of all users"
)
async def get_all_users(
    session=Depends(get_session),
    current_user=Depends(require_admin),
) -> List[User]:
    """
    Get list of all users. Requires valid JWT and ADMIN role.

    Args:
        session: Database session
        current_user: Authenticated admin user (from JWT)

    Returns:
        List[UserResponse]: List of users
    """
    try:
        users = UserService.get_all_users(session)
        logger.info(f"Retrieved {len(users)} users")
        return users
    except Exception as e:
        logger.error(f"Error retrieving users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving users"
        )