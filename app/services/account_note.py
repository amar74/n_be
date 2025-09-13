from datetime import datetime
import uuid
from typing import List

from sqlalchemy import select, func

from app.models.account import Account
from app.models.account_note import AccountNote
from app.models.user import User
from app.schemas.account_note import (
    AccountNoteCreateRequest,
    AccountNoteUpdateRequest,
    AccountNoteResponse,
    AccountNoteListResponse,
    AccountNoteDeleteResponse,
)
from app.db.session import get_request_transaction
from app.utils.error import MegapolisHTTPException
from app.utils.logger import logger


def _normalize_datetime(dt: datetime) -> datetime:
    if dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt


async def _ensure_account_in_org(account_id: uuid.UUID, user: User) -> Account:
    if not user.org_id:
        raise MegapolisHTTPException(status_code=403, message="Access denied", details="User not in an organization")
    db = get_request_transaction()
    stmt = select(Account).where(Account.account_id == account_id, Account.org_id == user.org_id)
    result = await db.execute(stmt)
    account = result.scalar_one_or_none()
    if not account:
        raise MegapolisHTTPException(status_code=404, message="Not found", details="Account not found or access denied")
    return account


async def create_account_note(account_id: uuid.UUID, payload: AccountNoteCreateRequest, user: User) -> AccountNoteResponse:
    await _ensure_account_in_org(account_id, user)
    db = get_request_transaction()
    note = AccountNote(
        account_id=account_id,
        title=payload.title,
        content=payload.content,
        date=_normalize_datetime(payload.date),
    )
    db.add(note)
    await db.flush()
    await db.refresh(note)
    logger.info(f"Created account note {note.id} for account {account_id}")
    return AccountNoteResponse.model_validate(note)


async def list_account_notes(account_id: uuid.UUID, user: User, page: int = 1, limit: int = 10) -> AccountNoteListResponse:
    await _ensure_account_in_org(account_id, user)
    db = get_request_transaction()
    offset = (page - 1) * limit
    stmt = (
        select(AccountNote)
        .where(AccountNote.account_id == account_id)
        .order_by(AccountNote.date.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(stmt)
    notes: List[AccountNote] = list(result.scalars().all())

    count_stmt = select(func.count(AccountNote.id)).where(AccountNote.account_id == account_id)
    count_result = await db.execute(count_stmt)
    total_count = count_result.scalar() or 0

    total_pages = (total_count + limit - 1) // limit
    has_next = page < total_pages
    has_prev = page > 1

    return AccountNoteListResponse(
        notes=[AccountNoteResponse.model_validate(n) for n in notes],
        total_count=total_count,
        page=page,
        limit=limit,
        total_pages=total_pages,
        has_next=has_next,
        has_prev=has_prev,
    )


async def get_account_note(account_id: uuid.UUID, note_id: uuid.UUID, user: User) -> AccountNoteResponse:
    await _ensure_account_in_org(account_id, user)
    db = get_request_transaction()
    stmt = select(AccountNote).where(AccountNote.id == note_id, AccountNote.account_id == account_id)
    result = await db.execute(stmt)
    note = result.scalar_one_or_none()
    if not note:
        raise MegapolisHTTPException(status_code=404, message="Not found", details="Note not found")
    return AccountNoteResponse.model_validate(note)


async def update_account_note(account_id: uuid.UUID, note_id: uuid.UUID, payload: AccountNoteUpdateRequest, user: User) -> AccountNoteResponse:
    await _ensure_account_in_org(account_id, user)
    db = get_request_transaction()
    stmt = select(AccountNote).where(AccountNote.id == note_id, AccountNote.account_id == account_id)
    result = await db.execute(stmt)
    note = result.scalar_one_or_none()
    if not note:
        raise MegapolisHTTPException(status_code=404, message="Not found", details="Note not found")

    update_data = payload.model_dump(exclude_unset=True)
    if "date" in update_data and update_data["date"] is not None:
        update_data["date"] = _normalize_datetime(update_data["date"])
    for field, value in update_data.items():
        setattr(note, field, value)

    await db.flush()
    await db.refresh(note)
    return AccountNoteResponse.model_validate(note)


async def delete_account_note(account_id: uuid.UUID, note_id: uuid.UUID, user: User) -> AccountNoteDeleteResponse:
    await _ensure_account_in_org(account_id, user)
    db = get_request_transaction()
    stmt = select(AccountNote).where(AccountNote.id == note_id, AccountNote.account_id == account_id)
    result = await db.execute(stmt)
    note = result.scalar_one_or_none()
    if not note:
        raise MegapolisHTTPException(status_code=404, message="Not found", details="Note not found")
    await db.delete(note)
    return AccountNoteDeleteResponse(id=note_id, message="Note deleted successfully")


