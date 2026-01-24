from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select

from models import TextDocument


def get_all_documents(session: Session) -> List[TextDocument]:
    statement = select(TextDocument)
    return session.exec(statement).all()


def get_document_by_id(document_id: UUID, session: Session) -> Optional[TextDocument]:
    return session.get(TextDocument, document_id)


def get_documents_by_user_id(user_id: UUID, session: Session) -> List[TextDocument]:
    statement = select(TextDocument).where(TextDocument.user_id == user_id)
    return session.exec(statement).all()


def create_document(document: TextDocument, session: Session) -> TextDocument:
    try:
        session.add(document)
        session.commit()
        session.refresh(document)
        return document
    except Exception:
        session.rollback()
        raise


def delete_document(document_id: UUID, session: Session) -> bool:
    try:
        doc = session.get(TextDocument, document_id)
        if doc:
            session.delete(doc)
            session.commit()
            return True
        return False
    except Exception:
        session.rollback()
        raise
