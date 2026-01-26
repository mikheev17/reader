import logging
from contextlib import asynccontextmanager
from typing import Dict

import uvicorn
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from sqlmodel import Session, select

from test_system_smoke import test
from database.database import get_session
from init_standard_data import init_data
from models.user import User
from routers import user as user_router
from routers import task as task_router
from routers import balance as balance_router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        init_data()
        test()
        logger.info("База данных инициализирована")
    except Exception as e:
        logger.error(f"Ошибка при инициализации базы данных: {e}")
    yield
    # Shutdown
    pass


app = FastAPI(
    title="Сервисное API",
    description="API для работы с читалкой",
    version="1.0.0",
    lifespan=lifespan
)

# Регистрация роутеров
app.include_router(user_router.user_route, tags=["users"])
app.include_router(task_router.task_route, tags=["tasks"])
app.include_router(balance_router.balance_route, tags=["balance"])

@app.get("/", response_model=Dict[str, str])
async def index(session: Session = Depends(get_session)) -> Dict[str, str]:
    """
    Корневой эндпоинт, возвращающий приветственное сообщение с информацией о пользователе.
    
    Returns:
        Dict[str, str]: Приветственное сообщение с информацией о пользователе
    """
    try:
        # Ищем пользователя в базе данных
        statement = select(User).where(User.email == "maksim.mikheev@gmail.com")
        user = session.exec(statement).first()
        
        if user:
            logger.info(f"Найден пользователь: {user.email}")
            return {"message": f"Hello world! User: {user.email} (ID: {user.id})"}
        else:
            # Если пользователь не найден, создаем нового
            user = User(email="maksim.mikheev@gmail.com", password_hash="12345678")
            session.add(user)
            session.commit()
            session.refresh(user)
            logger.info(f"Создан новый пользователь: {user.email}")
            return {"message": f"Hello world! New user created: {user.email} (ID: {user.id})"}
    except Exception as e:
        logger.error(f"Ошибка в маршруте index: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Эндпоинт проверки работоспособности для мониторинга.
    
    Returns:
        Dict[str, str]: Сообщение о статусе
    """
    logger.info("Эндпоинт health_check успешно вызван")
    return {"status": "healthy"}

# Обработчики ошибок
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    logger.warning(f"HTTPException: {exc.detail} для запроса {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8081,
        reload=True,
        log_level="debug"
    )
