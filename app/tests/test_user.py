"""Тесты API пользователей (список пользователей, права доступа)."""

from fastapi.testclient import TestClient


def test_get_users_forbidden_for_regular_user(client: TestClient) -> None:
    """GET /users для обычного пользователя — 403."""
    response = client.get("/users")
    assert response.status_code == 403
    detail = response.json().get("detail", "")
    assert "admin" in detail.lower() or "Admin" in detail


def test_get_users_as_admin(client_admin: TestClient) -> None:
    """GET /users для админа — 200 и список пользователей."""
    response = client_admin.get("/users")
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
    assert any(u.get("email") == "admin@test.ru" for u in users)
