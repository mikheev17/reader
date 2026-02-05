"""Тесты API баланса и транзакций."""

from decimal import Decimal

from fastapi.testclient import TestClient


def test_get_balance(client: TestClient) -> None:
    """Получение баланса текущего пользователя (подменён в фикстуре)."""
    response = client.get("/balance")
    assert response.status_code == 200
    data = response.json()
    assert "balance" in data
    assert "user_id" in data
    assert Decimal(str(data["balance"])) == Decimal("100.00")


def test_replenish_balance(client: TestClient) -> None:
    """Пополнение баланса."""
    response = client.post("/balance/replenish", json={"amount": "50.00"})
    assert response.status_code == 200
    data = response.json()
    assert Decimal(str(data["balance"])) == Decimal("150.00")

    # Ещё пополнение
    response2 = client.post("/balance/replenish", json={"amount": "25.50"})
    assert response2.status_code == 200
    assert Decimal(str(response2.json()["balance"])) == Decimal("175.50")


def test_get_transactions(client: TestClient) -> None:
    """История транзакций изначально пуста (после создания пользователя баланс создан без транзакции в тестах)."""
    response = client.get("/transactions")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_replenish_and_transactions(client: TestClient) -> None:
    """После пополнения в истории появляется транзакция replenishment."""
    client.post("/balance/replenish", json={"amount": "10.00"})
    response = client.get("/transactions")
    assert response.status_code == 200
    transactions = response.json()
    assert len(transactions) >= 1
    replenishments = [t for t in transactions if t.get("transaction_type") == "replenishment"]
    assert len(replenishments) >= 1
    assert any(Decimal(str(t["amount"])) == Decimal("10.00") for t in replenishments)
