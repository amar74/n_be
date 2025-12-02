"""
Service for managing opportunity filter presets.
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from app.models.opportunity_filter_preset import OpportunityFilterPreset
from app.schemas.opportunity_filter_preset import (
    OpportunityFilterPresetCreate,
    OpportunityFilterPresetUpdate,
    OpportunityFilterPresetResponse,
)
from app.utils.logger import get_logger

logger = get_logger("opportunity_filter_preset_service")


class OpportunityFilterPresetService:
    """Service for managing filter presets."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_preset(
        self,
        org_id: UUID,
        user_id: UUID,
        preset_data: OpportunityFilterPresetCreate
    ) -> OpportunityFilterPresetResponse:
        """Create a new filter preset."""
        try:
            # If setting as default, unset other defaults for this user
            if preset_data.is_default:
                stmt = select(OpportunityFilterPreset).where(
                    OpportunityFilterPreset.user_id == user_id,
                    OpportunityFilterPreset.is_default == True
                )
                result = await self.db.execute(stmt)
                existing_defaults = result.scalars().all()
                for preset in existing_defaults:
                    preset.is_default = False
            
            preset = OpportunityFilterPreset(
                org_id=org_id,
                user_id=user_id,
                name=preset_data.name,
                description=preset_data.description,
                filters=preset_data.filters,
                is_shared=preset_data.is_shared,
                is_default=preset_data.is_default
            )
            
            self.db.add(preset)
            await self.db.flush()
            await self.db.refresh(preset)
            
            return OpportunityFilterPresetResponse.model_validate(preset)
            
        except Exception as e:
            logger.error(f"Error creating filter preset: {e}")
            raise
    
    async def get_presets(
        self,
        org_id: UUID,
        user_id: Optional[UUID] = None,
        include_shared: bool = True
    ) -> List[OpportunityFilterPresetResponse]:
        """Get filter presets for user and organization."""
        try:
            conditions = [OpportunityFilterPreset.org_id == org_id]
            
            if user_id:
                if include_shared:
                    conditions.append(
                        or_(
                            OpportunityFilterPreset.user_id == user_id,
                            OpportunityFilterPreset.is_shared == True
                        )
                    )
                else:
                    conditions.append(OpportunityFilterPreset.user_id == user_id)
            elif include_shared:
                conditions.append(OpportunityFilterPreset.is_shared == True)
            
            stmt = select(OpportunityFilterPreset).where(
                and_(*conditions)
            ).order_by(
                OpportunityFilterPreset.is_default.desc(),
                OpportunityFilterPreset.created_at.desc()
            )
            
            result = await self.db.execute(stmt)
            presets = result.scalars().all()
            
            return [OpportunityFilterPresetResponse.model_validate(p) for p in presets]
            
        except Exception as e:
            logger.error(f"Error getting filter presets: {e}")
            raise
    
    async def get_preset(
        self,
        preset_id: UUID,
        org_id: UUID,
        user_id: Optional[UUID] = None
    ) -> Optional[OpportunityFilterPresetResponse]:
        """Get a specific filter preset."""
        try:
            conditions = [
                OpportunityFilterPreset.id == preset_id,
                OpportunityFilterPreset.org_id == org_id
            ]
            
            if user_id:
                conditions.append(
                    or_(
                        OpportunityFilterPreset.user_id == user_id,
                        OpportunityFilterPreset.is_shared == True
                    )
                )
            
            stmt = select(OpportunityFilterPreset).where(and_(*conditions))
            result = await self.db.execute(stmt)
            preset = result.scalar_one_or_none()
            
            if preset:
                return OpportunityFilterPresetResponse.model_validate(preset)
            return None
            
        except Exception as e:
            logger.error(f"Error getting filter preset: {e}")
            raise
    
    async def update_preset(
        self,
        preset_id: UUID,
        org_id: UUID,
        user_id: UUID,
        update_data: OpportunityFilterPresetUpdate
    ) -> Optional[OpportunityFilterPresetResponse]:
        """Update a filter preset."""
        try:
            stmt = select(OpportunityFilterPreset).where(
                OpportunityFilterPreset.id == preset_id,
                OpportunityFilterPreset.org_id == org_id,
                OpportunityFilterPreset.user_id == user_id  # Only owner can update
            )
            result = await self.db.execute(stmt)
            preset = result.scalar_one_or_none()
            
            if not preset:
                return None
            
            # If setting as default, unset other defaults
            if update_data.is_default is True:
                stmt = select(OpportunityFilterPreset).where(
                    OpportunityFilterPreset.user_id == user_id,
                    OpportunityFilterPreset.id != preset_id,
                    OpportunityFilterPreset.is_default == True
                )
                result = await self.db.execute(stmt)
                existing_defaults = result.scalars().all()
                for p in existing_defaults:
                    p.is_default = False
            
            # Update fields
            if update_data.name is not None:
                preset.name = update_data.name
            if update_data.description is not None:
                preset.description = update_data.description
            if update_data.filters is not None:
                preset.filters = update_data.filters
            if update_data.is_shared is not None:
                preset.is_shared = update_data.is_shared
            if update_data.is_default is not None:
                preset.is_default = update_data.is_default
            
            await self.db.flush()
            await self.db.refresh(preset)
            
            return OpportunityFilterPresetResponse.model_validate(preset)
            
        except Exception as e:
            logger.error(f"Error updating filter preset: {e}")
            raise
    
    async def delete_preset(
        self,
        preset_id: UUID,
        org_id: UUID,
        user_id: UUID
    ) -> bool:
        """Delete a filter preset."""
        try:
            stmt = select(OpportunityFilterPreset).where(
                OpportunityFilterPreset.id == preset_id,
                OpportunityFilterPreset.org_id == org_id,
                OpportunityFilterPreset.user_id == user_id  # Only owner can delete
            )
            result = await self.db.execute(stmt)
            preset = result.scalar_one_or_none()
            
            if preset:
                await self.db.delete(preset)
                await self.db.flush()
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error deleting filter preset: {e}")
            raise

