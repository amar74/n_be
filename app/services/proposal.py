from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import HTTPException, status
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.proposal import (
    Proposal,
    ProposalStatus,
    ProposalSource,
    ProposalSection,
    ProposalDocument,
    ProposalApproval,
    ProposalApprovalStatus,
)
from app.models.opportunity import Opportunity
from app.models.account import Account
from app.models.user import User
from app.schemas.proposal import (
    ProposalCreate,
    ProposalUpdate,
    ProposalResponse,
    ProposalListResponse,
    ProposalListItem,
    ProposalSubmitRequest,
    ProposalApprovalDecision,
    ProposalStatusUpdateRequest,
    ProposalConversionResponse,
    ProposalSectionCreate,
    ProposalSectionUpdate,
    ProposalDocumentCreate,
    ProposalApprovalCreate,
)
from app.utils.logger import get_logger


logger = get_logger("proposal_service")

DEFAULT_APPROVAL_FLOW: List[ProposalApprovalCreate] = [
    ProposalApprovalCreate(stage_name="Business Development Review", required_role="business_development", sequence=0),
    ProposalApprovalCreate(stage_name="Technical Manager Review", required_role="technical_manager", sequence=1),
    ProposalApprovalCreate(stage_name="Finance Manager Review", required_role="finance_manager", sequence=2),
    ProposalApprovalCreate(stage_name="Director Approval", required_role="director", sequence=3),
]


