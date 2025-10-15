from fastapi import APIRouter, Depends, Path, Query
from typing import Annotated
import uuid

from app.dependencies.user_auth import get_current_user
from app.dependencies.permissions import get_user_permission
from app.models.user import User
from app.schemas.user_permission import UserPermissionResponse
from app.schemas.account_document import (
    AccountDocumentCreateRequest,
    AccountDocumentUpdateRequest,
    AccountDocumentResponse,
    AccountDocumentListResponse,
    AccountDocumentDeleteResponse,
)
from app.services.account_document import (
    create_account_document,
    list_account_documents,
    get_account_document,
    update_account_document,
    delete_account_document,
)
from app.utils.logger import logger

router = APIRouter(prefix="/accounts/{account_id}/documents", tags=["account-documents"])

@router.post("/", response_model=AccountDocumentResponse, status_code=201, operation_id="createAccountDocument")
async def create_account_document_route(
    account_id: uuid.UUID = Path(..., description="Account ID"),
    payload: AccountDocumentCreateRequest = ...,
    current_user: Annotated[User, Depends(get_current_user)] = ...,
    user_permission: UserPermissionResponse = Depends(get_user_permission({"accounts": ["view", "edit"]}))
) -> AccountDocumentResponse:
        return await create_account_document(account_id, payload, current_user)

@router.get("/", response_model=AccountDocumentListResponse, operation_id="listAccountDocuments")
async def list_account_documents_route(
    account_id: uuid.UUID = Path(..., description="Account ID"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    current_user: Annotated[User, Depends(get_current_user)] = ...,
    user_permission: UserPermissionResponse = Depends(get_user_permission({"accounts": ["view"]}))
) -> AccountDocumentListResponse:
        return await list_account_documents(account_id, current_user, page, limit)

@router.get("/{document_id}", response_model=AccountDocumentResponse, operation_id="getAccountDocument")
async def get_account_document_route(
    account_id: uuid.UUID = Path(..., description="Account ID"),
    document_id: uuid.UUID = Path(..., description="Document ID"),
    current_user: Annotated[User, Depends(get_current_user)] = ...,
    user_permission: UserPermissionResponse = Depends(get_user_permission({"accounts": ["view"]}))
) -> AccountDocumentResponse:
        return await get_account_document(account_id, document_id, current_user)

@router.put("/{document_id}", response_model=AccountDocumentResponse, operation_id="updateAccountDocument")
async def update_account_document_route(
    account_id: uuid.UUID = Path(..., description="Account ID"),
    document_id: uuid.UUID = Path(..., description="Document ID"),
    payload: AccountDocumentUpdateRequest = ...,
    current_user: Annotated[User, Depends(get_current_user)] = ...,
    user_permission: UserPermissionResponse = Depends(get_user_permission({"accounts": ["view", "edit"]}))
) -> AccountDocumentResponse:
        return await update_account_document(account_id, document_id, payload, current_user)

@router.delete("/{document_id}", response_model=AccountDocumentDeleteResponse, operation_id="deleteAccountDocument")
async def delete_account_document_route(
    account_id: uuid.UUID = Path(..., description="Account ID"),
    document_id: uuid.UUID = Path(..., description="Document ID"),
    current_user: Annotated[User, Depends(get_current_user)] = ...,
    user_permission: UserPermissionResponse = Depends(get_user_permission({"accounts": ["view", "edit", "delete"]}))
) -> AccountDocumentDeleteResponse:
        return await delete_account_document(account_id, document_id, current_user)
