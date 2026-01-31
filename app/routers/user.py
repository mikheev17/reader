import logging
from decimal import Decimal
from typing import List, Dict

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

# Configure logging
logger = logging.getLogger(__name__)

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
async def login_get(request: Request):
    context = {
        "request": request,
    }
    return templates.TemplateResponse("login.html", context)


@user_route.post('/signin')
async def signin(data: UserSigninRequest, session=Depends(get_session)) -> Dict[str, str]:
    """
    Authenticate existing user and return JWT access token.

    Args:
        data: User credentials
        session: Database session

    Returns:
        dict: access_token (JWT) and token_type

    Raises:
        HTTPException: If authentication fails
    """
    user = UserService.get_user_by_email(data.email, session)
    if user is None:
        logger.warning(f"Login attempt with non-existent email: {data.email}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")
    
    if not verify_password(data.password, user.password_hash):
        logger.warning(f"Failed login attempt for user: {data.email}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Wrong credentials passed")
    
    access_token = create_access_token(user.id)
    return {"access_token": access_token, "token_type": "bearer"}

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