from __future__ import annotations

import uuid
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any

from fastapi import HTTPException, status
from sqlalchemy import select, func, desc, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.contract import (
    Contract,
    ContractStatus,
    RiskLevel as ContractRiskLevel,
    ClauseLibraryItem,
    ClauseCategory,
    ClauseRiskLevel,
)
from app.models.proposal import Proposal
from app.models.account import Account
from app.models.user import User
from app.models.opportunity import Opportunity
from app.models.opportunity import RiskLevel as OpportunityRiskLevel
from app.schemas.contract import (
    ContractCreate,
    ContractUpdate,
    ContractResponse,
    ContractListResponse,
    ContractListItem,
    ContractFromProposalRequest,
    ContractAnalysisResponse,
    ContractAnalysisItem,
    ClauseLibraryCreate,
    ClauseLibraryUpdate,
    ClauseLibraryResponse,
    ClauseLibraryListResponse,
    ClauseCategoryCreate,
    ClauseCategoryResponse,
    WorkflowStep,
    ReviewerInfo,
    WorkflowStats,
    ContractWorkflowResponse,
)
from app.utils.logger import get_logger
from app.services.pdf_extractor import PDFExtractor
import os
import boto3
from botocore.exceptions import ClientError
from app.environment import environment
import re
import asyncio


logger = get_logger("contract_service")


