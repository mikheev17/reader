from decimal import Decimal
from typing import Generator

from sqlmodel import SQLModel, create_engine
from sqlmodel import Session, select

from models.balance import Balance
from models.document import TextDocument, DocumentType
from models.task import Prediction
from models.task import Task, TaskStatus
from models.transaction import Transaction, TransactionType
from models.user import User, UserRole
from .config import get_settings

# Импортируем все модели для регистрации в SQLModel.metadata

def get_database_engine():
    """
    Create and configure the SQLAlchemy engine.
    
    Returns:
        Engine: Configured SQLAlchemy engine
    """
    settings = get_settings()
    
    engine = create_engine(
        url=settings.DATABASE_URL_psycopg,
        echo=settings.DEBUG,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=3600
    )
    return engine

engine = get_database_engine()

def get_session() -> Generator[Session, None, None]:
    """
    Получить сессию базы данных.
    
    Yields:
        Session: SQLModel сессия
    """
    with Session(engine) as session:
        yield session
        
def init_db(drop_all: bool = False) -> None:
    """
    Initialize database schema.
    
    Args:
        drop_all: If True, drops all tables before creation
    
    Raises:
        Exception: Any database-related exception
    """
    try:
        engine = get_database_engine()
        if drop_all:
            SQLModel.metadata.drop_all(engine)
        
        SQLModel.metadata.create_all(engine)
    except Exception as e:
        raise


def init_standard_data():
    """
    Инициализировать базу данных стандартными данными.
    """
    # Инициализируем схему БД
    print("Инициализация схемы базы данных...")
    init_db(drop_all=True)
    print("Схема базы данных создана.")

    # Создаем сессию
    engine = get_database_engine()

    with Session(engine) as session:
        # Проверяем, есть ли уже данные
        statement = select(User)
        existing_users = session.exec(statement).first()
        if existing_users:
            print("База данных уже содержит данные. Пропускаем инициализацию.")
            return

        print("Создание стандартных данных...")

        # Создаем пользователей
        users = [
            User(
                email="admin@example.com",
                password_hash="admin_hash_12345",
                username="Администратор",
                english_level="B2",
                role=UserRole.ADMIN,
                is_active=True
            ),
            User(
                email="user1@example.com",
                password_hash="user1_hash_12345",
                username="Иван Иванов",
                english_level="A2",
                role=UserRole.USER,
                is_active=True
            ),
            User(
                email="user2@example.com",
                password_hash="user2_hash_12345",
                username="Мария Петрова",
                english_level="B1",
                role=UserRole.USER,
                is_active=True
            ),
            User(
                email="maksim.mikheev@gmail.com",
                password_hash="12345678",
                username="Максим Михеев",
                english_level="B2",
                role=UserRole.USER,
                is_active=True
            ),
        ]

        for user in users:
            session.add(user)

        session.commit()
        print(f"Создано {len(users)} пользователей.")

        # Обновляем сессию для получения ID пользователей
        session.refresh(users[0])
        session.refresh(users[1])
        session.refresh(users[2])
        session.refresh(users[3])

        # Создаем балансы для пользователей
        balances = [
            Balance(user_id=users[0].id, balance=Decimal('1000.00')),
            Balance(user_id=users[1].id, balance=Decimal('500.00')),
            Balance(user_id=users[2].id, balance=Decimal('750.00')),
            Balance(user_id=users[3].id, balance=Decimal('100.00')),
        ]

        for balance in balances:
            session.add(balance)

        session.commit()
        print(f"Создано {len(balances)} балансов.")

        # Создаем документы
        documents = [
            TextDocument(
                user_id=users[1].id,
                document_type=DocumentType.TXT,
                content="This is a sample text document for testing purposes. It contains some English text.",
                filename="sample1.txt",
                is_processed=True
            ),
            TextDocument(
                user_id=users[2].id,
                document_type=DocumentType.TXT,
                content="Another sample document with more content. This document is longer and contains multiple sentences.",
                filename="sample2.txt",
                is_processed=False
            ),
            TextDocument(
                user_id=users[3].id,
                document_type=DocumentType.EPUB,
                content="EPUB document content here. This is a longer document with structured content.",
                filename="book.epub",
                is_processed=True
            ),
        ]

        for document in documents:
            session.add(document)

        session.commit()
        print(f"Создано {len(documents)} документов.")

        # Обновляем сессию для получения ID документов
        for doc in documents:
            session.refresh(doc)

        # Создаем задачи
        tasks = [
            Task(
                user_id=users[1].id,
                document_id=documents[0].id,
                status=TaskStatus.COMPLETED
            ),
            Task(
                user_id=users[2].id,
                document_id=documents[1].id,
                status=TaskStatus.PROCESSING
            ),
            Task(
                user_id=users[3].id,
                document_id=documents[2].id,
                status=TaskStatus.COMPLETED
            ),
            Task(
                user_id=users[1].id,
                status=TaskStatus.FAILED,
                error_message="Недостаточно средств на балансе"
            ),
        ]

        for task in tasks:
            session.add(task)

        session.commit()
        print(f"Создано {len(tasks)} задач.")

        # Обновляем сессию для получения ID задач
        for task in tasks:
            session.refresh(task)

        # Создаем транзакции
        transactions = [
            Transaction(
                user_id=users[0].id,
                transaction_type=TransactionType.REPLENISHMENT,
                amount=Decimal('1000.00')
            ),
            Transaction(
                user_id=users[1].id,
                transaction_type=TransactionType.REPLENISHMENT,
                amount=Decimal('500.00')
            ),
            Transaction(
                user_id=users[1].id,
                transaction_type=TransactionType.WITHDRAWAL,
                amount=Decimal('50.00'),
                task_id=tasks[0].id
            ),
            Transaction(
                user_id=users[2].id,
                transaction_type=TransactionType.REPLENISHMENT,
                amount=Decimal('750.00')
            ),
            Transaction(
                user_id=users[3].id,
                transaction_type=TransactionType.REPLENISHMENT,
                amount=Decimal('100.00')
            ),
        ]

        for transaction in transactions:
            session.add(transaction)

        session.commit()
        print(f"Создано {len(transactions)} транзакций.")

        # Создаем предсказания
        predictions = [
            Prediction(
                task_id=tasks[0].id,
                prediction_data={
                    "phrases": [
                        {"english": "This is a sample text document", "russian": "Это пример текстового документа"},
                        {"english": "for testing purposes", "russian": "для целей тестирования"},
                        {"english": "It contains some English text", "russian": "Он содержит некоторый английский текст"}
                    ]
                }
            ),
            Prediction(
                task_id=tasks[2].id,
                prediction_data={
                    "phrases": [
                        {"english": "EPUB document content here", "russian": "Содержимое документа EPUB здесь"},
                        {"english": "This is a longer document", "russian": "Это более длинный документ"},
                        {"english": "with structured content", "russian": "со структурированным содержимым"}
                    ]
                }
            ),
        ]

        for prediction in predictions:
            session.add(prediction)

        session.commit()
        print(f"Создано {len(predictions)} предсказаний.")

        print("\nИнициализация базы данных завершена успешно!")
        print("\nСозданные данные:")
        print(f"  - Пользователей: {len(users)}")
        print(f"  - Балансов: {len(balances)}")
        print(f"  - Документов: {len(documents)}")
        print(f"  - Задач: {len(tasks)}")
        print(f"  - Транзакций: {len(transactions)}")
        print(f"  - Предсказаний: {len(predictions)}")