class ProposalService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _generate_proposal_number(self, org_id: uuid.UUID) -> str:
        year = datetime.utcnow().year
        prefix = f"PROP-{year}"
        result = await self.db.execute(
            select(func.count(Proposal.id)).where(
                Proposal.org_id == org_id, Proposal.proposal_number.like(f"{prefix}%")
            )
        )
        count = result.scalar() or 0
        return f"{prefix}-{count + 1:04d}"

    async def _get_proposal_for_org(self, proposal_id: uuid.UUID, org_id: uuid.UUID) -> Proposal:
        proposal = await self.db.get(
            Proposal,
            proposal_id,
            options=[
                selectinload(Proposal.sections),
                selectinload(Proposal.documents),
                selectinload(Proposal.approvals),
            ],
        )
        if not proposal or proposal.org_id != org_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proposal not found")
        return proposal

    async def _validate_opportunity(
        self, opportunity_id: Optional[uuid.UUID], org_id: uuid.UUID
    ) -> Optional[Opportunity]:
        if not opportunity_id:
            return None
        opportunity = await self.db.get(Opportunity, opportunity_id)
        if not opportunity or opportunity.org_id != org_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")
        return opportunity

    async def _validate_account(self, account_id: Optional[uuid.UUID], org_id: uuid.UUID) -> Optional[Account]:
        if not account_id:
            return None
        account = await self.db.get(Account, account_id)
        if not account or getattr(account, "org_id", None) != org_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
        return account

    async def create_proposal(self, payload: ProposalCreate, user: User) -> ProposalResponse:
        logger.info("Creating proposal for user %s", user.id)
        if not user.org_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="User must belong to an organization"
            )

        opportunity = await self._validate_opportunity(payload.opportunity_id, user.org_id)
        account_id = payload.account_id or (opportunity.account_id if opportunity else None)
        if account_id:
            await self._validate_account(account_id, user.org_id)

        proposal_number = await self._generate_proposal_number(user.org_id)

        proposal = Proposal(
            org_id=user.org_id,
            opportunity_id=payload.opportunity_id,
            account_id=account_id,
            created_by=user.id,
            owner_id=payload.owner_id or user.id,
            proposal_number=proposal_number,
            title=payload.title,
            summary=payload.summary,
            status=ProposalStatus.draft,
            source=ProposalSource.opportunity if payload.opportunity_id else ProposalSource.manual,
            total_value=payload.total_value,
            currency=payload.currency,
            estimated_cost=payload.estimated_cost,
            expected_margin=payload.expected_margin,
            fee_structure=payload.fee_structure,
            due_date=payload.due_date,
            submission_date=payload.submission_date,
            client_response_date=payload.client_response_date,
            ai_assistance_summary=payload.ai_assistance_summary,
            ai_content_percentage=payload.ai_content_percentage,
            finance_snapshot=payload.finance_snapshot,
            resource_snapshot=payload.resource_snapshot,
            client_snapshot=payload.client_snapshot,
            requires_approval=payload.requires_approval,
            notes=payload.notes,
            tags=payload.tags,
        )

        self.db.add(proposal)
        await self.db.flush()

        if payload.sections:
            for order, section_data in enumerate(payload.sections):
                section = ProposalSection(
                    proposal_id=proposal.id,
                    section_type=section_data.section_type,
                    title=section_data.title,
                    content=section_data.content,
                    status=section_data.status,
                    page_count=section_data.page_count,
                    ai_generated_percentage=section_data.ai_generated_percentage,
                    extra_metadata=section_data.extra_metadata,
                    display_order=section_data.display_order if section_data.display_order is not None else order,
                )
                self.db.add(section)

        if payload.documents:
            for doc in payload.documents:
                document = ProposalDocument(
                    proposal_id=proposal.id,
                    name=doc.name,
                    category=doc.category,
                    file_path=doc.file_path,
                    external_url=doc.external_url,
                    uploaded_by=user.id,
                    extra_metadata=doc.extra_metadata,
                )
                self.db.add(document)

        await self.db.commit()
        await self.db.refresh(proposal)
        return ProposalResponse.model_validate(proposal)

    async def list_proposals(
        self,
        user: User,
        page: int = 1,
        size: int = 10,
        status_filter: Optional[ProposalStatus] = None,
        search: Optional[str] = None,
    ) -> ProposalListResponse:
        if not user.org_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User missing organization")

        filters = [Proposal.org_id == user.org_id]
        if status_filter:
            filters.append(Proposal.status == status_filter)
        if search:
            search_like = f"%{search.lower()}%"
            filters.append(
                func.lower(Proposal.title).like(search_like)
                | func.lower(Proposal.proposal_number).like(search_like)
                | func.lower(Proposal.summary).like(search_like)
            )

        query = select(Proposal).where(*filters)
        count_query = select(func.count(Proposal.id)).where(*filters)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        result = await self.db.execute(
            query.order_by(desc(Proposal.created_at)).offset((page - 1) * size).limit(size)
        )
        proposals = result.scalars().all()
        items = [ProposalListItem.model_validate(proposal) for proposal in proposals]
        return ProposalListResponse(items=items, total=total, page=page, size=size)

    async def get_proposal(self, proposal_id: uuid.UUID, user: User) -> ProposalResponse:
        proposal = await self._get_proposal_for_org(proposal_id, user.org_id)
        return ProposalResponse.model_validate(proposal)

    async def get_proposals_by_opportunity(
        self, opportunity_id: uuid.UUID, user: User
    ) -> List[ProposalResponse]:
        await self._validate_opportunity(opportunity_id, user.org_id)
        result = await self.db.execute(
            select(Proposal)
            .where(Proposal.org_id == user.org_id, Proposal.opportunity_id == opportunity_id)
            .options(
                selectinload(Proposal.sections),
                selectinload(Proposal.documents),
                selectinload(Proposal.approvals),
            )
            .order_by(desc(Proposal.created_at))
        )
        return [ProposalResponse.model_validate(proposal) for proposal in result.scalars().all()]

    async def update_proposal(
        self,
        proposal_id: uuid.UUID,
        payload: ProposalUpdate,
        user: User,
    ) -> ProposalResponse:
        proposal = await self._get_proposal_for_org(proposal_id, user.org_id)
        update_fields: Dict[str, Any] = payload.model_dump(exclude_unset=True)
        if "currency" in update_fields and update_fields["currency"] is None:
            update_fields.pop("currency")

        for field, value in update_fields.items():
            setattr(proposal, field, value)

        proposal.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(proposal)
        return ProposalResponse.model_validate(proposal)

    async def add_or_update_section(
        self,
        proposal_id: uuid.UUID,
        section_id: Optional[uuid.UUID],
        data: ProposalSectionCreate | ProposalSectionUpdate,
        user: User,
    ) -> ProposalResponse:
        proposal = await self._get_proposal_for_org(proposal_id, user.org_id)

        if section_id:
            section = next((s for s in proposal.sections if s.id == section_id), None)
            if not section:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proposal section not found")
            update_data = data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(section, field, value)
            section.updated_at = datetime.utcnow()
        else:
            if isinstance(data, ProposalSectionCreate):
                new_section = ProposalSection(
                    proposal_id=proposal.id,
                    section_type=data.section_type,
                    title=data.title,
                    content=data.content,
                    status=data.status,
                    page_count=data.page_count,
                    ai_generated_percentage=data.ai_generated_percentage,
                    extra_metadata=data.extra_metadata,
                    display_order=data.display_order if data.display_order is not None else len(proposal.sections),
                )
                self.db.add(new_section)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Section ID required for update operation"
                )

        proposal.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(proposal)
        return ProposalResponse.model_validate(proposal)

    async def add_document(
        self,
        proposal_id: uuid.UUID,
        document: ProposalDocumentCreate,
        user: User,
    ) -> ProposalResponse:
        proposal = await self._get_proposal_for_org(proposal_id, user.org_id)
        new_document = ProposalDocument(
            proposal_id=proposal.id,
            name=document.name,
            category=document.category,
            file_path=document.file_path,
            external_url=document.external_url,
            uploaded_by=user.id,
            extra_metadata=document.extra_metadata,
        )
        self.db.add(new_document)
        proposal.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(proposal)
        return ProposalResponse.model_validate(proposal)

    async def submit_proposal(
        self,
        proposal_id: uuid.UUID,
        payload: ProposalSubmitRequest,
        user: User,
    ) -> ProposalResponse:
        proposal = await self._get_proposal_for_org(proposal_id, user.org_id)
        if proposal.status not in {ProposalStatus.draft, ProposalStatus.in_review}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only draft or in-review proposals can be submitted",
            )

        approval_flow = payload.approval_flow or DEFAULT_APPROVAL_FLOW
        if not proposal.approvals:
            for approval in approval_flow:
                approval_record = ProposalApproval(
                    proposal_id=proposal.id,
                    stage_name=approval.stage_name,
                    required_role=approval.required_role,
                    sequence=approval.sequence,
                    status=ProposalApprovalStatus.pending,
                )
                self.db.add(approval_record)

        proposal.status = ProposalStatus.in_review
        proposal.submission_date = proposal.submission_date or datetime.utcnow().date()
        proposal.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(proposal)
        return ProposalResponse.model_validate(proposal)

    async def decide_approval(
        self,
        proposal_id: uuid.UUID,
        decision_payload: ProposalApprovalDecision,
        user: User,
    ) -> ProposalResponse:
        proposal = await self._get_proposal_for_org(proposal_id, user.org_id)
        approval = next((a for a in proposal.approvals if a.id == decision_payload.approval_id), None)
        if not approval:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval record not found")
        if approval.status != ProposalApprovalStatus.pending:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Approval already processed for this stage"
            )

        if decision_payload.decision == ProposalApprovalStatus.approved:
            approval.status = ProposalApprovalStatus.approved
        elif decision_payload.decision == ProposalApprovalStatus.rejected:
            approval.status = ProposalApprovalStatus.rejected
            proposal.status = ProposalStatus.in_review
        else:
            approval.status = decision_payload.decision

        approval.approver_id = user.id
        approval.comments = decision_payload.comments
        approval.decision_at = datetime.utcnow()
        approval.updated_at = datetime.utcnow()

        if all(a.status == ProposalApprovalStatus.approved for a in proposal.approvals):
            proposal.status = ProposalStatus.approved
            proposal.approval_completed = True

        proposal.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(proposal)
        return ProposalResponse.model_validate(proposal)

    async def update_status(
        self,
        proposal_id: uuid.UUID,
        payload: ProposalStatusUpdateRequest,
        user: User,
    ) -> ProposalResponse:
        proposal = await self._get_proposal_for_org(proposal_id, user.org_id)

        if payload.status == ProposalStatus.won:
            proposal.won_at = datetime.utcnow()
            proposal.lost_at = None
        elif payload.status == ProposalStatus.lost:
            proposal.lost_at = datetime.utcnow()
            proposal.won_at = None

        proposal.status = payload.status
        proposal.notes = payload.notes or proposal.notes
        proposal.conversion_metadata = payload.conversion_metadata or proposal.conversion_metadata
        proposal.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(proposal)
        return ProposalResponse.model_validate(proposal)

    async def convert_to_project(
        self,
        proposal_id: uuid.UUID,
        conversion_metadata: Optional[Dict[str, Any]],
        user: User,
    ) -> ProposalConversionResponse:
        proposal = await self._get_proposal_for_org(proposal_id, user.org_id)
        if proposal.status != ProposalStatus.won:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Proposal must be marked as won before conversion",
            )

        proposal.converted_to_project = True
        proposal.conversion_metadata = conversion_metadata or {}
        proposal.updated_at = datetime.utcnow()

        project_reference = {
            "project_id": str(uuid.uuid4()),
            "generated_at": datetime.utcnow().isoformat(),
        }
        proposal.conversion_metadata.update(project_reference)

        await self.db.commit()
        return ProposalConversionResponse(
            proposal_id=proposal.id,
            converted_to_project=True,
            project_reference=project_reference,
            message="Proposal converted to project successfully",
        )
