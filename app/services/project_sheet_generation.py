"""
Project Sheet Generation Service
AI-powered document generation for accounts with historical data processing
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.account import Account
from app.models.opportunity import Opportunity
from app.models.account_note import AccountNote
from app.models.contact import Contact
from app.models.account_document import AccountDocument
from app.services.ai_suggestions import AISuggestionService
from app.db.session import get_request_transaction
from app.utils.logger import logger


class ProjectSheetGenerationService:
    """Service for generating project sheets and proposals from account data"""
    
    def __init__(self):
        self.ai_service = AISuggestionService()
    
    async def generate_project_sheet(
        self,
        account_id: UUID,
        org_id: UUID,
        template_type: str = "comprehensive",  # "comprehensive", "executive", "technical", "financial"
        include_history: bool = True
    ) -> Dict[str, Any]:
        """
        Generate AI-powered project sheet/document for an account
        
        Returns:
            - document_content: Generated document content
            - sections: Document sections
            - metadata: Document metadata
        """
        db = get_request_transaction()
        
        try:
            # Get account with all relationships
            account_stmt = select(Account).where(
                and_(
                    Account.account_id == account_id,
                    Account.org_id == org_id
                )
            )
            result = await db.execute(account_stmt)
            account = result.scalar_one_or_none()
            
            if not account:
                raise ValueError(f"Account {account_id} not found")
            
            # Collect account data
            account_data = await self._collect_account_data(account, db, include_history)
            
            # Generate document based on template type
            if template_type == "executive":
                document = await self._generate_executive_summary(account, account_data)
            elif template_type == "technical":
                document = await self._generate_technical_sheet(account, account_data)
            elif template_type == "financial":
                document = await self._generate_financial_sheet(account, account_data)
            else:
                document = await self._generate_comprehensive_sheet(account, account_data)
            
            return {
                "account_id": str(account_id),
                "account_name": account.client_name,
                "template_type": template_type,
                "document_content": document["content"],
                "sections": document["sections"],
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "data_points_used": account_data["data_points_count"],
                    "includes_history": include_history
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating project sheet: {e}", exc_info=True)
            raise
    
    async def _collect_account_data(
        self,
        account: Account,
        db: AsyncSession,
        include_history: bool
    ) -> Dict[str, Any]:
        """Collect all relevant account data for document generation"""
        
        # Get opportunities
        opps_stmt = select(Opportunity).where(Opportunity.account_id == account.account_id)
        opps_result = await db.execute(opps_stmt)
        opportunities = list(opps_result.scalars().all())
        
        # Get contacts
        contacts_stmt = select(Contact).where(Contact.account_id == account.account_id)
        contacts_result = await db.execute(contacts_stmt)
        contacts = list(contacts_result.scalars().all())
        
        # Get notes (recent or all)
        notes_stmt = select(AccountNote).where(AccountNote.account_id == account.account_id)
        if not include_history:
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            notes_stmt = notes_stmt.where(AccountNote.created_at >= thirty_days_ago)
        notes_stmt = notes_stmt.order_by(AccountNote.created_at.desc()).limit(20)
        notes_result = await db.execute(notes_stmt)
        notes = list(notes_result.scalars().all())
        
        # Get documents
        docs_stmt = select(AccountDocument).where(AccountDocument.account_id == account.account_id)
        docs_result = await db.execute(docs_stmt)
        documents = list(docs_result.scalars().all())
        
        return {
            "account": {
                "name": account.client_name,
                "type": account.client_type.value if account.client_type else None,
                "market_sector": account.market_sector,
                "website": account.company_website,
                "hosting_area": account.hosting_area,
                "health_score": float(account.ai_health_score or 0),
                "risk_level": account.risk_level,
                "total_value": float(account.total_value or 0),
                "approval_status": account.approval_status
            },
            "opportunities": [
                {
                    "title": opp.title if hasattr(opp, 'title') else f"Opportunity {opp.id}",
                    "value": float(opp.project_value or 0),
                    "status": opp.status if hasattr(opp, 'status') else "unknown",
                    "created_at": opp.created_at.isoformat() if opp.created_at else None
                }
                for opp in opportunities
            ],
            "contacts": [
                {
                    "name": contact.name,
                    "email": contact.email,
                    "phone": contact.phone,
                    "title": contact.title
                }
                for contact in contacts
            ],
            "notes": [
                {
                    "title": note.title,
                    "content": note.content[:200],  # Truncate for summary
                    "date": note.date.isoformat() if note.date else None
                }
                for note in notes
            ],
            "documents": [
                {
                    "name": doc.name,
                    "category": doc.category,
                    "date": doc.date.isoformat() if doc.date else None
                }
                for doc in documents
            ],
            "data_points_count": len(opportunities) + len(contacts) + len(notes) + len(documents)
        }
    
    async def _generate_comprehensive_sheet(
        self,
        account: Account,
        account_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive project sheet"""
        
        # Build AI prompt
        prompt = f"""
        Generate a comprehensive project sheet for account: {account.client_name}
        
        Account Information:
        - Type: {account_data['account']['type']}
        - Market Sector: {account_data['account']['market_sector']}
        - Health Score: {account_data['account']['health_score']}
        - Risk Level: {account_data['account']['risk_level']}
        - Total Value: ${account_data['account']['total_value']:,.2f}
        
        Opportunities ({len(account_data['opportunities'])}):
        {self._format_opportunities(account_data['opportunities'])}
        
        Contacts ({len(account_data['contacts'])}):
        {self._format_contacts(account_data['contacts'])}
        
        Recent Notes ({len(account_data['notes'])}):
        {self._format_notes(account_data['notes'])}
        
        Create a professional project sheet with the following sections:
        1. Executive Summary
        2. Account Overview
        3. Opportunity Analysis
        4. Key Contacts
        5. Recent Activity
        6. Recommendations
        7. Next Steps
        
        Format as structured markdown with clear headings and bullet points.
        """
        
        try:
            from app.schemas.ai_suggestions import AISuggestionRequest
            request = AISuggestionRequest(
                context=prompt,
                suggestion_type="project_sheet_generation"
            )
            ai_response_obj = await self.ai_service.get_suggestions(request)
            ai_content = ai_response_obj.suggestion if ai_response_obj else None
        except Exception as e:
            logger.warning(f"AI generation failed, using template: {e}")
            ai_content = self._generate_template_sheet(account, account_data)
        
        sections = self._parse_sections(ai_content)
        
        return {
            "content": ai_content,
            "sections": sections
        }
    
    async def _generate_executive_summary(
        self,
        account: Account,
        account_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate executive summary sheet"""
        
        prompt = f"""
        Generate an executive summary for account: {account.client_name}
        
        Key Metrics:
        - Health Score: {account_data['account']['health_score']}
        - Total Value: ${account_data['account']['total_value']:,.2f}
        - Active Opportunities: {len(account_data['opportunities'])}
        - Key Contacts: {len(account_data['contacts'])}
        
        Create a concise executive summary (1-2 pages) covering:
        1. Account Status
        2. Key Metrics
        3. Strategic Value
        4. Risk Assessment
        5. Recommendations
        """
        
        try:
            from app.schemas.ai_suggestions import AISuggestionRequest
            request = AISuggestionRequest(
                context=prompt,
                suggestion_type="executive_summary"
            )
            ai_response_obj = await self.ai_service.get_suggestions(request)
            ai_content = ai_response_obj.suggestion if ai_response_obj else None
            if not ai_content:
                raise ValueError("AI service returned empty response")
        except Exception as e:
            logger.warning(f"AI generation failed: {e}")
            ai_content = f"# Executive Summary: {account.client_name}\n\nAccount Status: {account_data['account']['approval_status']}\nHealth Score: {account_data['account']['health_score']}\nTotal Value: ${account_data['account']['total_value']:,.2f}"
        
        return {
            "content": ai_content,
            "sections": ["Executive Summary", "Key Metrics", "Recommendations"]
        }
    
    async def _generate_technical_sheet(
        self,
        account: Account,
        account_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate technical project sheet"""
        
        prompt = f"""
        Generate a technical project sheet for account: {account.client_name}
        
        Focus on:
        - Technical requirements
        - Implementation details
        - Resource needs
        - Timeline considerations
        - Technical risks
        
        Account Data:
        {self._format_opportunities(account_data['opportunities'])}
        """
        
        try:
            from app.schemas.ai_suggestions import AISuggestionRequest
            request = AISuggestionRequest(
                context=prompt,
                suggestion_type="technical_sheet"
            )
            ai_response_obj = await self.ai_service.get_suggestions(request)
            ai_content = ai_response_obj.suggestion if ai_response_obj else None
            if not ai_content:
                raise ValueError("AI service returned empty response")
        except Exception as e:
            logger.warning(f"AI generation failed: {e}")
            ai_content = f"# Technical Sheet: {account.client_name}\n\nTechnical requirements and implementation details."
        
        return {
            "content": ai_content,
            "sections": ["Technical Requirements", "Implementation Plan", "Resource Needs"]
        }
    
    async def _generate_financial_sheet(
        self,
        account: Account,
        account_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate financial project sheet"""
        
        total_opp_value = sum(opp['value'] for opp in account_data['opportunities'])
        
        prompt = f"""
        Generate a financial project sheet for account: {account.client_name}
        
        Financial Data:
        - Account Total Value: ${account_data['account']['total_value']:,.2f}
        - Opportunity Value: ${total_opp_value:,.2f}
        - Opportunities: {len(account_data['opportunities'])}
        
        Include:
        1. Financial Overview
        2. Revenue Projections
        3. Cost Analysis
        4. ROI Projections
        5. Financial Risks
        """
        
        try:
            from app.schemas.ai_suggestions import AISuggestionRequest
            request = AISuggestionRequest(
                context=prompt,
                suggestion_type="financial_sheet"
            )
            ai_response_obj = await self.ai_service.get_suggestions(request)
            ai_content = ai_response_obj.suggestion if ai_response_obj else None
            if not ai_content:
                raise ValueError("AI service returned empty response")
        except Exception as e:
            logger.warning(f"AI generation failed: {e}")
            ai_content = f"# Financial Sheet: {account.client_name}\n\nTotal Value: ${account_data['account']['total_value']:,.2f}\nOpportunity Value: ${total_opp_value:,.2f}"
        
        return {
            "content": ai_content,
            "sections": ["Financial Overview", "Revenue Projections", "Cost Analysis"]
        }
    
    def _format_opportunities(self, opportunities: List[Dict]) -> str:
        """Format opportunities for prompt"""
        if not opportunities:
            return "No opportunities"
        return "\n".join([
            f"- {opp['title']}: ${opp['value']:,.2f} ({opp['status']})"
            for opp in opportunities[:10]
        ])
    
    def _format_contacts(self, contacts: List[Dict]) -> str:
        """Format contacts for prompt"""
        if not contacts:
            return "No contacts"
        return "\n".join([
            f"- {contact['name']} ({contact['title']}): {contact['email']}"
            for contact in contacts[:10]
        ])
    
    def _format_notes(self, notes: List[Dict]) -> str:
        """Format notes for prompt"""
        if not notes:
            return "No recent notes"
        return "\n".join([
            f"- {note['title']}: {note['content']}"
            for note in notes[:5]
        ])
    
    def _generate_template_sheet(
        self,
        account: Account,
        account_data: Dict[str, Any]
    ) -> str:
        """Generate template-based sheet when AI fails"""
        return f"""# Project Sheet: {account.client_name}

## Executive Summary
Account Type: {account_data['account']['type']}
Market Sector: {account_data['account']['market_sector']}
Health Score: {account_data['account']['health_score']}
Risk Level: {account_data['account']['risk_level']}

## Opportunities
Total Opportunities: {len(account_data['opportunities'])}
Total Value: ${sum(opp['value'] for opp in account_data['opportunities']):,.2f}

## Key Contacts
{len(account_data['contacts'])} contacts on file

## Recommendations
Based on the account data, focus on maintaining strong relationships and pursuing new opportunities.
"""
    
    def _parse_sections(self, content: str) -> List[str]:
        """Parse sections from markdown content"""
        import re
        sections = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
        return sections[:10]  # Limit to 10 sections


project_sheet_generation_service = ProjectSheetGenerationService()

