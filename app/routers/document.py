"""
Роутер для работы с документами.
"""

import logging
import re
from typing import Optional

from database.database import get_session
from dto import CreateDocumentResponse, DocumentResponse
from fastapi import APIRouter, HTTPException, status, Depends, File, Form, UploadFile
from models import TextDocument, DocumentType
from models import User
from services.auth.auth import get_current_user
from services.crud.document import create_document as crud_create_document
from services.task_service import create_task_with_balance_deduction, TASK_CREATION_COST

from services.rm.rm import send_task

logger = logging.getLogger(__name__)

document_route = APIRouter()


def _parse_document_type(value: str) -> DocumentType:
    """Преобразовать строку в DocumentType."""
    v = value.lower()
    if v == "txt":
        return DocumentType.TXT
    if v == "epub":
        return DocumentType.EPUB
    raise ValueError(f"Неподдерживаемый тип документа: {value}. Допустимы: txt, epub")


def _document_type_from_filename(filename: Optional[str]) -> DocumentType:
    """Определить тип документа по расширению имени файла."""
    if not filename or "." not in filename:
        return DocumentType.TXT
    ext = filename.rsplit(".", 1)[-1].lower()
    if ext == "epub":
        return DocumentType.EPUB
    return DocumentType.TXT


@document_route.post(
    "/documents",
    response_model=CreateDocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать документ и задачу на его обработку",
    description="Принимает файл в бинарном виде. При обработке из байтов извлекается латиница и сохраняется в content."
)
async def create_document(
    session=Depends(get_session),
    current_user: User = Depends(get_current_user),
    file: UploadFile = File(..., description="Файл документа (бинарная отправка)"),
    document_type: Optional[str] = Form(None, description="Тип документа: txt или epub (опционально, по умолчанию из расширения файла)"),
) -> CreateDocumentResponse:
    """
    Создать документ и задачу для его обработки. Требуется JWT. user_id берётся из токена.

    Документ передаётся бинарно (файл). При сохранении из содержимого извлекаются
    только латинские символы (и допустимая пунктуация/пробелы) и записываются в поле content.

    Далее создаётся задача на обработку с списанием стоимости с баланса пользователя.

    Args:
        session: Сессия БД
        current_user: Текущий пользователь (из JWT)
        file: Загружаемый файл (бинарно)
        document_type: txt или epub (если не задано — определяется по расширению файла)

    Returns:
        CreateDocumentResponse: Созданный документ и задача

    Raises:
        HTTPException: При неверном типе документа или недостатке средств
    """
    uid = current_user.id

    if document_type is not None:
        try:
            doc_type = _parse_document_type(document_type)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    else:
        doc_type = _document_type_from_filename(file.filename)

    raw = await file.read()
    if not raw:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Файл пуст",
        )

    decoded = raw.decode("utf-8", errors="ignore")
    content = re.sub(r"[^a-zA-Z\s.,;:!?()\-'\"\n\r\t]", "", decoded).strip()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="В файле не найдено латинских символов для поля content",
        )

    doc = TextDocument(
        user_id=uid,
        document_type=doc_type,
        content=content,
        filename=file.filename or None,
    )
    validation = doc.validate()
    if not validation.is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"validation_errors": [e.message for e in validation.errors]},
        )

    doc = crud_create_document(doc, session)
    logger.info(f"Document created: id={doc.id}, user_id={doc.user_id}")

    task = create_task_with_balance_deduction(
        user_id=uid,
        session=session,
        document_id=doc.id,
        task_cost=TASK_CREATION_COST,
    )

    if task is None:
        logger.warning(f"Document {doc.id} created, but task creation failed for user {uid}: insufficient balance")
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Документ создан, но недостаточно средств на балансе для создания задачи на обработку. "
                   "Создайте задачу позже через POST /tasks с document_id.",
        )

    logger.info(f"Task created for document: task_id={task.id}, document_id={doc.id}")

    send_task(str(task.id))
    logger.info(f"Task sent to worker: task_id={task.id}")

    return CreateDocumentResponse(
        document=DocumentResponse(
            id=doc.id,
            user_id=doc.user_id,
            document_type=doc.document_type.value,
            filename=doc.filename,
            is_processed=doc.is_processed,
            content_length=len(doc.content),
            created_at=doc.created_at.isoformat(),
            updated_at=doc.updated_at.isoformat(),
        ),
        task_id=task.id,
        task_status=task.status.value,
    )
