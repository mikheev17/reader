"""Тесты health-check endpoint."""

from fastapi.testclient import TestClient


def test_health(client: TestClient) -> None:
    """Проверка health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
