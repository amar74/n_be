from fastapi import APIRouter, Depends, Path, Query
from typing import Annotated
import uuid
from app.dependencies.user_auth import get_current_user
from app.dependencies.permissions import get_user_permission
from app.models.user import User
from app.schemas.user_permission import UserPermissionResponse
from app.schemas.account_note import (
    AccountNoteCreateRequest,
    AccountNoteUpdateRequest,
    AccountNoteResponse,
    AccountNoteListResponse,
    AccountNoteDeleteResponse,
)
from app.services.account_note import (
    create_account_note,
    list_account_notes,
    get_account_note,
    update_account_note,
    delete_account_note,
)
from app.utils.logger import logger

router = APIRouter(prefix="/accounts/{account_id}/notes", tags=["account-notes"])

@router.post("/", response_model=AccountNoteResponse, status_code=201, operation_id="createAccountNote")
async def create_account_note_route(
    account_id: uuid.UUID = Path(..., description="Account ID"),
    payload: AccountNoteCreateRequest = ...,
    current_user: Annotated[User, Depends(get_current_user)] = ...,
    user_permission: UserPermissionResponse = Depends(get_user_permission({"accounts": ["view", "edit"]}))
) -> AccountNoteResponse:
        return await create_account_note(account_id, payload, current_user)

@router.get("/", response_model=AccountNoteListResponse, operation_id="listAccountNotes")
async def list_account_notes_route(
    account_id: uuid.UUID = Path(..., description="Account ID"),
    current_user: Annotated[User, Depends(get_current_user)] = ...,
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    user_permission: UserPermissionResponse = Depends(get_user_permission({"accounts": ["view"]}))
) -> AccountNoteListResponse:
        return await list_account_notes(account_id, current_user, page=page, limit=limit)

@router.get("/{note_id}", response_model=AccountNoteResponse, operation_id="getAccountNote")
async def get_account_note_route(
    account_id: uuid.UUID = Path(..., description="Account ID"),
    note_id: uuid.UUID = Path(..., description="Note ID"),
    current_user: Annotated[User, Depends(get_current_user)] = ...,
    user_permission: UserPermissionResponse = Depends(get_user_permission({"accounts": ["view"]}))
) -> AccountNoteResponse:
        return await get_account_note(account_id, note_id, current_user)

@router.put("/{note_id}", response_model=AccountNoteResponse, operation_id="updateAccountNote")
async def update_account_note_route(
    account_id: uuid.UUID = Path(..., description="Account ID"),
    note_id: uuid.UUID = Path(..., description="Note ID"),
    payload: AccountNoteUpdateRequest = ...,
    current_user: Annotated[User, Depends(get_current_user)] = ...,
    user_permission: UserPermissionResponse = Depends(get_user_permission({"accounts": ["view", "edit"]}))
) -> AccountNoteResponse:
        return await update_account_note(account_id, note_id, payload, current_user)

@router.delete("/{note_id}", response_model=AccountNoteDeleteResponse, operation_id="deleteAccountNote")
async def delete_account_note_route(
    account_id: uuid.UUID = Path(..., description="Account ID"),
    note_id: uuid.UUID = Path(..., description="Note ID"),
    current_user: Annotated[User, Depends(get_current_user)] = ...,
    user_permission: UserPermissionResponse = Depends(get_user_permission({"accounts": ["view", "edit", "delete"]}))
) -> AccountNoteDeleteResponse:
        return await delete_account_note(account_id, note_id, current_user)

