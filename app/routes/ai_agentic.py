from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uuid

from app.db.session import get_request_transaction
from app.dependencies.user_auth import get_current_user, AuthUserResponse
from app.dependencies.permissions import get_user_permission
from app.schemas.ai_agentic import (
    AIAgenticTemplateCreate,
    AIAgenticTemplateUpdate,
    AIAgenticTemplateResponse,
    AIAgenticTemplateListResponse
)
from app.services.ai_agentic_service import AIAgenticService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/ai-agentic", tags=["AI Agentic"])


@router.get("/templates", response_model=AIAgenticTemplateListResponse)
async def get_templates(
    category: Optional[str] = Query(None),
    module: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    include_inactive: bool = Query(False),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: AuthUserResponse = Depends(get_current_user),
):
    try:
        org_id = getattr(current_user, 'org_id', None)
        if org_id:
            org_id = uuid.UUID(str(org_id))
        
        templates = await AIAgenticService.get_all(
            db=db,
            org_id=org_id,
            category=category,
            module=module,
            is_active=is_active,
            include_inactive=include_inactive
        )
        
        # Convert templates to response format
        template_responses = []
        for template in templates:
            template_responses.append(AIAgenticTemplateResponse(
                id=template.id,
                name=template.name,
                description=template.description,
                category=template.category,
                tags=template.tags or [],
                assigned_modules=template.assigned_modules or [],
                system_prompt=template.system_prompt,
                welcome_message=template.welcome_message,
                quick_actions=template.quick_actions if template.quick_actions else None,
                is_active=template.is_active,
                is_default=template.is_default,
                display_order=template.display_order,
                org_id=str(template.org_id) if template.org_id else None,
                created_by=str(template.created_by) if template.created_by else None,
                created_at=template.created_at,
                updated_at=template.updated_at,
            ))
        
        return AIAgenticTemplateListResponse(
            templates=template_responses,
            total=len(template_responses)
        )
    except Exception as e:
        import traceback
        logger.error(f"Error fetching AI Agentic templates: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch templates: {str(e)}"
        )


@router.get("/templates/by-module/{module}", response_model=AIAgenticTemplateListResponse)
async def get_templates_by_module(
    module: str,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: AuthUserResponse = Depends(get_current_user),
):
    try:
        org_id = getattr(current_user, 'org_id', None)
        if org_id:
            org_id = uuid.UUID(str(org_id))
        
        templates = await AIAgenticService.get_by_module(
            db=db,
            module=module,
            org_id=org_id
        )
        
        # Convert templates to response format
        template_responses = []
        for template in templates:
            template_responses.append(AIAgenticTemplateResponse(
                id=template.id,
                name=template.name,
                description=template.description,
                category=template.category,
                tags=template.tags or [],
                assigned_modules=template.assigned_modules or [],
                system_prompt=template.system_prompt,
                welcome_message=template.welcome_message,
                quick_actions=template.quick_actions if template.quick_actions else None,
                is_active=template.is_active,
                is_default=template.is_default,
                display_order=template.display_order,
                org_id=str(template.org_id) if template.org_id else None,
                created_by=str(template.created_by) if template.created_by else None,
                created_at=template.created_at,
                updated_at=template.updated_at,
            ))
        
        return AIAgenticTemplateListResponse(
            templates=template_responses,
            total=len(template_responses)
        )
    except Exception as e:
        import traceback
        logger.error(f"Error fetching AI Agentic templates by module {module}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch templates by module: {str(e)}"
        )


@router.get("/templates/{template_id}", response_model=AIAgenticTemplateResponse)
async def get_template(
    template_id: int,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: AuthUserResponse = Depends(get_current_user),
):
    org_id = getattr(current_user, 'org_id', None)
    if org_id:
        org_id = uuid.UUID(str(org_id))
    
    template = await AIAgenticService.get_by_id(db, template_id, org_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    # Convert to response format
    response_data = AIAgenticTemplateResponse(
        id=template.id,
        name=template.name,
        description=template.description,
        category=template.category,
        tags=template.tags or [],
        assigned_modules=template.assigned_modules or [],
        system_prompt=template.system_prompt,
        welcome_message=template.welcome_message,
        quick_actions=template.quick_actions if template.quick_actions else None,
        is_active=template.is_active,
        is_default=template.is_default,
        display_order=template.display_order,
        org_id=str(template.org_id) if template.org_id else None,
        created_by=str(template.created_by) if template.created_by else None,
        created_at=template.created_at,
        updated_at=template.updated_at,
    )
    
    return response_data


@router.post("/templates", response_model=AIAgenticTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: AIAgenticTemplateCreate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: AuthUserResponse = Depends(get_current_user),
    _ = Depends(get_user_permission({"ai_agentic": ["create"]})),
):
    try:
        org_id = getattr(current_user, 'org_id', None)
        user_id = getattr(current_user, 'id', None)
        
        if org_id:
            org_id = uuid.UUID(str(org_id))
        if user_id:
            user_id = uuid.UUID(str(user_id))
        
        template = await AIAgenticService.create(
            db=db,
            template_data=template_data,
            org_id=org_id,
            user_id=user_id
        )
        
        # Convert to response format
        response_data = AIAgenticTemplateResponse(
            id=template.id,
            name=template.name,
            description=template.description,
            category=template.category,
            tags=template.tags or [],
            assigned_modules=template.assigned_modules or [],
            system_prompt=template.system_prompt,
            welcome_message=template.welcome_message,
            quick_actions=template.quick_actions if template.quick_actions else None,
            is_active=template.is_active,
            is_default=template.is_default,
            display_order=template.display_order,
            org_id=str(template.org_id) if template.org_id else None,
            created_by=str(template.created_by) if template.created_by else None,
            created_at=template.created_at,
            updated_at=template.updated_at,
        )
        
        return response_data
    except Exception as e:
        import traceback
        logger.error(f"Error creating AI Agentic template: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create template: {str(e)}"
        )


@router.put("/templates/{template_id}", response_model=AIAgenticTemplateResponse)
async def update_template(
    template_id: int,
    template_data: AIAgenticTemplateUpdate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: AuthUserResponse = Depends(get_current_user),
    _ = Depends(get_user_permission({"ai_agentic": ["edit"]})),
):
    try:
        org_id = getattr(current_user, 'org_id', None)
        if org_id:
            org_id = uuid.UUID(str(org_id))
        
        template = await AIAgenticService.update(
            db=db,
            template_id=template_id,
            template_data=template_data,
            org_id=org_id
        )
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        # Convert to response format
        response_data = AIAgenticTemplateResponse(
            id=template.id,
            name=template.name,
            description=template.description,
            category=template.category,
            tags=template.tags or [],
            assigned_modules=template.assigned_modules or [],
            system_prompt=template.system_prompt,
            welcome_message=template.welcome_message,
            quick_actions=template.quick_actions if template.quick_actions else None,
            is_active=template.is_active,
            is_default=template.is_default,
            display_order=template.display_order,
            org_id=str(template.org_id) if template.org_id else None,
            created_by=str(template.created_by) if template.created_by else None,
            created_at=template.created_at,
            updated_at=template.updated_at,
        )
        
        return response_data
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        logger.error(f"Error updating AI Agentic template: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update template: {str(e)}"
        )


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: int,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: AuthUserResponse = Depends(get_current_user),
    _ = Depends(get_user_permission({"ai_agentic": ["delete"]})),
):
    org_id = getattr(current_user, 'org_id', None)
    if org_id:
        org_id = uuid.UUID(str(org_id))
    
    deleted = await AIAgenticService.delete(db, template_id, org_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

