import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from init_standard_data import init_data
from database.config import get_settings
from database.database import get_session, init_db
from routers import user as user_router
from routers import task as task_router
from routers import balance as balance_router
from routers import transaction as transaction_router
from routers import document as document_router
from routers import home as home_router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        logger.info("Initializing database...")
        init_db()
        init_data()
        logger.info("Application startup completed successfully")
    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")
        raise
    yield
    # Shutdown
    logger.info("Application shutting down...")


def create_application() -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Returns:
        FastAPI: Configured application instance
    """
    
    app = FastAPI(
        title=settings.APP_NAME or "Reader API",
        description=settings.APP_DESCRIPTION or "Reader API",
        version=settings.API_VERSION or "v1",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        lifespan=lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routes
    app.include_router(home_router.home_route, tags=["home"])
    app.include_router(user_router.user_route, tags=["users"])
    app.include_router(task_router.task_route, tags=["tasks"])
    app.include_router(balance_router.balance_route, tags=["balance"])
    app.include_router(transaction_router.transaction_route, tags=["transactions"])
    app.include_router(document_router.document_route, tags=["documents"])

    return app

app = create_application()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    uvicorn.run(
        'api:app',
        host='0.0.0.0',
        port=8081,
        reload=True,
        log_level="info"
    )