class ContractService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _generate_contract_id(self, org_id: uuid.UUID) -> str:
        year = datetime.utcnow().year
        prefix = f"CNT-{year}"
        
        try:
            result = await self.db.execute(
                select(Contract.contract_id)
                .where(
                    Contract.org_id == org_id,
                    Contract.contract_id.like(f"{prefix}-%")
                )
                .order_by(desc(Contract.contract_id))
                .limit(100)
            )
            existing_ids = [row[0] for row in result.fetchall() if row[0]]
            
            max_number = 0
            for cnt_id in existing_ids:
                try:
                    parts = cnt_id.split('-')
                    if len(parts) >= 3:
                        num_str = parts[2]
                        num = int(num_str)
                        if num > max_number:
                            max_number = num
                except (ValueError, IndexError):
                    continue
            
            next_number = max_number + 1
            unique_suffix = str(uuid.uuid4())[:8].upper()
            contract_id = f"{prefix}-{next_number:04d}-{unique_suffix}"
            
            logger.info(f"Generated contract ID: {contract_id} for org {org_id}")
            return contract_id
        except Exception as e:
            logger.warning(f"Error generating contract ID: {e}, using timestamp fallback")
            import time
            timestamp = str(int(time.time()))[-6:]
            unique_suffix = str(uuid.uuid4())[:8].upper()
            return f"{prefix}-{timestamp}-{unique_suffix}"

    async def _get_contract_for_org(self, contract_id: uuid.UUID, org_id: uuid.UUID) -> Contract:
        contract = await self.db.get(Contract, contract_id)
        if not contract or contract.org_id != org_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contract not found or access denied"
            )
        return contract

    async def _get_proposal_for_org(self, proposal_id: uuid.UUID, org_id: uuid.UUID) -> Proposal:
        proposal = await self.db.get(Proposal, proposal_id)
        if not proposal or proposal.org_id != org_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Proposal not found or access denied"
            )
        return proposal

    async def create_contract(self, payload: ContractCreate, user: User) -> ContractResponse:
        try:
            logger.info(f"Creating contract - client_name: {payload.client_name}, project_name: {payload.project_name}, document_type: {payload.document_type}")
            logger.info(f"Status: {payload.status} (type: {type(payload.status)}), Risk Level: {payload.risk_level} (type: {type(payload.risk_level)}), Currency: {payload.currency}")
            
            user_id = user.id if hasattr(user, 'id') else None
            user_org_id = user.org_id if hasattr(user, 'org_id') else None
            
            if not user_id or not user_org_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User must belong to an organization"
                )

            contract_id = await self._generate_contract_id(user_org_id)
            now = datetime.utcnow()
            
            logger.info(f"Generated contract_id: {contract_id} for org: {user_org_id}")

            # Fetch risk_level from opportunity if available
            final_risk_level = payload.risk_level
            if payload.opportunity_id:
                try:
                    opportunity_result = await self.db.execute(
                        select(Opportunity).where(
                            Opportunity.id == payload.opportunity_id,
                            Opportunity.org_id == user_org_id
                        )
                    )
                    opportunity = opportunity_result.scalar_one_or_none()
                    if opportunity and opportunity.risk_level:
                        # Map opportunity risk_level (low_risk, medium_risk, high_risk) to contract risk_level (low, medium, high)
                        opp_risk = opportunity.risk_level.value if hasattr(opportunity.risk_level, 'value') else str(opportunity.risk_level)
                        if opp_risk == 'low_risk':
                            final_risk_level = ContractRiskLevel.low
                        elif opp_risk == 'medium_risk':
                            final_risk_level = ContractRiskLevel.medium
                        elif opp_risk == 'high_risk':
                            final_risk_level = ContractRiskLevel.high
                        logger.info(f"Fetched risk_level from opportunity: {opp_risk} -> {final_risk_level}")
                except Exception as e:
                    logger.warning(f"Could not fetch risk_level from opportunity {payload.opportunity_id}: {e}")
                    # Continue with payload risk_level

            # Convert enum instances to their values for database insertion
            # SQLAlchemy needs the enum value (e.g., "awaiting-review") not the enum name (e.g., "awaiting_review")
            status_value = payload.status.value if isinstance(payload.status, ContractStatus) else payload.status
            risk_level_value = final_risk_level.value if isinstance(final_risk_level, ContractRiskLevel) else final_risk_level
            
            logger.info(f"Converted values - status_value: {status_value} (type: {type(status_value)}), risk_level_value: {risk_level_value} (type: {type(risk_level_value)})")
            
            contract = Contract(
                id=uuid.uuid4(),
                org_id=user_org_id,
                contract_id=contract_id,
                account_id=payload.account_id,
                opportunity_id=payload.opportunity_id,
                proposal_id=payload.proposal_id,
                project_id=payload.project_id,
                created_by=user_id,
                assigned_reviewer=payload.assigned_reviewer,
                client_name=payload.client_name,
                project_name=payload.project_name,
                document_type=payload.document_type,
                version=payload.version,
                status=status_value,
                risk_level=risk_level_value,
                contract_value=payload.contract_value,
                currency=payload.currency,
                start_date=payload.start_date,
                end_date=payload.end_date,
                upload_date=now,
                file_name=payload.file_name,
                file_size=payload.file_size,
                file_url=payload.file_url,
                terms_and_conditions=payload.terms_and_conditions,
                extra_metadata=payload.extra_metadata,
                created_at=now,
                updated_at=now,
            )

            logger.info(f"Adding contract to database - ID: {contract.id}, Contract ID: {contract.contract_id}")
            self.db.add(contract)
            await self.db.flush()
            logger.info("Contract flushed to database successfully")
            await self.db.refresh(contract)
            logger.info("Contract refreshed from database")

            return await self._contract_to_response(contract)
        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error creating contract: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create contract: {str(e)}"
            )

    async def create_from_proposal(
        self, payload: ContractFromProposalRequest, user: User
    ) -> ContractResponse:
        try:
            user_org_id = user.org_id if hasattr(user, 'org_id') else None
            if not user_org_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User must belong to an organization"
                )

            proposal = await self._get_proposal_for_org(payload.proposal_id, user_org_id)
            
            account_name = None
            if proposal.account_id:
                account_result = await self.db.execute(
                    select(Account.client_name).where(Account.account_id == proposal.account_id)
                )
                account_row = account_result.scalar_one_or_none()
                if account_row:
                    account_name = account_row

            contract_data = ContractCreate(
                account_id=proposal.account_id,
                opportunity_id=proposal.opportunity_id,
                proposal_id=proposal.id,
                client_name=account_name or proposal.title,
                project_name=proposal.title,
                document_type="Contract",
                status=ContractStatus.awaiting_review,
                risk_level=ContractRiskLevel.medium,
                contract_value=float(proposal.total_value) if proposal.total_value else None,
                currency=proposal.currency,
            )

            contract = await self.create_contract(contract_data, user)

            if payload.auto_analyze:
                await self.analyze_contract(contract.id, user)

            return contract
        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error creating contract from proposal: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create contract from proposal: {str(e)}"
            )

    async def list_contracts(
        self,
        org_id: uuid.UUID,
        page: int = 1,
        size: int = 10,
        status_filter: Optional[ContractStatus] = None,
        risk_filter: Optional[ContractRiskLevel] = None,
        search: Optional[str] = None,
    ) -> ContractListResponse:
        try:
            query = select(Contract).where(Contract.org_id == org_id)

            if status_filter:
                query = query.where(Contract.status == status_filter)
            if risk_filter:
                query = query.where(Contract.risk_level == risk_filter)
            if search:
                search_term = f"%{search}%"
                query = query.where(
                    or_(
                        Contract.client_name.ilike(search_term),
                        Contract.project_name.ilike(search_term),
                        Contract.contract_id.ilike(search_term),
                    )
                )

            total_result = await self.db.execute(
                select(func.count()).select_from(query.subquery())
            )
            total = total_result.scalar() or 0

            query = query.order_by(desc(Contract.created_at)).offset((page - 1) * size).limit(size)
            result = await self.db.execute(query)
            contracts = result.scalars().all()

            items = [await self._contract_to_list_item(c) for c in contracts]

            return ContractListResponse(
                items=items,
                total=total,
                page=page,
                size=size,
            )
        except Exception as e:
            logger.exception(f"Error listing contracts: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list contracts: {str(e)}"
            )

    async def get_contract(self, contract_id: uuid.UUID, org_id: uuid.UUID) -> ContractResponse:
        contract = await self._get_contract_for_org(contract_id, org_id)
        return await self._contract_to_response(contract)

    async def update_contract(
        self, contract_id: uuid.UUID, payload: ContractUpdate, org_id: uuid.UUID
    ) -> ContractResponse:
        try:
            contract = await self._get_contract_for_org(contract_id, org_id)

            update_data = payload.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                if hasattr(contract, key):
                    setattr(contract, key, value)

            contract.updated_at = datetime.utcnow()
            await self.db.flush()
            await self.db.refresh(contract)

            return await self._contract_to_response(contract)
        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error updating contract: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update contract: {str(e)}"
            )

    async def delete_contract(self, contract_id: uuid.UUID, org_id: uuid.UUID) -> None:
        try:
            contract = await self._get_contract_for_org(contract_id, org_id)
            await self.db.delete(contract)
            await self.db.flush()
        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error deleting contract: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete contract: {str(e)}"
            )

    async def analyze_contract(
        self, contract_id: uuid.UUID, user: User, force_reanalyze: bool = True
    ) -> ContractAnalysisResponse:
        """
        Analyze contract using AI (Gemini) to identify clauses, risks, and provide detailed analysis.
        Each contract gets its own separate analysis stored in extra_metadata.
        
        Args:
            contract_id: The contract ID to analyze
            user: The user performing the analysis
            force_reanalyze: If True, always re-analyze even if analysis exists. If False, return cached analysis.
        """
        try:
            user_org_id = user.org_id if hasattr(user, 'org_id') else None
            contract = await self._get_contract_for_org(contract_id, user_org_id)

            # Check if analysis already exists and we don't want to force re-analysis
            if not force_reanalyze:
                stored_analysis = None
                if contract.extra_metadata and isinstance(contract.extra_metadata, dict):
                    stored_analysis = contract.extra_metadata.get('ai_analysis')
                    if stored_analysis:
                        logger.info(f"Retrieving stored AI analysis for contract {contract_id}")
                        # Return stored analysis
                        analysis_items = [
                            ContractAnalysisItem(**item) for item in stored_analysis.get('items', [])
                        ]
                        stored_executive_summary = stored_analysis.get('executive_summary', None)
                        return ContractAnalysisResponse(
                            red_clauses=contract.red_clauses,
                            amber_clauses=contract.amber_clauses,
                            green_clauses=contract.green_clauses,
                            total_clauses=contract.total_clauses,
                            risk_level=contract.risk_level,
                            analysis=analysis_items,
                            executive_summary=stored_executive_summary if stored_executive_summary else None,
                        )
            
            logger.info(f"Starting AI analysis for contract {contract_id} (force_reanalyze={force_reanalyze})")

            # Fetch related opportunity and proposal data for comprehensive analysis
            opportunity_data = None
            proposal_data = None
            executive_summary = None
            
            if contract.opportunity_id:
                try:
                    opportunity_result = await self.db.execute(
                        select(Opportunity).where(
                            Opportunity.id == contract.opportunity_id,
                            Opportunity.org_id == user_org_id
                        )
                    )
                    opportunity = opportunity_result.scalar_one_or_none()
                    if opportunity:
                        opportunity_data = {
                            'project_name': opportunity.project_name,
                            'client_name': opportunity.client_name,
                            'description': opportunity.description,
                            'stage': opportunity.stage.value if hasattr(opportunity.stage, 'value') else str(opportunity.stage),
                            'risk_level': opportunity.risk_level.value if opportunity.risk_level and hasattr(opportunity.risk_level, 'value') else str(opportunity.risk_level) if opportunity.risk_level else None,
                            'project_value': float(opportunity.project_value) if opportunity.project_value else None,
                            'currency': opportunity.currency,
                            'market_sector': opportunity.market_sector,
                            'state': opportunity.state,
                            'deadline': opportunity.deadline.isoformat() if opportunity.deadline else None,
                        }
                        logger.info(f"Fetched opportunity data for contract {contract_id}")
                except Exception as e:
                    logger.warning(f"Failed to fetch opportunity data: {e}")
            
            if contract.proposal_id:
                try:
                    proposal_result = await self.db.execute(
                        select(Proposal).where(
                            Proposal.id == contract.proposal_id,
                            Proposal.org_id == user_org_id
                        )
                    )
                    proposal = proposal_result.scalar_one_or_none()
                    if proposal:
                        proposal_data = {
                            'title': proposal.title,
                            'summary': proposal.summary,
                            'status': proposal.status.value if hasattr(proposal.status, 'value') else str(proposal.status),
                            'total_value': float(proposal.total_value) if proposal.total_value else None,
                            'currency': proposal.currency,
                            'estimated_cost': float(proposal.estimated_cost) if proposal.estimated_cost else None,
                            'expected_margin': float(proposal.expected_margin) if proposal.expected_margin else None,
                            'fee_structure': proposal.fee_structure,
                            'due_date': proposal.due_date.isoformat() if proposal.due_date else None,
                            'submission_date': proposal.submission_date.isoformat() if proposal.submission_date else None,
                        }
                        logger.info(f"Fetched proposal data for contract {contract_id}")
                except Exception as e:
                    logger.warning(f"Failed to fetch proposal data: {e}")

            # Extract text from contract document
            contract_text = ""
            if contract.file_url:
                try:
                    # Download file from S3 or local storage
                    file_content = await self._download_contract_file(contract.file_url, contract.file_name)
                    if file_content:
                        contract_text = PDFExtractor.extract_text_from_file(file_content, contract.file_name or "contract.pdf")
                        contract_text = PDFExtractor.clean_text(contract_text, max_length=50000)
                        logger.info(f"Extracted {len(contract_text)} characters from contract document")
                except Exception as e:
                    logger.warning(f"Failed to extract text from contract document: {e}")

            # Also use terms_and_conditions if available
            if contract.terms_and_conditions:
                if contract_text:
                    contract_text += "\n\n" + contract.terms_and_conditions
                else:
                    contract_text = contract.terms_and_conditions

            # If no text available, try to generate basic analysis with available context
            if not contract_text or len(contract_text.strip()) < 50:
                logger.warning(f"No contract text available for analysis (contract {contract_id}), attempting analysis with available context")
                # Even without document text, we can still analyze based on contract metadata and context
                contract_text = f"Contract for {contract.client_name} - {contract.project_name}. Document Type: {contract.document_type}."
                if contract.contract_value:
                    contract_text += f" Contract Value: {contract.contract_value} {contract.currency}."
                if contract.start_date:
                    contract_text += f" Start Date: {contract.start_date}."
                if contract.end_date:
                    contract_text += f" End Date: {contract.end_date}."
                if contract.terms_and_conditions:
                    contract_text += f"\n\nTerms and Conditions: {contract.terms_and_conditions[:1000]}"
                
                # Use AI analysis even with limited text
                if len(contract_text.strip()) >= 50:
                    analysis_items, red_count, amber_count, green_count, risk_level, executive_summary = await self._analyze_with_ai(
                        contract_text, 
                        contract.client_name, 
                        contract.project_name, 
                        contract.document_type,
                        opportunity_data,
                        proposal_data,
                        contract
                    )
                    total_clauses = len(analysis_items)
                else:
                    # Fallback to basic analysis
                    analysis_items = []
                    if contract.terms_and_conditions:
                        analysis_items.append(
                            ContractAnalysisItem(
                                clauseTitle="Terms and Conditions",
                                detectedText=contract.terms_and_conditions[:200] + "...",
                                riskLevel="medium",
                                reasoning="General terms review - document text not available for detailed analysis",
                                location="Main document",
                                category="General",
                            )
                        )
                    
                    red_count = 0
                    amber_count = len(analysis_items)
                    green_count = 0
                    total_clauses = len(analysis_items)
                    risk_level = ContractRiskLevel.medium
                    executive_summary = "Basic analysis performed. Please upload contract document for comprehensive AI analysis."
            else:
                # Use Gemini AI for comprehensive analysis with opportunity and proposal context
                analysis_items, red_count, amber_count, green_count, risk_level, executive_summary = await self._analyze_with_ai(
                    contract_text, 
                    contract.client_name, 
                    contract.project_name, 
                    contract.document_type,
                    opportunity_data,
                    proposal_data,
                    contract
                )
                total_clauses = len(analysis_items)

            # Store analysis in extra_metadata
            if not contract.extra_metadata:
                contract.extra_metadata = {}
            
            # Ensure contract_text is defined (should always be, but safety check)
            contract_text_length = len(contract_text) if contract_text else 0
            
            analysis_metadata = {
                'items': [item.model_dump() for item in analysis_items],
                'analyzed_at': datetime.utcnow().isoformat(),
                'contract_text_length': contract_text_length,
                'opportunity_context': opportunity_data is not None,
                'proposal_context': proposal_data is not None,
                'executive_summary': executive_summary if executive_summary else '',
            }
            contract.extra_metadata['ai_analysis'] = analysis_metadata

            # Update contract with analysis results
            contract.red_clauses = red_count
            contract.amber_clauses = amber_count
            contract.green_clauses = green_count
            contract.total_clauses = total_clauses
            contract.risk_level = risk_level
            contract.updated_at = datetime.utcnow()

            await self.db.flush()
            # Refresh to ensure we have the latest data
            await self.db.refresh(contract)
            
            # Verify the analysis was saved
            if contract.extra_metadata and 'ai_analysis' in contract.extra_metadata:
                saved_items_count = len(contract.extra_metadata['ai_analysis'].get('items', []))
                logger.info(f"AI analysis saved: {saved_items_count} items stored in extra_metadata for contract {contract_id}")
            else:
                logger.warning(f"AI analysis may not have been saved properly for contract {contract_id}")

            logger.info(f"AI analysis completed for contract {contract_id}: {red_count} red, {amber_count} amber, {green_count} green clauses, {len(analysis_items)} total items")

            return ContractAnalysisResponse(
                red_clauses=red_count,
                amber_clauses=amber_count,
                green_clauses=green_count,
                total_clauses=total_clauses,
                risk_level=risk_level,
                analysis=analysis_items,
                executive_summary=executive_summary,
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error analyzing contract: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to analyze contract: {str(e)}"
            )

    async def _download_contract_file(self, file_url: str, file_name: Optional[str] = None) -> Optional[bytes]:
        """Download contract file from S3 or local storage"""
        try:
            # Check if it's an S3 URL
            if file_url.startswith('https://') and 's3' in file_url and 'amazonaws.com' in file_url:
                # Extract S3 key from URL
                # Format: https://bucket.s3.region.amazonaws.com/key
                try:
                    from urllib.parse import urlparse
                    parsed = urlparse(file_url)
                    path_parts = parsed.path.lstrip('/').split('/', 1)
                    if len(path_parts) == 2:
                        bucket = path_parts[0] if not parsed.netloc.startswith(path_parts[0]) else parsed.netloc.split('.')[0]
                        s3_key = path_parts[1]
                    else:
                        # Try to extract from netloc
                        bucket = parsed.netloc.split('.')[0]
                        s3_key = parsed.path.lstrip('/')
                    
                    s3_client = boto3.client(
                        's3',
                        aws_access_key_id=environment.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=environment.AWS_SECRET_ACCESS_KEY,
                        region_name=environment.AWS_S3_REGION or "us-east-1"
                    )
                    
                    response = s3_client.get_object(Bucket=bucket, Key=s3_key)
                    file_content = response['Body'].read()
                    logger.info(f"Downloaded contract file from S3: {s3_key}")
                    return file_content
                except Exception as e:
                    logger.warning(f"Failed to download from S3: {e}")
            
            # Try local file path
            if os.path.exists(file_url):
                with open(file_url, 'rb') as f:
                    return f.read()
            
            # Try HTTP download
            if file_url.startswith('http'):
                try:
                    import httpx
                    async with httpx.AsyncClient() as client:
                        response = await client.get(file_url, timeout=30.0)
                        if response.status_code == 200:
                            return response.content
                except ImportError:
                    # Fallback to requests if httpx not available
                    import requests
                    response = requests.get(file_url, timeout=30)
                    if response.status_code == 200:
                        return response.content
            
            logger.warning(f"Could not download contract file from {file_url}")
            return None
        except Exception as e:
            logger.error(f"Error downloading contract file: {e}")
            return None

    async def _analyze_with_ai(
        self, 
        contract_text: str, 
        client_name: str, 
        project_name: str, 
        document_type: str,
        opportunity_data: Optional[Dict[str, Any]] = None,
        proposal_data: Optional[Dict[str, Any]] = None,
        contract: Optional[Contract] = None
    ) -> tuple[List[ContractAnalysisItem], int, int, int, ContractRiskLevel, str]:
        """
        Use Gemini AI to analyze contract text and identify clauses, risks, and provide recommendations.
        Includes context from related opportunity and proposal for comprehensive analysis.
        Returns: (analysis_items, red_count, amber_count, green_count, risk_level)
        """
        try:
            from app.services.gemini_service import gemini_service
            import json
            import re
            
            if not gemini_service.enabled:
                logger.warning("Gemini AI not enabled, returning basic analysis")
                return self._get_basic_analysis(contract_text)

            # Build comprehensive context
            context_parts = []
            
            # Contract Information
            contract_info = f"""Contract Information:
- Client: {client_name}
- Project: {project_name}
- Document Type: {document_type}"""
            
            if contract:
                if contract.contract_value:
                    contract_info += f"\n- Contract Value: ${contract.contract_value:,.2f} {contract.currency}"
                if contract.start_date:
                    contract_info += f"\n- Start Date: {contract.start_date}"
                if contract.end_date:
                    contract_info += f"\n- End Date: {contract.end_date}"
                if contract.status:
                    contract_info += f"\n- Status: {contract.status.value if hasattr(contract.status, 'value') else str(contract.status)}"
            
            context_parts.append(contract_info)
            
            # Opportunity Context
            if opportunity_data:
                opp_context = "\n\nRelated Opportunity Information:"
                opp_context += f"\n- Project Name: {opportunity_data.get('project_name', 'N/A')}"
                opp_context += f"\n- Client Name: {opportunity_data.get('client_name', 'N/A')}"
                if opportunity_data.get('description'):
                    opp_context += f"\n- Description: {opportunity_data.get('description', '')[:500]}"
                if opportunity_data.get('stage'):
                    opp_context += f"\n- Stage: {opportunity_data.get('stage')}"
                if opportunity_data.get('risk_level'):
                    opp_context += f"\n- Risk Level: {opportunity_data.get('risk_level')}"
                if opportunity_data.get('project_value'):
                    opp_context += f"\n- Project Value: ${opportunity_data.get('project_value'):,.2f} {opportunity_data.get('currency', 'USD')}"
                if opportunity_data.get('market_sector'):
                    opp_context += f"\n- Market Sector: {opportunity_data.get('market_sector')}"
                if opportunity_data.get('state'):
                    opp_context += f"\n- State/Location: {opportunity_data.get('state')}"
                if opportunity_data.get('deadline'):
                    opp_context += f"\n- Deadline: {opportunity_data.get('deadline')}"
                context_parts.append(opp_context)
            
            # Proposal Context
            if proposal_data:
                prop_context = "\n\nRelated Proposal Information:"
                prop_context += f"\n- Title: {proposal_data.get('title', 'N/A')}"
                if proposal_data.get('summary'):
                    prop_context += f"\n- Summary: {proposal_data.get('summary', '')[:500]}"
                if proposal_data.get('status'):
                    prop_context += f"\n- Status: {proposal_data.get('status')}"
                if proposal_data.get('total_value'):
                    prop_context += f"\n- Total Value: ${proposal_data.get('total_value'):,.2f} {proposal_data.get('currency', 'USD')}"
                if proposal_data.get('estimated_cost'):
                    prop_context += f"\n- Estimated Cost: ${proposal_data.get('estimated_cost'):,.2f}"
                if proposal_data.get('expected_margin'):
                    prop_context += f"\n- Expected Margin: {proposal_data.get('expected_margin')}%"
                if proposal_data.get('fee_structure'):
                    fee_struct = proposal_data.get('fee_structure')
                    if isinstance(fee_struct, dict):
                        prop_context += f"\n- Fee Structure: {json.dumps(fee_struct, indent=2)}"
                    else:
                        prop_context += f"\n- Fee Structure: {str(fee_struct)}"
                if proposal_data.get('due_date'):
                    prop_context += f"\n- Due Date: {proposal_data.get('due_date')}"
                context_parts.append(prop_context)
            
            context = "\n".join(context_parts)

            prompt = f"""You are an expert contract analysis AI assistant. Perform a comprehensive analysis of the contract document, considering all related business context including the opportunity and proposal information.

{context}

Contract Document Text:
{contract_text[:40000]}

Perform a COMPREHENSIVE analysis considering:
1. The contract document itself (all clauses, terms, and provisions)
2. The related opportunity context (project scope, risk level, market sector, deadlines)
3. The related proposal context (proposed value, margins, fee structure, terms)
4. Alignment between what was proposed and what's in the contract
5. Financial terms consistency (compare proposal value vs contract value)
6. Risk assessment based on opportunity risk level and contract terms
7. Timeline alignment (proposal deadlines vs contract dates)

For each clause identified, provide:
1. Clause Title (e.g., "Payment Terms", "Liability Limitation", "Termination Clause")
2. Detected Text (the actual clause text from the document, up to 300 characters)
3. Risk Level: "red" (high risk - requires immediate attention), "amber" (medium risk - needs review), or "green" (low risk - acceptable)
4. Reasoning: Detailed explanation considering:
   - The clause itself and its implications
   - How it relates to the opportunity and proposal context
   - Financial impact and alignment with proposed terms
   - Risk factors based on opportunity risk level
   - Any discrepancies between proposal and contract terms
5. Location: Where in the document this clause appears (e.g., "Section 3.2", "Payment Terms Section", "General Terms")
6. Category: Type of clause (e.g., "Financial", "Legal", "Termination", "Liability", "Intellectual Property", "Confidentiality", "General")
7. Suggested Replacement (optional): If it's a risky clause, suggest better language aligned with the proposal and opportunity context

Focus on identifying:
- Unfavorable payment terms (compare with proposal payment structure)
- Excessive liability or indemnification clauses (especially given opportunity risk level)
- Unfair termination provisions
- Intellectual property concerns
- Confidentiality and data protection issues
- Force majeure and dispute resolution clauses
- Financial discrepancies (contract value vs proposal value, margin protection)
- Timeline risks (deadlines, delivery dates)
- Terms that deviate from industry standards or proposal commitments
- Terms that favor one party significantly over the other
- Alignment issues between opportunity scope and contract scope

Return ONLY a valid JSON object in this exact format:
{{
  "clauses": [
    {{
      "clauseTitle": "Clause Name",
      "detectedText": "Actual clause text from document...",
      "riskLevel": "red|amber|green",
      "reasoning": "Detailed explanation of the risk and concerns",
      "location": "Section X.Y or location description",
      "category": "Category name",
      "suggestedReplacement": "Optional suggested replacement text"
    }}
  ],
  "summary": {{
    "totalClauses": 10,
    "redCount": 2,
    "amberCount": 5,
    "greenCount": 3,
    "overallRiskLevel": "high|medium|low",
    "executiveSummary": {{
      "contractOverview": "Brief overview of the contract and key findings",
      "keyFinancialTerms": [
        "Payment terms: [details]",
        "Contract value: [amount]",
        "Other financial considerations"
      ],
      "criticalActionItems": [
        "URGENT: [high priority action]",
        "Review: [medium priority action]",
        "Consider: [recommendation]"
      ],
      "aiRecommendation": "Overall AI recommendation and next steps"
    }}
  }}
}}

Rules:
- Identify at least 5-15 clauses if the contract is substantial
- Be thorough and identify all significant clauses
- Use "red" for clauses that pose significant legal or financial risk
- Use "amber" for clauses that need review or negotiation
- Use "green" for standard, acceptable clauses
- Provide specific, actionable reasoning for each clause
- Extract actual text from the document for detectedText
- For executiveSummary.contractOverview: Provide a brief 2-3 sentence overview of the contract and main findings
- For executiveSummary.keyFinancialTerms: List 3-5 key financial terms including payment terms, contract value, and other financial considerations
- For executiveSummary.criticalActionItems: List 3-5 prioritized action items (use "URGENT:", "Review:", "Consider:" prefixes)
- For executiveSummary.aiRecommendation: Provide a 2-3 sentence overall recommendation and next steps
- Return ONLY the JSON object, no markdown formatting or explanations
"""

            response = await asyncio.to_thread(gemini_service.model.generate_content, prompt)
            response_text = response.text.strip()
            
            # Extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                ai_result = json.loads(json_match.group())
            else:
                # Try to parse directly
                ai_result = json.loads(response_text)
            
            clauses_data = ai_result.get('clauses', [])
            summary = ai_result.get('summary', {})
            executive_summary_raw = summary.get('executiveSummary', {})
            
            # Handle both string and structured format
            if isinstance(executive_summary_raw, str):
                # Legacy format - plain string
                executive_summary = executive_summary_raw
            elif isinstance(executive_summary_raw, dict):
                # Structured format - convert to formatted string
                contract_overview = executive_summary_raw.get('contractOverview', '')
                key_financial_terms = executive_summary_raw.get('keyFinancialTerms', [])
                critical_action_items = executive_summary_raw.get('criticalActionItems', [])
                ai_recommendation = executive_summary_raw.get('aiRecommendation', '')
                
                # Format as structured text
                parts = []
                if contract_overview:
                    parts.append(f"Contract Overview:\n{contract_overview}")
                if key_financial_terms:
                    parts.append(f"\nKey Financial Terms:\n" + "\n".join(f"• {term}" for term in key_financial_terms))
                if critical_action_items:
                    parts.append(f"\nCritical Action Items:\n" + "\n".join(f"• {item}" for item in critical_action_items))
                if ai_recommendation:
                    parts.append(f"\nAI Recommendation:\n{ai_recommendation}")
                
                executive_summary = "\n".join(parts)
            else:
                executive_summary = ''
            
            # Convert to ContractAnalysisItem objects
            analysis_items = []
            for clause_data in clauses_data:
                analysis_items.append(
                    ContractAnalysisItem(
                        clauseTitle=clause_data.get('clauseTitle', 'Unnamed Clause'),
                        detectedText=clause_data.get('detectedText', '')[:500],  # Limit text length
                        riskLevel=clause_data.get('riskLevel', 'amber'),
                        suggestedReplacement=clause_data.get('suggestedReplacement'),
                        reasoning=clause_data.get('reasoning', 'No reasoning provided'),
                        location=clause_data.get('location', 'Unknown'),
                        category=clause_data.get('category', 'General'),
                    )
                )
            
            # Get counts from summary or calculate from items
            red_count = summary.get('redCount', sum(1 for item in analysis_items if item.riskLevel == 'red'))
            amber_count = summary.get('amberCount', sum(1 for item in analysis_items if item.riskLevel == 'amber'))
            green_count = summary.get('greenCount', sum(1 for item in analysis_items if item.riskLevel == 'green'))
            
            # Determine overall risk level
            overall_risk = summary.get('overallRiskLevel', 'medium')
            if overall_risk == 'high' or red_count > amber_count + green_count:
                risk_level = ContractRiskLevel.high
            elif overall_risk == 'low' or green_count > red_count + amber_count:
                risk_level = ContractRiskLevel.low
            else:
                risk_level = ContractRiskLevel.medium
            
            logger.info(f"AI analysis completed: {len(analysis_items)} clauses identified ({red_count} red, {amber_count} amber, {green_count} green)")
            
            return analysis_items, red_count, amber_count, green_count, risk_level, executive_summary
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI analysis JSON: {e}")
            logger.error(f"Response text: {response_text[:500] if 'response_text' in locals() else 'N/A'}")
            return self._get_basic_analysis(contract_text)
        except Exception as e:
            logger.exception(f"Error in AI analysis: {e}")
            return self._get_basic_analysis(contract_text)

    def _get_basic_analysis(self, contract_text: str) -> tuple[List[ContractAnalysisItem], int, int, int, ContractRiskLevel, str]:
        """Fallback basic analysis when AI is not available"""
        analysis_items = []
        executive_summary = "Basic analysis performed. AI analysis is recommended for comprehensive contract review."
        
        if contract_text:
            # Simple keyword-based analysis
            text_lower = contract_text.lower()
            
            # Check for common risky terms
            risky_keywords = {
                'indemnification': ('red', 'Indemnification Clause', 'High risk indemnification language'),
                'liability': ('amber', 'Liability Clause', 'Liability terms need review'),
                'termination': ('amber', 'Termination Clause', 'Termination provisions'),
                'confidentiality': ('green', 'Confidentiality Clause', 'Standard confidentiality terms'),
                'payment': ('amber', 'Payment Terms', 'Payment terms and conditions'),
            }
            
            for keyword, (risk, title, reasoning) in risky_keywords.items():
                if keyword in text_lower:
                    # Find the relevant section
                    idx = text_lower.find(keyword)
                    start = max(0, idx - 50)
                    end = min(len(contract_text), idx + 200)
                    detected_text = contract_text[start:end]
                    
                    analysis_items.append(
                        ContractAnalysisItem(
                            clauseTitle=title,
                            detectedText=detected_text[:300],
                            riskLevel=risk,
                            reasoning=reasoning,
                            location="Document",
                            category="General",
                        )
                    )
        
        red_count = sum(1 for item in analysis_items if item.riskLevel == 'red')
        amber_count = sum(1 for item in analysis_items if item.riskLevel == 'amber')
        green_count = sum(1 for item in analysis_items if item.riskLevel == 'green')
        risk_level = ContractRiskLevel.medium
        
        return analysis_items, red_count, amber_count, green_count, risk_level, executive_summary

    async def extract_contract_details_from_file(
        self, file_content: bytes, filename: str, content_type: str
    ) -> Dict[str, Any]:
        """Extract contract details from uploaded file using AI"""
        try:
            # Extract text from file
            file_extension = filename.lower().split('.')[-1]
            text_content = ""
            
            if file_extension == 'pdf':
                text_content = PDFExtractor.extract_text_from_file(file_content, filename)
            elif file_extension in ['doc', 'docx']:
                text_content = PDFExtractor.extract_text_from_file(file_content, filename)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported file type: {file_extension}"
                )
            
            if not text_content or len(text_content.strip()) < 50:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Could not extract sufficient text from document. Please ensure the document is not scanned or corrupted."
                )
            
            # Use AI to extract structured data (simplified extraction for now)
            # In production, this would call an AI service like Gemini
            extracted_data = await self._extract_contract_fields_from_text(text_content)
            
            return {
                "client_name": extracted_data.get("client_name"),
                "project_name": extracted_data.get("project_name"),
                "contract_value": extracted_data.get("contract_value"),
                "start_date": extracted_data.get("start_date"),
                "end_date": extracted_data.get("end_date"),
                "document_type": extracted_data.get("document_type", "Professional Services Agreement"),
                "risk_level": extracted_data.get("risk_level", "medium"),
                "extracted_text_preview": text_content[:500] + "..." if len(text_content) > 500 else text_content,
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error extracting contract details: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to extract contract details: {str(e)}"
            )

    async def _extract_contract_fields_from_text(self, text: str) -> Dict[str, Any]:
        """Extract contract fields from text using pattern matching and AI if available"""
        extracted = {}
        
        # Simple pattern matching for common contract fields
        # Client/Party name patterns
        client_patterns = [
            r'client[:\s]+([A-Z][a-zA-Z\s&,]+)',
            r'between\s+([A-Z][a-zA-Z\s&,]+?)\s+and',
            r'party[:\s]+([A-Z][a-zA-Z\s&,]+)',
        ]
        for pattern in client_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                extracted["client_name"] = match.group(1).strip()[:100]
                break
        
        # Project name patterns
        project_patterns = [
            r'project[:\s]+([A-Z][a-zA-Z0-9\s\-&,]+?)(?:\n|\.|$)',
            r'services?\s+for\s+([A-Z][a-zA-Z0-9\s\-&,]+?)(?:\n|\.|$)',
        ]
        for pattern in project_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                extracted["project_name"] = match.group(1).strip()[:200]
                break
        
        # Contract value patterns
        value_patterns = [
            r'\$[\s]*([\d,]+\.?\d*)\s*(?:million|M|thousand|K)?',
            r'contract\s+value[:\s]*\$?\s*([\d,]+\.?\d*)',
            r'total[:\s]*\$?\s*([\d,]+\.?\d*)',
        ]
        for pattern in value_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value_str = match.group(1).replace(',', '')
                try:
                    value = float(value_str)
                    # Check if million or thousand indicator
                    if 'million' in match.group(0).lower() or 'M' in match.group(0).upper():
                        value *= 1000000
                    elif 'thousand' in match.group(0).lower() or 'K' in match.group(0).upper():
                        value *= 1000
                    extracted["contract_value"] = str(int(value))
                except ValueError:
                    pass
                break
        
        # Date patterns
        date_patterns = [
            r'(?:start|effective|commencement)\s+date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(?:end|expiration|termination)\s+date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        ]
        # This is simplified - in production would parse dates properly
        
        # Document type detection
        doc_type_keywords = {
            "Professional Services Agreement": ["professional services", "consulting agreement"],
            "Construction Contract": ["construction", "build", "contractor"],
            "Design-Build Agreement": ["design-build", "design build"],
            "Technology Services Agreement": ["technology", "software", "IT services"],
        }
        text_lower = text.lower()
        for doc_type, keywords in doc_type_keywords.items():
            if any(kw in text_lower for kw in keywords):
                extracted["document_type"] = doc_type
                break
        
        return extracted

    async def upload_contract_document(
        self, contract_id: uuid.UUID, file_content: bytes, filename: str, 
        content_type: str, org_id: uuid.UUID, user_id: uuid.UUID
    ) -> tuple[str, str]:
        """Upload contract document to storage and return file_path and file_url"""
        try:
            # Sanitize filename
            safe_filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)[:255]
            timestamp = int(datetime.utcnow().timestamp())
            storage_filename = f"{timestamp}_{safe_filename}"
            
            # Try S3 first
            s3_configured = all([
                environment.AWS_ACCESS_KEY_ID,
                environment.AWS_SECRET_ACCESS_KEY,
                environment.AWS_S3_BUCKET_NAME,
            ])
            
            file_path = None
            file_url = None
            
            if s3_configured:
                try:
                    s3_key = f"contracts/{contract_id}/{storage_filename}"
                    s3_client = boto3.client(
                        's3',
                        aws_access_key_id=environment.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=environment.AWS_SECRET_ACCESS_KEY,
                        region_name=environment.AWS_S3_REGION or "us-east-1"
                    )
                    s3_client.put_object(
                        Bucket=environment.AWS_S3_BUCKET_NAME,
                        Key=s3_key,
                        Body=file_content,
                        ContentType=content_type
                    )
                    region_segment = f".{environment.AWS_S3_REGION}" if environment.AWS_S3_REGION else ""
                    file_url = f"https://{environment.AWS_S3_BUCKET_NAME}.s3{region_segment}.amazonaws.com/{s3_key}"
                    file_path = s3_key
                    logger.info(f"Contract document uploaded to S3: {s3_key}")
                except ClientError as e:
                    logger.warning(f"S3 upload failed: {e}, falling back to local storage")
            
            # Fallback to local storage
            if not file_path:
                upload_root = os.path.join("uploads", "contract_documents")
                os.makedirs(upload_root, exist_ok=True)
                contract_dir = os.path.join(upload_root, str(contract_id))
                os.makedirs(contract_dir, exist_ok=True)
                local_path = os.path.join(contract_dir, storage_filename)
                
                with open(local_path, "wb") as f:
                    f.write(file_content)
                
                file_path = local_path
                api_base = getattr(environment, 'FRONTEND_URL', None) or "http://127.0.0.1:8000"
                if ":5173" in api_base:
                    api_base = api_base.replace(":5173", ":8000")
                file_url = f"{api_base}/uploads/contract_documents/{contract_id}/{storage_filename}"
                logger.info(f"Contract document saved locally: {local_path}")
            
            return file_path, file_url
            
        except Exception as e:
            logger.exception(f"Error uploading contract document: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload contract document: {str(e)}"
            )
    
    async def update_contract_file(
        self, contract_id: uuid.UUID, org_id: uuid.UUID, file_content: bytes, 
        filename: str, content_type: str, user_id: uuid.UUID
    ) -> ContractResponse:
        """Upload and attach a document to an existing contract"""
        try:
            contract = await self._get_contract_for_org(contract_id, org_id)
            
            # Upload file
            file_path, file_url = await self.upload_contract_document(
                contract_id,
                file_content,
                filename,
                content_type,
                org_id,
                user_id
            )
            
            # Update contract with file info
            contract.file_name = filename
            contract.file_size = f"{len(file_content)}"
            contract.file_url = file_url
            contract.updated_at = datetime.utcnow()
            
            await self.db.flush()
            await self.db.refresh(contract)
            
            return await self._contract_to_response(contract)
        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error updating contract file: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update contract file: {str(e)}"
            )

    async def _contract_to_response(self, contract: Contract) -> ContractResponse:
        account_name = None
        if contract.account_id:
            account_result = await self.db.execute(
                select(Account.client_name).where(Account.account_id == contract.account_id)
            )
            account_row = account_result.scalar_one_or_none()
            if account_row:
                account_name = account_row

        return ContractResponse(
            id=contract.id,
            org_id=contract.org_id,
            contract_id=contract.contract_id,
            account_id=contract.account_id,
            account_name=account_name,
            opportunity_id=contract.opportunity_id,
            proposal_id=contract.proposal_id,
            project_id=contract.project_id,
            created_by=contract.created_by,
            assigned_reviewer=contract.assigned_reviewer,
            client_name=contract.client_name,
            project_name=contract.project_name,
            document_type=contract.document_type,
            version=contract.version,
            status=contract.status,
            risk_level=contract.risk_level,
            contract_value=float(contract.contract_value) if contract.contract_value else None,
            currency=contract.currency,
            start_date=contract.start_date,
            end_date=contract.end_date,
            upload_date=contract.upload_date,
            execution_date=contract.execution_date,
            last_modified=contract.last_modified,
            file_name=contract.file_name,
            file_size=contract.file_size,
            file_url=contract.file_url,
            red_clauses=contract.red_clauses,
            amber_clauses=contract.amber_clauses,
            green_clauses=contract.green_clauses,
            total_clauses=contract.total_clauses,
            terms_and_conditions=contract.terms_and_conditions,
            extra_metadata=contract.extra_metadata,
            created_at=contract.created_at,
            updated_at=contract.updated_at,
        )

    async def _contract_to_list_item(self, contract: Contract) -> ContractListItem:
        return ContractListItem(
            id=contract.id,
            contract_id=contract.contract_id,
            client_name=contract.client_name,
            project_name=contract.project_name,
            document_type=contract.document_type,
            status=contract.status,
            risk_level=contract.risk_level,
            contract_value=float(contract.contract_value) if contract.contract_value else None,
            red_clauses=contract.red_clauses,
            amber_clauses=contract.amber_clauses,
            green_clauses=contract.green_clauses,
            total_clauses=contract.total_clauses,
            created_at=contract.created_at,
            updated_at=contract.updated_at,
        )

    async def get_contract_workflow(self, org_id: uuid.UUID, contract_id: Optional[uuid.UUID] = None) -> ContractWorkflowResponse:
        """Get workflow information for contracts, optionally filtered by contract_id"""
        try:
            from app.models.employee import Employee
            
            # Get contracts for workflow stats
            base_query = select(Contract).where(Contract.org_id == org_id)
            if contract_id:
                base_query = base_query.where(Contract.id == contract_id)
            
            result = await self.db.execute(base_query)
            contracts = result.scalars().all()
            
            # Calculate workflow stats
            total_contracts = len(contracts)
            
            # Calculate average cycle time (from upload to execution, or current date if not executed)
            cycle_times = []
            for contract in contracts:
                if contract.upload_date:
                    try:
                        end_date = contract.execution_date
                        if not end_date:
                            end_date = datetime.utcnow()
                        
                        # Handle timezone-aware and timezone-naive datetimes
                        if isinstance(contract.upload_date, datetime) and isinstance(end_date, datetime):
                            # If both are timezone-aware, ensure they're comparable
                            if contract.upload_date.tzinfo and not end_date.tzinfo:
                                end_date = end_date.replace(tzinfo=contract.upload_date.tzinfo)
                            elif not contract.upload_date.tzinfo and end_date.tzinfo:
                                end_date = end_date.replace(tzinfo=None)
                            
                            delta = end_date - contract.upload_date
                            cycle_times.append(delta.total_seconds() / (24 * 3600))  # Convert to days
                    except Exception as e:
                        logger.debug(f"Error calculating cycle time for contract {contract.id}: {e}")
                        continue
            
            avg_cycle_time = sum(cycle_times) / len(cycle_times) if cycle_times else 0.0
            ai_target = max(0.0, avg_cycle_time * 0.75) if avg_cycle_time > 0 else 6.1  # AI target is 25% faster, or default 6.1
            
            # Calculate assignment accuracy (contracts with assigned reviewers)
            assigned_count = sum(1 for c in contracts if c.assigned_reviewer is not None)
            assignment_accuracy = (assigned_count / total_contracts * 100) if total_contracts > 0 else 0.0
            
            # Contracts by status
            contracts_by_status = {}
            for status_enum in ContractStatus:
                status_value = status_enum.value if hasattr(status_enum, 'value') else str(status_enum)
                count = 0
                for c in contracts:
                    # Handle both enum and string status values
                    contract_status_value = c.status.value if hasattr(c.status, 'value') else str(c.status)
                    if contract_status_value == status_value:
                        count += 1
                contracts_by_status[status_value] = count
            
            workflow_stats = WorkflowStats(
                average_cycle_time_days=round(avg_cycle_time, 1),
                ai_target_cycle_time_days=round(ai_target, 1),
                assignment_accuracy_percent=round(assignment_accuracy, 1),
                total_contracts=total_contracts,
                contracts_by_status=contracts_by_status,
            )
            
            # Get workflow steps based on contract status (if contract_id provided)
            workflow_steps = []
            if contract_id and contracts:
                contract = contracts[0]
                # Get contract status as string value for comparison
                contract_status_value = contract.status.value if hasattr(contract.status, 'value') else str(contract.status)
                
                status_to_steps = {
                    'awaiting-review': [
                        {'step': 1, 'title': 'Document Upload', 'description': 'AI analysis triggers automatically', 'status': 'completed'},
                        {'step': 2, 'title': 'Initial AI Review', 'description': 'Risk assessment and clause identification', 'status': 'in-progress'},
                        {'step': 3, 'title': 'Legal Review', 'description': 'Attorney review of high-risk items', 'status': 'pending'},
                        {'step': 4, 'title': 'Exception Approval', 'description': 'Management approval of proposed exceptions', 'status': 'pending'},
                        {'step': 5, 'title': 'Client Negotiation', 'description': 'Submit exceptions and negotiate terms', 'status': 'pending'},
                    ],
                    'in-legal-review': [
                        {'step': 1, 'title': 'Document Upload', 'description': 'AI analysis triggers automatically', 'status': 'completed'},
                        {'step': 2, 'title': 'Initial AI Review', 'description': 'Risk assessment and clause identification', 'status': 'completed'},
                        {'step': 3, 'title': 'Legal Review', 'description': 'Attorney review of high-risk items', 'status': 'in-progress'},
                        {'step': 4, 'title': 'Exception Approval', 'description': 'Management approval of proposed exceptions', 'status': 'pending'},
                        {'step': 5, 'title': 'Client Negotiation', 'description': 'Submit exceptions and negotiate terms', 'status': 'pending'},
                    ],
                    'exceptions-approved': [
                        {'step': 1, 'title': 'Document Upload', 'description': 'AI analysis triggers automatically', 'status': 'completed'},
                        {'step': 2, 'title': 'Initial AI Review', 'description': 'Risk assessment and clause identification', 'status': 'completed'},
                        {'step': 3, 'title': 'Legal Review', 'description': 'Attorney review of high-risk items', 'status': 'completed'},
                        {'step': 4, 'title': 'Exception Approval', 'description': 'Management approval of proposed exceptions', 'status': 'completed'},
                        {'step': 5, 'title': 'Client Negotiation', 'description': 'Submit exceptions and negotiate terms', 'status': 'in-progress'},
                    ],
                    'negotiating': [
                        {'step': 1, 'title': 'Document Upload', 'description': 'AI analysis triggers automatically', 'status': 'completed'},
                        {'step': 2, 'title': 'Initial AI Review', 'description': 'Risk assessment and clause identification', 'status': 'completed'},
                        {'step': 3, 'title': 'Legal Review', 'description': 'Attorney review of high-risk items', 'status': 'completed'},
                        {'step': 4, 'title': 'Exception Approval', 'description': 'Management approval of proposed exceptions', 'status': 'completed'},
                        {'step': 5, 'title': 'Client Negotiation', 'description': 'Submit exceptions and negotiate terms', 'status': 'in-progress'},
                    ],
                    'executed': [
                        {'step': 1, 'title': 'Document Upload', 'description': 'AI analysis triggers automatically', 'status': 'completed'},
                        {'step': 2, 'title': 'Initial AI Review', 'description': 'Risk assessment and clause identification', 'status': 'completed'},
                        {'step': 3, 'title': 'Legal Review', 'description': 'Attorney review of high-risk items', 'status': 'completed'},
                        {'step': 4, 'title': 'Exception Approval', 'description': 'Management approval of proposed exceptions', 'status': 'completed'},
                        {'step': 5, 'title': 'Client Negotiation', 'description': 'Submit exceptions and negotiate terms', 'status': 'completed'},
                    ],
                }
                
                steps_data = status_to_steps.get(contract_status_value, status_to_steps['awaiting-review'])
                workflow_steps = [WorkflowStep(**step) for step in steps_data]
            else:
                # Default workflow steps
                workflow_steps = [
                    WorkflowStep(step=1, title='Document Upload', description='AI analysis triggers automatically', status='completed'),
                    WorkflowStep(step=2, title='Initial AI Review', description='Risk assessment and clause identification', status='completed'),
                    WorkflowStep(step=3, title='Legal Review', description='Attorney review of high-risk items', status='in-progress'),
                    WorkflowStep(step=4, title='Exception Approval', description='Management approval of proposed exceptions', status='pending'),
                    WorkflowStep(step=5, title='Client Negotiation', description='Submit exceptions and negotiate terms', status='pending'),
                ]
            
            # Get reviewers (users in the organization, preferably legal department/role)
            users_result = await self.db.execute(
                select(User).where(User.org_id == org_id).limit(50)
            )
            users = users_result.scalars().all()
            
            reviewers = []
            legal_keywords = ['legal', 'counsel', 'attorney', 'lawyer', 'compliance']
            
            for user in users:
                try:
                    # Get name from email or user name
                    if user.email:
                        name = user.email.split('@')[0].replace('.', ' ').replace('_', ' ').title()
                    else:
                        name = user.name or 'Unknown User'
                    
                    role = user.role or ''
                    
                    # Try to get employee info for name and check if legal
                    try:
                        employee_result = await self.db.execute(
                            select(Employee).where(Employee.user_id == user.id).limit(1)
                        )
                        employee = employee_result.scalar_one_or_none()
                        
                        if employee:
                            if hasattr(employee, 'first_name') and hasattr(employee, 'last_name'):
                                if employee.first_name or employee.last_name:
                                    name = f"{employee.first_name or ''} {employee.last_name or ''}".strip()
                            
                            # Get role/designation
                            employee_role = None
                            if hasattr(employee, 'job_title') and employee.job_title:
                                employee_role = employee.job_title
                            elif hasattr(employee, 'role') and employee.role:
                                employee_role = employee.role
                            
                            if employee_role:
                                role = employee_role
                            
                            # Check if employee is in legal department
                            if hasattr(employee, 'department') and employee.department:
                                dept_lower = str(employee.department).lower()
                                if any(keyword in dept_lower for keyword in legal_keywords):
                                    role = f"{role} (Legal)" if role else "Legal"
                    except Exception as e:
                        # If employee lookup fails, continue with user data only
                        logger.debug(f"Could not fetch employee for user {user.id}: {e}")
                    
                    reviewer_info = ReviewerInfo(
                        id=user.id,
                        name=name,
                        email=user.email or '',
                        role=role,
                    )
                    reviewers.append(reviewer_info)
                except Exception as e:
                    logger.warning(f"Error processing reviewer {user.id if user else 'unknown'}: {e}")
                    continue
            
            # Sort: legal reviewers first, then others
            legal_keywords_lower = [kw.lower() for kw in legal_keywords]
            def get_reviewer_priority(reviewer: ReviewerInfo) -> int:
                role_str = (reviewer.role or '').lower()
                return 0 if any(keyword in role_str for keyword in legal_keywords_lower) else 1
            
            reviewers.sort(key=get_reviewer_priority)
            
            # Approval authority rules (based on contract value)
            approval_rules = [
                "Director Level: < $1M contracts",
                "VP Level: $1M - $5M contracts",
                "CEO Level: > $5M contracts",
            ]
            
            # AI Automation rules
            ai_automation_rules = [
                "Auto-assign high risk contracts to senior counsel",
                "AI-triggered escalation after 48 hours",
                "Auto-generate exception templates from clause library",
                "Smart routing based on contract type and value",
                "Predictive workflow optimization suggestions",
            ]
            
            return ContractWorkflowResponse(
                workflow_steps=workflow_steps,
                reviewers=reviewers,
                approval_authority_rules=approval_rules,
                ai_automation_rules=ai_automation_rules,
                workflow_stats=workflow_stats,
            )
        except Exception as e:
            logger.exception(f"Error getting contract workflow: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get contract workflow: {str(e)}"
            )


class ClauseLibraryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_clauses(
        self,
        org_id: uuid.UUID,
        page: int = 1,
        size: int = 10,
        category: Optional[str] = None,
        search: Optional[str] = None,
    ) -> ClauseLibraryListResponse:
        try:
            query = select(ClauseLibraryItem).where(ClauseLibraryItem.org_id == org_id)

            if category:
                query = query.where(ClauseLibraryItem.category == category)
            if search:
                search_term = f"%{search}%"
                query = query.where(
                    or_(
                        ClauseLibraryItem.title.ilike(search_term),
                        ClauseLibraryItem.clause_text.ilike(search_term),
                    )
                )

            total_result = await self.db.execute(
                select(func.count()).select_from(query.subquery())
            )
            total = total_result.scalar() or 0

            query = query.order_by(desc(ClauseLibraryItem.created_at)).offset((page - 1) * size).limit(size)
            result = await self.db.execute(query)
            clauses = result.scalars().all()

            items = [
                ClauseLibraryResponse(
                    id=c.id,
                    title=c.title,
                    category=c.category,
                    clause_text=c.clause_text,
                    acceptable_alternatives=c.acceptable_alternatives or [],
                    fallback_positions=c.fallback_positions or [],
                    risk_level=c.risk_level,
                    created_at=c.created_at,
                    updated_at=c.updated_at,
                )
                for c in clauses
            ]

            return ClauseLibraryListResponse(items=items, total=total, page=page, size=size)
        except Exception as e:
            logger.exception(f"Error listing clauses: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list clauses: {str(e)}"
            )

    async def get_clause(self, clause_id: uuid.UUID, org_id: uuid.UUID) -> ClauseLibraryResponse:
        clause = await self.db.get(ClauseLibraryItem, clause_id)
        if not clause or clause.org_id != org_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Clause not found or access denied"
            )

        return ClauseLibraryResponse(
            id=clause.id,
            title=clause.title,
            category=clause.category,
            clause_text=clause.clause_text,
            acceptable_alternatives=clause.acceptable_alternatives or [],
            fallback_positions=clause.fallback_positions or [],
            risk_level=clause.risk_level,
            created_at=clause.created_at,
            updated_at=clause.updated_at,
        )

    async def create_clause(
        self, payload: ClauseLibraryCreate, user: User
    ) -> ClauseLibraryResponse:
        try:
            user_org_id = user.org_id if hasattr(user, 'org_id') else None
            if not user_org_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User must belong to an organization"
                )

            # Ensure default categories exist before creating clause
            await self._ensure_default_categories(user_org_id)

            clause = ClauseLibraryItem(
                id=uuid.uuid4(),
                org_id=user_org_id,
                title=payload.title,
                category=payload.category,
                clause_text=payload.clause_text,
                acceptable_alternatives=payload.acceptable_alternatives,
                fallback_positions=payload.fallback_positions,
                risk_level=payload.risk_level,
                created_by=user.id if hasattr(user, 'id') else None,
                version=1,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            self.db.add(clause)
            await self.db.flush()
            await self.db.refresh(clause)

            return ClauseLibraryResponse(
                id=clause.id,
                title=clause.title,
                category=clause.category,
                clause_text=clause.clause_text,
                acceptable_alternatives=clause.acceptable_alternatives or [],
                fallback_positions=clause.fallback_positions or [],
                risk_level=clause.risk_level,
                created_at=clause.created_at,
                updated_at=clause.updated_at,
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error creating clause: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create clause: {str(e)}"
            )

    async def update_clause(
        self, clause_id: uuid.UUID, payload: ClauseLibraryUpdate, org_id: uuid.UUID
    ) -> ClauseLibraryResponse:
        try:
            clause = await self.db.get(ClauseLibraryItem, clause_id)
            if not clause or clause.org_id != org_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Clause not found or access denied"
                )

            update_data = payload.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                if hasattr(clause, key):
                    setattr(clause, key, value)

            clause.version += 1
            clause.updated_at = datetime.utcnow()
            await self.db.flush()
            await self.db.refresh(clause)

            return ClauseLibraryResponse(
                id=clause.id,
                title=clause.title,
                category=clause.category,
                clause_text=clause.clause_text,
                acceptable_alternatives=clause.acceptable_alternatives or [],
                fallback_positions=clause.fallback_positions or [],
                risk_level=clause.risk_level,
                created_at=clause.created_at,
                updated_at=clause.updated_at,
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error updating clause: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update clause: {str(e)}"
            )

    async def delete_clause(self, clause_id: uuid.UUID, org_id: uuid.UUID) -> None:
        try:
            clause = await self.db.get(ClauseLibraryItem, clause_id)
            if not clause or clause.org_id != org_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Clause not found or access denied"
                )
            await self.db.delete(clause)
            await self.db.flush()
        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error deleting clause: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete clause: {str(e)}"
            )

    async def _ensure_default_categories(self, org_id: uuid.UUID) -> None:
        """Ensure all default categories exist for an organization. Creates missing ones."""
        DEFAULT_CATEGORIES = [
            {'name': 'Risk Management', 'description': 'Clauses related to risk allocation, indemnification, and liability'},
            {'name': 'Financial', 'description': 'Payment terms, pricing, invoicing, and financial obligations'},
            {'name': 'Intellectual Property', 'description': 'IP ownership, licensing, and protection clauses'},
            {'name': 'Termination', 'description': 'Termination rights, notice periods, and exit conditions'},
            {'name': 'Confidentiality', 'description': 'NDA, confidentiality, and data protection clauses'},
            {'name': 'Service Level', 'description': 'SLA, performance metrics, and service delivery standards'},
            {'name': 'Warranty', 'description': 'Warranties, guarantees, and disclaimers'},
            {'name': 'Limitation of Liability', 'description': 'Liability caps, exclusions, and damage limitations'},
            {'name': 'Dispute Resolution', 'description': 'Arbitration, mediation, and governing law clauses'},
            {'name': 'Force Majeure', 'description': 'Force majeure events and excusable delays'},
            {'name': 'Change Management', 'description': 'Change orders, scope modifications, and amendments'},
            {'name': 'Compliance', 'description': 'Regulatory compliance, certifications, and standards'},
        ]
        
        try:
            # Get existing categories for this org
            result = await self.db.execute(
                select(ClauseCategory).where(ClauseCategory.org_id == org_id)
            )
            existing_categories = {cat.name.lower() for cat in result.scalars().all()}
            
            # Create missing categories
            for category_data in DEFAULT_CATEGORIES:
                category_name_lower = category_data['name'].lower()
                
                if category_name_lower not in existing_categories:
                    category = ClauseCategory(
                        id=uuid.uuid4(),
                        org_id=org_id,
                        name=category_data['name'],
                        description=category_data['description'],
                        created_by=None,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                    )
                    self.db.add(category)
                    logger.info(f"Auto-created missing category '{category_data['name']}' for org {org_id}")
            
            # Flush to make categories available in current transaction
            await self.db.flush()
        except Exception as e:
            logger.warning(f"Error ensuring default categories: {e}")
            # Don't fail if we can't create categories, just log it

    async def list_categories(self, org_id: uuid.UUID) -> List[ClauseCategoryResponse]:
        try:
            # Ensure default categories exist before listing
            await self._ensure_default_categories(org_id)
            
            result = await self.db.execute(
                select(ClauseCategory)
                .where(ClauseCategory.org_id == org_id)
                .order_by(ClauseCategory.name)
            )
            categories = result.scalars().all()

            return [
                ClauseCategoryResponse(
                    id=c.id,
                    name=c.name,
                    description=c.description,
                    created_at=c.created_at,
                    updated_at=c.updated_at,
                )
                for c in categories
            ]
        except Exception as e:
            logger.exception(f"Error listing categories: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list categories: {str(e)}"
            )

    async def create_category(
        self, payload: ClauseCategoryCreate, user: User
    ) -> ClauseCategoryResponse:
        try:
            user_org_id = user.org_id if hasattr(user, 'org_id') else None
            if not user_org_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User must belong to an organization"
                )

            category = ClauseCategory(
                id=uuid.uuid4(),
                org_id=user_org_id,
                name=payload.name,
                description=payload.description,
                created_by=user.id if hasattr(user, 'id') else None,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            self.db.add(category)
            await self.db.flush()
            await self.db.refresh(category)

            return ClauseCategoryResponse(
                id=category.id,
                name=category.name,
                description=category.description,
                created_at=category.created_at,
                updated_at=category.updated_at,
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error creating category: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create category: {str(e)}"
            )

