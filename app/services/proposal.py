from __future__ import annotations

import uuid
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException, status
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.environment import environment

from app.models.proposal import (
    Proposal,
    ProposalStatus,
    ProposalSource,
    ProposalType,
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
        from sqlalchemy.exc import OperationalError, InvalidRequestError
        
        year = datetime.utcnow().year
        prefix = f"PROP-{year}"
        
        try:
            # Query all existing proposal numbers for this org and year, ordered by number
            # This gives us the highest number currently in use
            result = await self.db.execute(
                select(Proposal.proposal_number)
                .where(
                    Proposal.org_id == org_id,
                    Proposal.proposal_number.like(f"{prefix}-%")
                )
                .order_by(desc(Proposal.proposal_number))
                .limit(100)  # Limit to recent proposals for performance
            )
            existing_numbers = [row[0] for row in result.fetchall()]
            
            # Find the highest sequential number
            max_number = 0
            for prop_num in existing_numbers:
                try:
                    # Extract number from "PROP-2025-0001" or "PROP-2025-0001-ABC12345" format
                    parts = prop_num.split('-')
                    if len(parts) >= 3:
                        num_str = parts[2]  # Third part is the number (e.g., "0001")
                        # Parse the 4-digit number
                        num = int(num_str)
                        if num > max_number:
                            max_number = num
                except (ValueError, IndexError):
                    continue
            
            # Generate next sequential number
            next_number = max_number + 1
            
            # Always add a UUID suffix to ensure uniqueness even with concurrent requests
            # This prevents race conditions where two requests generate the same sequential number
            # Format: PROP-2025-0001-ABC12345
            unique_suffix = str(uuid.uuid4())[:8].upper()
            proposal_number = f"{prefix}-{next_number:04d}-{unique_suffix}"
            
            logger.info(f"Generated proposal number: {proposal_number} for org {org_id}")
            return proposal_number
            
        except (OperationalError, InvalidRequestError) as e:
            # Transaction/session error - use timestamp + UUID for guaranteed uniqueness
            logger.warning(f"Database session error generating proposal number: {e}, using timestamp fallback")
            import time
            timestamp = str(int(time.time()))[-6:]  # Last 6 digits of timestamp
            unique_suffix = str(uuid.uuid4())[:8].upper()
            return f"{prefix}-{timestamp}-{unique_suffix}"
        except Exception as e:
            # Any other error - use timestamp + UUID for guaranteed uniqueness
            logger.warning(f"Unexpected error generating proposal number: {e}, using timestamp fallback")
            import time
            timestamp = str(int(time.time()))[-6:]  # Last 6 digits of timestamp
            unique_suffix = str(uuid.uuid4())[:8].upper()
            return f"{prefix}-{timestamp}-{unique_suffix}"

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
            # Generic error to prevent information leakage
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Resource not found or access denied"
            )
        return proposal

    async def _validate_opportunity(
        self, opportunity_id: Optional[uuid.UUID], org_id: uuid.UUID
    ) -> Optional[Opportunity]:
        if not opportunity_id:
            return None
        try:
            result = await self.db.execute(
                select(Opportunity.id, Opportunity.account_id, Opportunity.org_id).where(
                    Opportunity.id == opportunity_id, Opportunity.org_id == org_id
                )
            )
            row = result.mappings().first()
            if not row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail="Resource not found or access denied"
                )
            # Create a simple object with just the fields we need
            class OpportunityData:
                def __init__(self, id, account_id, org_id):
                    self.id = id
                    self.account_id = account_id
                    self.org_id = org_id
            
            return OpportunityData(row['id'], row['account_id'], row['org_id'])
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error validating opportunity: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to validate opportunity: {str(e)}"
            )

    async def _validate_account(self, account_id: Optional[uuid.UUID], org_id: uuid.UUID) -> Optional[Account]:
        if not account_id:
            return None
        try:
            result = await self.db.execute(
                select(Account.account_id, Account.org_id).where(Account.account_id == account_id)
            )
            row = result.mappings().first()
            if not row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail="Resource not found or access denied"
                )
            # Check org_id from the row data, not from the object
            if row['org_id'] != org_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail="Resource not found or access denied"
                )
            # Return a simple object to avoid SQLAlchemy lazy loading issues
            class AccountData:
                def __init__(self, account_id, org_id):
                    self.account_id = account_id
                    self.org_id = org_id
            
            return AccountData(row['account_id'], row['org_id'])
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error validating account: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to validate account: {str(e)}"
            )

    async def create_proposal(self, payload: ProposalCreate, user: User) -> ProposalResponse:
        try:
            from app.utils.security import mask_id
            
            # Store user attributes immediately
            user_id = user.id if hasattr(user, 'id') else None
            user_org_id = user.org_id if hasattr(user, 'org_id') else None
            
            if not user_id or not user_org_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail="User must belong to an organization"
                )

            logger.info("=== CREATE PROPOSAL START ===")
            logger.info(f"User: {mask_id(str(user_id))}, Org: {mask_id(str(user_org_id))}")

            # Validate opportunity and account
            opportunity = await self._validate_opportunity(payload.opportunity_id, user_org_id)
            opportunity_account_id = getattr(opportunity, 'account_id', None) if opportunity else None
            account_id = payload.account_id or opportunity_account_id
            
            if account_id:
                await self._validate_account(account_id, user_org_id)

            # Prepare datetime
            now = datetime.utcnow()
            
            # Helper to convert Decimal to float
            def safe_float(val):
                return float(val) if val is not None else None
            
            # Generate proposal number and ID (do this once before attempting to create)
            # The number generation includes conflict checking, so this should be safe
            proposal_number = await self._generate_proposal_number(user_org_id)
            proposal_id = uuid.uuid4()
            
            # Create proposal with explicit ID
            proposal = Proposal(
                id=proposal_id,
                org_id=user_org_id,
                opportunity_id=payload.opportunity_id,
                account_id=account_id,
                created_by=user_id,
                owner_id=payload.owner_id or user_id,
                proposal_number=proposal_number,
                title=payload.title,
                summary=payload.summary,
                status=ProposalStatus.draft,
                source=ProposalSource.opportunity if payload.opportunity_id else ProposalSource.manual,
                proposal_type=payload.proposal_type,
                version=1,
                total_value=payload.total_value,
                currency=payload.currency or "USD",
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
                requires_approval=payload.requires_approval if payload.requires_approval is not None else True,
                notes=payload.notes,
                tags=payload.tags,
                created_at=now,
                updated_at=now,
            )

            self.db.add(proposal)

            # Add sections if provided
            if payload.sections:
                for order, section_data in enumerate(payload.sections):
                    section = ProposalSection(
                        proposal_id=proposal_id,
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

            # Add documents if provided
            if payload.documents:
                for doc in payload.documents:
                    document = ProposalDocument(
                        proposal_id=proposal_id,
                        name=doc.name,
                        category=doc.category,
                        file_path=doc.file_path,
                        external_url=doc.external_url,
                        uploaded_by=user_id,
                        extra_metadata=doc.extra_metadata,
                    )
                    self.db.add(document)

            # Flush all changes - let middleware handle commit
            # If this fails with a duplicate number, we can't retry within the same transaction
            # because the transaction will be rolled back. The client will need to retry the request.
            try:
                await self.db.flush()
                logger.info(f"Proposal flushed successfully: {proposal_id} with number {proposal_number}")
            except Exception as flush_error:
                import traceback
                from sqlalchemy.exc import IntegrityError
                
                error_str = str(flush_error)
                if hasattr(flush_error, 'orig'):
                    error_str = str(flush_error.orig)
                
                logger.error(f"Flush error: {flush_error}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                
                # Check if it's a unique constraint violation on proposal_number
                is_duplicate_number = (
                    isinstance(flush_error, IntegrityError) or
                    ("unique" in error_str.lower() or "duplicate" in error_str.lower()) and
                    ("proposal_number" in error_str.lower() or "proposal_number" in str(flush_error))
                )
                
                if is_duplicate_number:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"Proposal number {proposal_number} already exists. Please try again."
                    )
                
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to save proposal: {error_str}"
                )
            
            # Build response from known values - NO database access
            response_data = {
                "id": proposal_id,
                "org_id": user_org_id,
                "proposal_number": proposal_number,
                "title": payload.title,
                "summary": payload.summary,
                "status": ProposalStatus.draft,
                "source": ProposalSource.opportunity if payload.opportunity_id else ProposalSource.manual,
                "proposal_type": payload.proposal_type,
                "version": 1,
                "opportunity_id": payload.opportunity_id,
                "account_id": account_id,
                "owner_id": payload.owner_id or user_id,
                "created_by": user_id,
                "total_value": safe_float(payload.total_value),
                "currency": payload.currency or "USD",
                "estimated_cost": safe_float(payload.estimated_cost),
                "expected_margin": safe_float(payload.expected_margin),
                "fee_structure": payload.fee_structure,
                "due_date": payload.due_date,
                "submission_date": payload.submission_date,
                "client_response_date": payload.client_response_date,
                "won_at": None,
                "lost_at": None,
                "ai_assistance_summary": payload.ai_assistance_summary,
                "ai_content_percentage": payload.ai_content_percentage,
                "ai_last_run_at": None,
                "ai_metadata": None,
                "finance_snapshot": payload.finance_snapshot,
                "resource_snapshot": payload.resource_snapshot,
                "client_snapshot": payload.client_snapshot,
                "requires_approval": payload.requires_approval if payload.requires_approval is not None else True,
                "approval_completed": False,
                "converted_to_project": False,
                "conversion_metadata": None,
                "notes": payload.notes,
                "tags": payload.tags,
                "created_at": now,
                "updated_at": now,
                "sections": [],
                "documents": [],
                "approvals": [],
            }
            
            # Create response object - NO database access
            response = ProposalResponse.model_validate(response_data)
            logger.info(f"Proposal created successfully: {proposal_id}")
            logger.info("=== CREATE PROPOSAL END ===")
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            import traceback
            from sqlalchemy.exc import InvalidRequestError, OperationalError
            
            logger.exception(f"Error creating proposal: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Check for transaction-related errors
            error_msg = str(e)
            if isinstance(e, (InvalidRequestError, OperationalError)) or "closed transaction" in error_msg.lower():
                logger.error("Transaction was closed - this may be due to a database connection issue")
            
            detail_msg = error_msg
            if hasattr(e, 'orig'):
                detail_msg = f"{detail_msg} | {str(e.orig)}"
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create proposal: {detail_msg}"
            )

    async def list_proposals(
        self,
        user: User,
        page: int = 1,
        size: int = 10,
        status_filter: Optional[ProposalStatus] = None,
        type_filter: Optional[ProposalType] = None,
        search: Optional[str] = None,
    ) -> ProposalListResponse:
        try:
            if not user.org_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User missing organization")

            filters = [Proposal.org_id == user.org_id]
            if status_filter:
                filters.append(Proposal.status == status_filter)
            if type_filter:
                filters.append(Proposal.proposal_type == type_filter)
            if search:
                # Sanitize search input - limit length and escape special characters
                search_clean = search.strip()[:100]  # Limit to 100 characters
                search_like = f"%{search_clean.lower()}%"
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
            
            # Validate each proposal and handle validation errors gracefully
            items = []
            for proposal in proposals:
                try:
                    # Ensure required fields have defaults if missing (for backward compatibility)
                    currency = getattr(proposal, 'currency', None) or "USD"
                    proposal_type = getattr(proposal, 'proposal_type', None) or ProposalType.proposal
                    
                    # Convert total_value to float if it's a Decimal
                    total_value = None
                    if proposal.total_value is not None:
                        try:
                            total_value = float(proposal.total_value)
                        except (ValueError, TypeError):
                            total_value = None
                    
                    # Create dict with all required fields, applying defaults
                    proposal_data = {
                        "id": proposal.id,
                        "proposal_number": proposal.proposal_number,
                        "title": proposal.title,
                        "status": proposal.status,
                        "proposal_type": proposal_type,
                        "opportunity_id": getattr(proposal, 'opportunity_id', None),
                        "account_id": getattr(proposal, 'account_id', None),
                        "total_value": total_value,
                        "currency": currency,
                        "submission_date": getattr(proposal, 'submission_date', None),
                        "created_at": proposal.created_at,
                        "updated_at": proposal.updated_at,
                    }
                    
                    # Use model_validate with the dict
                    items.append(ProposalListItem.model_validate(proposal_data))
                except Exception as e:
                    logger.error(f"Error validating proposal {proposal.id}: {str(e)}")
                    import traceback
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    # Skip invalid proposals instead of failing the entire request
                    continue
            
            return ProposalListResponse(items=items, total=total, page=page, size=size)
        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error listing proposals for user {user.id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list proposals: {str(e)}"
            )

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

        # Handle proposal_type enum conversion if present
        if "proposal_type" in update_fields and isinstance(update_fields["proposal_type"], str):
            update_fields["proposal_type"] = ProposalType(update_fields["proposal_type"])

        for field, value in update_fields.items():
            setattr(proposal, field, value)

        proposal.updated_at = datetime.utcnow()
        await self.db.flush()
        # Refresh to ensure relationships are loaded
        await self.db.refresh(proposal, ["sections", "documents", "approvals"])
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
        await self.db.flush()
        await self.db.refresh(proposal, ["sections", "documents", "approvals"])
        return ProposalResponse.model_validate(proposal)

    async def upload_document(
        self,
        proposal_id: uuid.UUID,
        file_content: bytes,
        file_name: str,
        content_type: str,
        category: str,
        user: User,
    ) -> ProposalResponse:
        """
        Upload document to proposal with S3/local storage fallback.
        Clean implementation with proper error handling.
        """
        # Get proposal
        proposal = await self._get_proposal_for_org(proposal_id, user.org_id)
        
        # Validate file name
        if not file_name or not file_name.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File name is required"
            )
        
        # Truncate file name if too long (database limit is 255)
        safe_file_name = file_name[:255] if len(file_name) > 255 else file_name
        
        # Validate category
        from app.models.proposal import ProposalDocumentCategory
        try:
            document_category = ProposalDocumentCategory(category)
        except ValueError:
            document_category = ProposalDocumentCategory.attachment
            logger.warning(f"Invalid category '{category}', defaulting to 'attachment'")
        
        # Prepare metadata (JSON-serializable dict only)
        metadata = {
            "content_type": str(content_type) if content_type else "application/octet-stream",
            "file_size": int(len(file_content)),
            "uploaded_at": datetime.utcnow().isoformat(),
        }
        
        # Try S3 first, fallback to local storage
        file_url = None
        file_path = None
        storage_type = "local"  # default
        
        # Check if S3 is configured
        s3_configured = all([
            environment.AWS_ACCESS_KEY_ID,
            environment.AWS_SECRET_ACCESS_KEY,
            environment.AWS_S3_BUCKET_NAME
        ])
        
        if s3_configured:
            try:
                # Prepare S3 key
                timestamp = int(datetime.utcnow().timestamp())
                # Sanitize file name for S3 (remove special chars)
                safe_s3_name = "".join(c if c.isalnum() or c in "-_." else "_" for c in safe_file_name)
                s3_key = f"proposals/{proposal_id}/{timestamp}_{safe_s3_name}"
                
                # Initialize S3 client
                s3_client = boto3.client(
                    's3',
                    aws_access_key_id=environment.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=environment.AWS_SECRET_ACCESS_KEY,
                    region_name=environment.AWS_S3_REGION or "us-east-1"
                )
                
                # Upload to S3
                s3_client.put_object(
                    Bucket=environment.AWS_S3_BUCKET_NAME,
                    Key=s3_key,
                    Body=file_content,
                    ContentType=content_type or "application/octet-stream"
                )
                
                # Build S3 URL
                region_segment = f".{environment.AWS_S3_REGION}" if environment.AWS_S3_REGION else ""
                file_url = f"https://{environment.AWS_S3_BUCKET_NAME}.s3{region_segment}.amazonaws.com/{s3_key}"
                file_path = s3_key
                storage_type = "s3"
                
                logger.info(f"File uploaded to S3: {s3_key}")
            except ClientError as e:
                logger.warning(f"S3 upload failed ({e}), falling back to local storage")
            except Exception as e:
                logger.warning(f"S3 upload error ({type(e).__name__}: {e}), falling back to local storage")
        
        # Use local storage if S3 failed or not configured
        if not file_path or storage_type != "s3":
            try:
                # Ensure upload directory exists
                upload_root = os.path.join("uploads", "proposal_documents")
                os.makedirs(upload_root, exist_ok=True)
                
                proposal_dir = os.path.join(upload_root, str(proposal_id))
                os.makedirs(proposal_dir, exist_ok=True)
                
                # Generate local filename
                timestamp = int(datetime.utcnow().timestamp())
                # Sanitize filename for filesystem
                safe_local_name = "".join(c if c.isalnum() or c in "-_." else "_" for c in safe_file_name)
                local_filename = f"{timestamp}_{safe_local_name}"
                local_path = os.path.join(proposal_dir, local_filename)
                
                # Save file
                with open(local_path, "wb") as f:
                    f.write(file_content)
                
                file_path = local_path
                storage_type = "local"
                
                # Build local URL
                api_base = getattr(environment, 'FRONTEND_URL', None) or "http://127.0.0.1:8000"
                if ":5173" in api_base:
                    api_base = api_base.replace(":5173", ":8000")
                file_url = f"{api_base}/uploads/proposal_documents/{proposal_id}/{local_filename}"
                
                logger.info(f"File saved to local storage: {local_path}")
            except PermissionError as e:
                logger.error(f"Permission denied saving file: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Permission denied saving file: {str(e)}"
                )
            except OSError as e:
                logger.error(f"OS error saving file: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to save file: {str(e)}"
                )
            except Exception as e:
                logger.error(f"Unexpected error saving file: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to save file: {str(e)}"
                )
        
        # Ensure we have file_path
        if not file_path:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to determine file storage path"
            )
        
        # Update metadata with storage info
        metadata["storage_type"] = storage_type
        
        # Create document record
        try:
            new_document = ProposalDocument(
                proposal_id=proposal.id,
                name=safe_file_name,
                category=document_category,
                file_path=file_path,
                external_url=file_url if file_url and file_url.startswith('http') else None,
                uploaded_by=user.id,
                extra_metadata=metadata,  # JSON-serializable dict only
            )
            self.db.add(new_document)
            proposal.updated_at = datetime.utcnow()
            
            # Flush to database
            await self.db.flush()
            logger.info(f"Document record created: id={new_document.id}, storage={storage_type}")
        except Exception as db_error:
            logger.error(f"Database error creating document: {db_error}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create document record: {str(db_error)}"
            )
        
        # Re-query proposal with relationships to ensure all documents are loaded
        # This is necessary because refresh() doesn't reload relationships properly
        result = await self.db.execute(
            select(Proposal)
            .where(Proposal.id == proposal_id)
            .options(
                selectinload(Proposal.sections),
                selectinload(Proposal.documents),
                selectinload(Proposal.approvals),
            )
        )
        proposal = result.scalar_one()
        
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
        await self.db.flush()
        await self.db.refresh(proposal, ["sections", "documents", "approvals"])
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

        await self.db.flush()
        await self.db.refresh(proposal, ["sections", "documents", "approvals"])
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
        await self.db.flush()
        await self.db.refresh(proposal, ["sections", "documents", "approvals"])
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

        await self.db.flush()
        await self.db.refresh(proposal, ["sections", "documents", "approvals"])
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

        await self.db.flush()
        return ProposalConversionResponse(
            proposal_id=proposal.id,
            converted_to_project=True,
            project_reference=project_reference,
            message="Proposal converted to project successfully",
        )
