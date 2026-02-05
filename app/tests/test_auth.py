"""Тесты API аутентификации: регистрация, вход, выход."""

from fastapi.testclient import TestClient


def test_signup_and_signin_flow(client: TestClient) -> None:
    """Регистрация нового пользователя и вход (form data)."""
    # Регистрация (форма требует confirm-password и terms)
    response = client.post(
        "/signup",
        data={
            "name": "New User",
            "email": "newuser@test.ru",
            "password": "securepass123",
            "confirm-password": "securepass123",
            "terms": "on",
        },
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert response.headers.get("location") == "/signin"

    # Вход
    response_login = client.post(
        "/signin",
        data={"email": "newuser@test.ru", "password": "securepass123"},
        follow_redirects=False,
    )
    assert response_login.status_code == 302
    assert response_login.headers.get("location") == "/dashboard"


def test_logout(client: TestClient) -> None:
    """GET /logout — редирект на /signin."""
    response = client.get("/logout", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers.get("location") == "/signin"
