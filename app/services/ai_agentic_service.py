from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from app.models.ai_agentic import AIAgenticTemplate
from app.schemas.ai_agentic import AIAgenticTemplateCreate, AIAgenticTemplateUpdate
import uuid
import logging

logger = logging.getLogger(__name__)


class AIAgenticService:
    @staticmethod
    async def get_all(
        db: AsyncSession,
        org_id: Optional[uuid.UUID] = None,
        category: Optional[str] = None,
        module: Optional[str] = None,
        is_active: Optional[bool] = None,
        include_inactive: bool = False
    ) -> List[AIAgenticTemplate]:
        query = select(AIAgenticTemplate)
        
        conditions = []
        
        if org_id:
            conditions.append(AIAgenticTemplate.org_id == org_id)
        
        if category:
            conditions.append(AIAgenticTemplate.category == category)
        
        if module:
            conditions.append(AIAgenticTemplate.assigned_modules.contains([module]))
        
        if is_active is not None:
            conditions.append(AIAgenticTemplate.is_active == is_active)
        elif not include_inactive:
            conditions.append(AIAgenticTemplate.is_active == True)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(AIAgenticTemplate.display_order, AIAgenticTemplate.name)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        template_id: int,
        org_id: Optional[uuid.UUID] = None
    ) -> Optional[AIAgenticTemplate]:
        query = select(AIAgenticTemplate).where(AIAgenticTemplate.id == template_id)
        
        if org_id:
            query = query.where(AIAgenticTemplate.org_id == org_id)
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_module(
        db: AsyncSession,
        module: str,
        org_id: Optional[uuid.UUID] = None
    ) -> List[AIAgenticTemplate]:
        query = select(AIAgenticTemplate).where(
            and_(
                AIAgenticTemplate.is_active == True,
                AIAgenticTemplate.assigned_modules.contains([module])
            )
        )
        
        if org_id:
            query = query.where(
                or_(
                    AIAgenticTemplate.org_id == org_id,
                    AIAgenticTemplate.org_id.is_(None)
                )
            )
        else:
            query = query.where(AIAgenticTemplate.org_id.is_(None))
        
        query = query.order_by(AIAgenticTemplate.display_order, AIAgenticTemplate.name)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def create(
        db: AsyncSession,
        template_data: AIAgenticTemplateCreate,
        org_id: Optional[uuid.UUID] = None,
        user_id: Optional[uuid.UUID] = None
    ) -> AIAgenticTemplate:
        # Handle quick_actions: convert empty dict to None
        quick_actions = template_data.quick_actions
        if quick_actions is not None and isinstance(quick_actions, dict) and len(quick_actions) == 0:
            quick_actions = None
        
        template = AIAgenticTemplate(
            name=template_data.name,
            description=template_data.description,
            category=template_data.category,
            tags=template_data.tags or [],
            assigned_modules=template_data.assigned_modules or [],
            system_prompt=template_data.system_prompt,
            welcome_message=template_data.welcome_message,
            quick_actions=quick_actions,
            is_active=template_data.is_active,
            is_default=template_data.is_default,
            display_order=template_data.display_order,
            org_id=org_id,
            created_by=user_id
        )
        
        db.add(template)
        await db.flush()
        await db.refresh(template)
        return template
    
    @staticmethod
    async def update(
        db: AsyncSession,
        template_id: int,
        template_data: AIAgenticTemplateUpdate,
        org_id: Optional[uuid.UUID] = None
    ) -> Optional[AIAgenticTemplate]:
        template = await AIAgenticService.get_by_id(db, template_id, org_id)
        if not template:
            return None
        
        update_data = template_data.model_dump(exclude_unset=True)
        
        # Handle quick_actions: convert empty dict to None
        if 'quick_actions' in update_data:
            quick_actions = update_data['quick_actions']
            if quick_actions is not None and isinstance(quick_actions, dict) and len(quick_actions) == 0:
                update_data['quick_actions'] = None
        
        for field, value in update_data.items():
            setattr(template, field, value)
        
        await db.flush()
        await db.refresh(template)
        return template
    
    @staticmethod
    async def delete(
        db: AsyncSession,
        template_id: int,
        org_id: Optional[uuid.UUID] = None
    ) -> bool:
        template = await AIAgenticService.get_by_id(db, template_id, org_id)
        if not template:
            return False
        
        await db.delete(template)
        await db.flush()
        return True

