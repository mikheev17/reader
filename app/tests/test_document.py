"""Тесты API документов."""

from unittest.mock import patch
from uuid import uuid4

from fastapi.testclient import TestClient


@patch("routers.document.send_task")
def test_upload_document(mock_send_task, client: TestClient) -> None:
    """Загрузка документа: файл с латиницей, создаётся документ и задача."""
    file_content = b"Hello world. Simple text for test."
    response = client.post(
        "/documents",
        files={"file": ("test.txt", file_content, "text/plain")},
        data={},
    )
    assert response.status_code == 201
    data = response.json()
    assert "document" in data
    assert data["document"]["document_type"] == "txt"
    assert data["document"]["content_length"] == len("Hello world. Simple text for test.")
    assert "task_id" in data
    assert data["task_status"] == "PENDING"
    mock_send_task.assert_called_once()


@patch("routers.document.send_task")
def test_list_documents(mock_send_task, client: TestClient) -> None:
    """После загрузки документа GET /documents возвращает его в списке."""
    client.post(
        "/documents",
        files={"file": ("doc.txt", b"Some latin content here.", "text/plain")},
        data={},
    )
    response = client.get("/documents")
    assert response.status_code == 200
    docs = response.json()
    assert len(docs) >= 1
    assert any(d["filename"] == "doc.txt" for d in docs)


@patch("routers.document.send_task")
def test_get_document_by_id(mock_send_task, client: TestClient) -> None:
    """Получение документа по ID возвращает content."""
    client.post(
        "/documents",
        files={"file": ("my.txt", b"Secret latin text.", "text/plain")},
        data={},
    )
    list_resp = client.get("/documents")
    assert list_resp.status_code == 200
    doc_id = list_resp.json()[0]["id"]

    response = client.get(f"/documents/{doc_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "Secret latin text."
    assert data["filename"] == "my.txt"


def test_get_document_404(client: TestClient) -> None:
    """Несуществующий ID документа — 404."""
    fake_id = uuid4()
    response = client.get(f"/documents/{fake_id}")
    assert response.status_code == 404


@patch("routers.document.send_task")
def test_upload_document_empty_file(mock_send_task, client: TestClient) -> None:
    """Пустой файл — 400."""
    response = client.post(
        "/documents",
        files={"file": ("empty.txt", b"", "text/plain")},
        data={},
    )
    assert response.status_code == 400
    assert "пуст" in response.json().get("detail", "").lower()


@patch("routers.document.send_task")
def test_upload_document_no_latin(mock_send_task, client: TestClient) -> None:
    """Файл только с кириллицей (после удаления не-латиницы content пуст) — 400."""
    response = client.post(
        "/documents",
        files={"file": ("cyrillic.txt", "Приветмир".encode("utf-8"), "text/plain")},
        data={},
    )
    assert response.status_code == 400
    assert "латин" in response.json().get("detail", "").lower()
