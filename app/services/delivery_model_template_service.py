import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.delivery_model_template import DeliveryModelTemplate
from app.schemas.delivery_model_template import (
    DeliveryModelTemplateCreate,
    DeliveryModelTemplateUpdate,
    DeliveryModelTemplateResponse,
    DeliveryModelTemplatePhase,
)


class DeliveryModelTemplateService:
    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def _coerce_budget_value(value: Any) -> Optional[float]:
        if value is None or value == "":
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            cleaned = value.replace(",", "").replace("$", "").strip()
            if not cleaned:
                return None
            try:
                return float(cleaned)
            except ValueError:
                return None
        return None

    def _normalize_phases(self, phases: List[DeliveryModelTemplatePhase]) -> Tuple[List[Dict[str, Any]], float]:
        normalized: List[Dict[str, Any]] = []
        total_budget = 0.0
        timestamp = datetime.utcnow().isoformat()

        for phase in phases:
            budget = self._coerce_budget_value(phase.budget)
            if budget is not None:
                total_budget += budget

            normalized.append(
                {
                    "phase_id": str(phase.phase_id),
                    "name": phase.name.strip(),
                    "status": phase.status,
                    "duration": phase.duration,
                    "budget": budget,
                    "updated_by": phase.updated_by,
                    "description": phase.description,
                    "last_updated": phase.last_updated.isoformat() if phase.last_updated else timestamp,
                }
            )

        return normalized, total_budget

    def _deserialize_template(self, template: DeliveryModelTemplate) -> DeliveryModelTemplateResponse:
        raw_phases = template.phases or []
        phases: List[DeliveryModelTemplatePhase] = []

        for raw in raw_phases:
            if not isinstance(raw, dict):
                continue
            phases.append(
                DeliveryModelTemplatePhase(
                    phase_id=uuid.UUID(str(raw.get("phase_id", uuid.uuid4()))),
                    name=raw.get("name", ""),
                    status=raw.get("status"),
                    duration=raw.get("duration"),
                    budget=self._coerce_budget_value(raw.get("budget")),
                    updated_by=raw.get("updated_by"),
                    description=raw.get("description"),
                    last_updated=datetime.fromisoformat(raw["last_updated"]) if raw.get("last_updated") else None,
                )
            )

        return DeliveryModelTemplateResponse(
            id=template.id,
            org_id=template.org_id,
            created_by=template.created_by,
            approach=template.approach,
            notes=template.notes,
            phases=phases,
            created_at=template.created_at,
            updated_at=template.updated_at,
        )

    async def list_templates(self, org_id: uuid.UUID) -> List[DeliveryModelTemplateResponse]:
        stmt = (
            select(DeliveryModelTemplate)
            .where(DeliveryModelTemplate.org_id == org_id)
            .order_by(desc(DeliveryModelTemplate.updated_at))
        )
        result = await self.db.execute(stmt)
        templates = result.scalars().all()
        return [self._deserialize_template(template) for template in templates]

    async def get_template(self, template_id: uuid.UUID, org_id: uuid.UUID) -> Optional[DeliveryModelTemplateResponse]:
        stmt = select(DeliveryModelTemplate).where(
            DeliveryModelTemplate.id == template_id,
            DeliveryModelTemplate.org_id == org_id,
        )
        result = await self.db.execute(stmt)
        template = result.scalar_one_or_none()
        if not template:
            return None
        return self._deserialize_template(template)

    async def create_template(
        self,
        org_id: uuid.UUID,
        created_by: Optional[uuid.UUID],
        data: DeliveryModelTemplateCreate,
    ) -> DeliveryModelTemplateResponse:
        normalized_phases, _ = self._normalize_phases(data.phases)
        template = DeliveryModelTemplate(
            id=uuid.uuid4(),
            org_id=org_id,
            created_by=created_by,
            approach=data.approach.strip(),
            notes=data.notes.strip() if data.notes else None,
            phases=normalized_phases,
        )
        self.db.add(template)
        await self.db.flush()
        await self.db.refresh(template)
        return self._deserialize_template(template)

    async def update_template(
        self,
        template_id: uuid.UUID,
        org_id: uuid.UUID,
        data: DeliveryModelTemplateUpdate,
    ) -> Optional[DeliveryModelTemplateResponse]:
        stmt = select(DeliveryModelTemplate).where(
            DeliveryModelTemplate.id == template_id,
            DeliveryModelTemplate.org_id == org_id,
        )
        result = await self.db.execute(stmt)
        template = result.scalar_one_or_none()
        if not template:
            return None

        if data.approach is not None:
            template.approach = data.approach.strip()
        if data.notes is not None:
            template.notes = data.notes.strip() or None
        if data.phases is not None:
            normalized_phases, _ = self._normalize_phases(data.phases)
            template.phases = normalized_phases

        await self.db.flush()
        await self.db.refresh(template)
        return self._deserialize_template(template)

    async def delete_template(self, template_id: uuid.UUID, org_id: uuid.UUID) -> bool:
        stmt = select(DeliveryModelTemplate).where(
            DeliveryModelTemplate.id == template_id,
            DeliveryModelTemplate.org_id == org_id,
        )
        result = await self.db.execute(stmt)
        template = result.scalar_one_or_none()
        if not template:
            return False
        await self.db.delete(template)
        await self.db.flush()
        return True

