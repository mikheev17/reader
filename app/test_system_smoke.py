from __future__ import annotations

"""
Сценарий для проверки работоспособности системы (success path):
- создание пользователя
- создание/получение баланса
- пополнение баланса
- загрузка документа
- создание задачи на обработку
- получение предсказания

Запуск (из корня проекта):
    python test_system_smoke.py

Требования:
- в файле app/.env должны быть корректно заполнены переменные подключения к БД
"""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlmodel import Session

from database.database import get_database_engine
from models import User, Balance, TextDocument, DocumentType, TaskStatus
from services.crud.user import get_user_by_email, create_user
from services.crud.balance import get_balance_by_user_id, create_balance
from services.balance_service import replenish as balance_replenish
from services.crud.document import create_document
from services.document_service import send_document_for_processing
from services.task_service import create_task_with_balance_deduction, TASK_CREATION_COST
from services.crud.task import complete_task_with_prediction, get_task_by_id
from services.crud.prediction import get_predictions_by_task_id


def create_test_user(session: Session) -> User:
    unique_email = f"test_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}@example.com"
    user = User(
        email=unique_email,
        password_hash="test_hash",
        username="Smoke Test User",
        english_level="A2",
    )
    existing = get_user_by_email(unique_email, session)
    if existing:
        return existing
    return create_user(user, session)


def ensure_balance(user_id: UUID, session: Session) -> Balance:
    bal = get_balance_by_user_id(user_id, session)
    if bal:
        return bal
    bal = Balance(user_id=user_id)
    return create_balance(bal, session)


def test() -> None:
    engine = get_database_engine()
    with Session(engine) as session:
        print("=== SMOKE TEST START ===")
        print("Проверка success path: пользователь -> документ -> задача -> предсказание\n")

        # 1) Создание пользователя
        user = create_test_user(session)
        print(f"✓ Создан пользователь: id={user.id}, email={user.email}")

        # 2) Создание/получение баланса
        bal = ensure_balance(user.id, session)
        print(f"✓ Начальный баланс: {bal.balance}")

        # 3) Пополнение баланса (необходимо для создания задачи)
        replenish_amount = Decimal("100.00")
        balance = balance_replenish(user.id, replenish_amount, session)
        assert balance is not None, "Пополнение баланса должно быть успешным"
        bal = get_balance_by_user_id(user.id, session)
        print(f"✓ Пополнение баланса: +{replenish_amount} -> баланс: {bal.balance}")

        # 4) Загрузка документа
        document_content = "This is a test document for smoke testing. It contains some English text to process."
        document = TextDocument(
            user_id=user.id,
            document_type=DocumentType.TXT,
            content=document_content,
            filename="test_document.txt"
        )
        document = create_document(document, session)
        print(f"✓ Загружен документ: id={document.id}, filename={document.filename}, content_length={len(document.content)}")

        # 5) Создание задачи на обработку документа
        processing_cost = Decimal("10.00")
        task = send_document_for_processing(document.id, processing_cost, session)
        assert task is not None, "Задача должна быть создана успешно"
        assert task.status == TaskStatus.PENDING, f"Статус задачи должен быть PENDING, получен {task.status}"
        print(f"✓ Создана задача: id={task.id}, status={task.status}, document_id={task.document_id}")
        
        # Проверяем, что баланс был списан
        bal = get_balance_by_user_id(user.id, session)
        expected_balance = (replenish_amount - processing_cost).quantize(Decimal("0.01"))
        actual_balance = Decimal(bal.balance).quantize(Decimal("0.01"))
        assert actual_balance == expected_balance, f"Ожидался баланс {expected_balance}, фактически {actual_balance}"
        print(f"✓ Баланс после списания: {bal.balance}")

        # 6) Получение предсказания (завершение задачи)
        prediction_data = {
            "phrases": [
                {"english": "smoke testing", "russian": "Смоук-тестирование"},
                {"english": "contains", "russian": "содержит"}
            ]
        }
        prediction = complete_task_with_prediction(task.id, prediction_data, session)
        assert prediction is not None, "Предсказание должно быть создано успешно"
        print(f"✓ Создано предсказание: id={prediction.id}, task_id={prediction.task_id}")
        print(f"  Данные предсказания: {prediction.prediction_data}")

        # Проверяем, что задача завершена
        task = get_task_by_id(task.id, session)
        assert task.status == TaskStatus.COMPLETED, f"Статус задачи должен быть COMPLETED, получен {task.status}"
        print(f"✓ Задача завершена: status={task.status}")

        # Проверяем, что документ помечен как обработанный
        from services.crud.document import get_document_by_id
        document = get_document_by_id(document.id, session)
        assert document.is_processed, "Документ должен быть помечен как обработанный"
        print(f"✓ Документ помечен как обработанный: is_processed={document.is_processed}")

        # Проверяем получение предсказания по task_id
        predictions = get_predictions_by_task_id(task.id, session)
        assert len(predictions) > 0, "Должно быть хотя бы одно предсказание для задачи"
        print(f"✓ Получено предсказаний для задачи: {len(predictions)}")

        # 7) Тест прямого создания задачи через task_service с автоматическим списанием баланса
        print("\n--- Тест прямого создания задачи с автоматическим списанием баланса ---")
        bal_before = get_balance_by_user_id(user.id, session)
        balance_before = Decimal(bal_before.balance)
        print(f"Баланс перед созданием задачи: {balance_before}")
        
        # Создаем задачу напрямую через task_service
        task2 = create_task_with_balance_deduction(
            user_id=user.id,
            session=session,
            document_id=None,
            task_cost=None  # Используется фиксированная стоимость TASK_CREATION_COST
        )
        assert task2 is not None, "Задача должна быть создана успешно"
        assert task2.status == TaskStatus.PENDING, f"Статус задачи должен быть PENDING, получен {task2.status}"
        print(f"✓ Создана задача напрямую: id={task2.id}, status={task2.status}")
        
        # Проверяем, что баланс был списан на фиксированную сумму
        bal_after = get_balance_by_user_id(user.id, session)
        balance_after = Decimal(bal_after.balance)
        expected_balance_after = (balance_before - TASK_CREATION_COST).quantize(Decimal("0.01"))
        actual_balance_after = balance_after.quantize(Decimal("0.01"))
        assert actual_balance_after == expected_balance_after, \
            f"Ожидался баланс {expected_balance_after}, фактически {actual_balance_after}"
        print(f"✓ Баланс после создания задачи: {balance_after} (списано {TASK_CREATION_COST})")

        print("\n=== SMOKE TEST OK ===")
        print("Все этапы success path выполнены успешно!")