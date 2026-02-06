"""Тесты API задач и предсказаний."""

from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient


def test_create_task_deduction(client: TestClient) -> None:
    """Создание задачи списывает кредиты с баланса (фиксированная стоимость задачи)."""
    # Баланс из фикстуры 100.00
    balance_before = client.get("/balance").json()
    bal_before = Decimal(str(balance_before["balance"]))

    response = client.post("/tasks", json={})
    assert response.status_code == 201
    task = response.json()
    assert task["status"] == "PENDING"
    assert "id" in task

    balance_after = client.get("/balance").json()
    bal_after = Decimal(str(balance_after["balance"]))
    # Стоимость создания задачи = 10.00
    assert bal_after == bal_before - Decimal("10.00")


def test_transactions_after_task(client: TestClient) -> None:
    """После создания задачи в истории есть транзакция withdrawal."""
    client.post("/tasks", json={})
    response = client.get("/transactions")
    assert response.status_code == 200
    transactions = response.json()
    withdrawals = [t for t in transactions if t.get("transaction_type") == "withdrawal"]
    assert len(withdrawals) >= 1
    assert any(Decimal(str(t["amount"])) == Decimal("10.00") for t in withdrawals)


def test_create_task_insufficient_balance(client: TestClient) -> None:
    """При недостаточном балансе создание задачи возвращает 402."""
    # Списываем почти весь баланс пополнениями и одной задачей, затем ещё задачи
    client.post("/balance/replenish", json={"amount": "0.01"})  # 100.01
    for _ in range(10):
        client.post("/tasks", json={})  # 10 * 10 = 100
    # Баланс ~0.01
    response = client.post("/tasks", json={})
    assert response.status_code == 402
    assert "Недостаточно" in response.json().get("detail", "")


def test_get_tasks_list(client: TestClient) -> None:
    """Список задач: изначально пуст, после создания задачи — содержит задачу."""
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []

    client.post("/tasks", json={})
    response = client.get("/tasks")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["status"] == "PENDING"
    assert "id" in tasks[0]


def test_get_task_by_id(client: TestClient) -> None:
    """Получение задачи по ID."""
    create = client.post("/tasks", json={})
    assert create.status_code == 201
    task_id = create.json()["id"]

    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["status"] == "PENDING"


def test_get_task_by_id_404(client: TestClient) -> None:
    """Несуществующий ID задачи — 404."""
    fake_id = uuid4()
    response = client.get(f"/tasks/{fake_id}")
    assert response.status_code == 404
    detail = response.json().get("detail", "").lower()
    assert "не найдена" in detail or "not found" in detail


def test_get_predictions_empty(client: TestClient) -> None:
    """История предсказаний без предсказаний — пустой список."""
    response = client.get("/predictions")
    assert response.status_code == 200
    assert response.json() == []


def test_get_task_prediction_404(client: TestClient) -> None:
    """Предсказание по задаче ещё не готово — 404."""
    create = client.post("/tasks", json={})
    assert create.status_code == 201
    task_id = create.json()["id"]

    response = client.get(f"/tasks/{task_id}/prediction")
    assert response.status_code == 404
    detail = response.json().get("detail", "")
    assert "не готов" in detail or "not found" in detail.lower()
