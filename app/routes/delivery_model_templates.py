from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.db.session import get_request_transaction
from app.dependencies.permissions import get_user_permission
from app.dependencies.user_auth import get_current_user
from app.models.user import User
from app.schemas.delivery_model_template import (
    DeliveryModelTemplateCreate,
    DeliveryModelTemplateUpdate,
    DeliveryModelTemplateResponse,
)
from app.schemas.user_permission import UserPermissionResponse
from app.services.delivery_model_template_service import DeliveryModelTemplateService


router = APIRouter(prefix="/delivery-models", tags=["Delivery Models"])


def _require_org(user: User) -> UUID:
    if not user.org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with an organization.",
        )
    return user.org_id


@router.get("/", response_model=list[DeliveryModelTemplateResponse])
async def list_delivery_models(
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["read"]})),
):
    org_id = _require_org(current_user)
    service = DeliveryModelTemplateService(db)
    return await service.list_templates(org_id)


@router.post("/", response_model=DeliveryModelTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_delivery_model(
    payload: DeliveryModelTemplateCreate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["create"]})),
):
    org_id = _require_org(current_user)
    service = DeliveryModelTemplateService(db)
    return await service.create_template(org_id, current_user.id, payload)


@router.get("/{template_id}", response_model=DeliveryModelTemplateResponse)
async def get_delivery_model(
    template_id: UUID,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["read"]})),
):
    org_id = _require_org(current_user)
    service = DeliveryModelTemplateService(db)
    template = await service.get_template(template_id, org_id)
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delivery model not found.")
    return template


@router.put("/{template_id}", response_model=DeliveryModelTemplateResponse)
async def update_delivery_model(
    template_id: UUID,
    payload: DeliveryModelTemplateUpdate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["update"]})),
):
    org_id = _require_org(current_user)
    service = DeliveryModelTemplateService(db)
    template = await service.update_template(template_id, org_id, payload)
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delivery model not found.")
    return template


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_delivery_model(
    template_id: UUID,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["delete"]})),
):
    org_id = _require_org(current_user)
    service = DeliveryModelTemplateService(db)
    success = await service.delete_template(template_id, org_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delivery model not found.")

