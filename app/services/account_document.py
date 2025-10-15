from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from datetime import datetime
import uuid

from app.models.account_document import AccountDocument
from app.models.account import Account
from app.models.user import User
from app.schemas.account_document import (
    AccountDocumentCreateRequest,
    AccountDocumentUpdateRequest,
    AccountDocumentResponse,
    AccountDocumentListResponse,
    AccountDocumentDeleteResponse,
)
from app.db.session import get_request_transaction
from app.utils.logger import logger

def _normalize_datetime(dt: datetime) -> datetime:

    if dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt

async def _ensure_account_in_org(account_id: uuid.UUID, user: User) -> Account:
    if not user.org_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not in an organization")
    db = get_request_transaction()
    result = await db.execute(select(Account).where(Account.account_id == account_id, Account.org_id == user.org_id))
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found or access denied")
    return account

async def create_account_document(
    account_id: uuid.UUID, payload: AccountDocumentCreateRequest, user: User
) -> AccountDocumentResponse:
    await _ensure_account_in_org(account_id, user)
    db = get_request_transaction()
    
    document = AccountDocument(
        account_id=account_id,
        name=payload.name,
        category=payload.category,
        date=_normalize_datetime(payload.date),
        file_name=payload.file_name,
        file_size=payload.file_size,
        mime_type=payload.mime_type,
        file_path=None,
    )
    db.add(document)
    await db.flush()
    await db.refresh(document)
    logger.info(f"Created account document {document.id} for account {account_id}")
    return AccountDocumentResponse.model_validate(document)

async def list_account_documents(
    account_id: uuid.UUID, user: User, page: int = 1, limit: int = 10
) -> AccountDocumentListResponse:
    await _ensure_account_in_org(account_id, user)
    db = get_request_transaction()
    
    count_result = await db.execute(
        select(func.count(AccountDocument.id)).where(AccountDocument.account_id == account_id)
    )
    total = count_result.scalar() or 0
    
    offset = (page - 1) * limit
    result = await db.execute(
        select(AccountDocument)
        .where(AccountDocument.account_id == account_id)
        .order_by(AccountDocument.date.desc(), AccountDocument.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    documents = result.scalars().all()
    
    logger.info(f"Retrieved {len(documents)} documents for account {account_id} (page {page}, total {total})")
    return AccountDocumentListResponse(
        documents=[AccountDocumentResponse.model_validate(doc) for doc in documents],
        total=total,
        page=page,
        limit=limit,
    )

async def get_account_document(account_id: uuid.UUID, document_id: uuid.UUID, user: User) -> AccountDocumentResponse:
    await _ensure_account_in_org(account_id, user)
    db = get_request_transaction()
    
    result = await db.execute(
        select(AccountDocument).where(AccountDocument.id == document_id, AccountDocument.account_id == account_id)
    )
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    
    logger.info(f"Retrieved document {document_id} for account {account_id}")
    return AccountDocumentResponse.model_validate(document)

async def update_account_document(
    account_id: uuid.UUID, document_id: uuid.UUID, payload: AccountDocumentUpdateRequest, user: User
) -> AccountDocumentResponse:
    await _ensure_account_in_org(account_id, user)
    db = get_request_transaction()
    
    result = await db.execute(
        select(AccountDocument).where(AccountDocument.id == document_id, AccountDocument.account_id == account_id)
    )
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    
    if payload.name is not None:
        document.name = payload.name
    if payload.category is not None:
        document.category = payload.category
    if payload.date is not None:
        document.date = _normalize_datetime(payload.date)
    
    await db.flush()
    await db.refresh(document)
    logger.info(f"Updated document {document_id} for account {account_id}")
    return AccountDocumentResponse.model_validate(document)

async def delete_account_document(account_id: uuid.UUID, document_id: uuid.UUID, user: User) -> AccountDocumentDeleteResponse:
    await _ensure_account_in_org(account_id, user)
    db = get_request_transaction()
    
    result = await db.execute(
        select(AccountDocument).where(AccountDocument.id == document_id, AccountDocument.account_id == account_id)
    )
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    
    await db.delete(document)
    await db.flush()
    
    logger.info(f"Deleted document {document_id} for account {account_id}")
    return AccountDocumentDeleteResponse(id=document_id, message="Document deleted successfully")
