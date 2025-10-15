from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
import json

from app.db.session import get_session
from app.models.account import Account
from app.models.contact import Contact
from app.utils.logger import logger
from app.services.ai_suggestions import ai_suggestion_service
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

class AIDataEnrichmentService:

    async def enrich_account_data(self, account_id: str, org_id: str) -> Dict[str, Any]:

        async with get_session() as db:
            stmt = select(Account).where(
                Account.account_id == account_id,
                Account.org_id == org_id
            )
            result = await db.execute(stmt)
            account = result.scalar_one_or_none()
            
            if not account:
                raise ValueError(f"Account {account_id} not found")
            
            enrichment_results = {
                "account_id": account_id,
                "enriched_at": datetime.utcnow().isoformat(),
                "updates": [],
                "confidence_scores": {},
                "sources": []
            }
            
            try:
                if account.company_website:
                    company_data = await self._enrich_company_from_website(
                        account.company_website, account, db
                    )
                    if company_data:
                        enrichment_results["updates"].extend(company_data["updates"])
                        enrichment_results["confidence_scores"].update(company_data["confidence_scores"])
                        enrichment_results["sources"].extend(company_data["sources"])
                
                contact_data = await self._enrich_contact_information(account, db)
                if contact_data:
                    enrichment_results["updates"].extend(contact_data["updates"])
                    enrichment_results["confidence_scores"].update(contact_data["confidence_scores"])
                    enrichment_results["sources"].extend(contact_data["sources"])
                
                industry_data = await self._enrich_industry_classification(account, db)
                if industry_data:
                    enrichment_results["updates"].extend(industry_data["updates"])
                    enrichment_results["confidence_scores"].update(industry_data["confidence_scores"])
                    enrichment_results["sources"].extend(industry_data["sources"])
                
                address_data = await self._enrich_address_information(account, db)
                if address_data:
                    enrichment_results["updates"].extend(address_data["updates"])
                    enrichment_results["confidence_scores"].update(address_data["confidence_scores"])
                    enrichment_results["sources"].extend(address_data["sources"])
                
                logger.info(f"Data enrichment completed for account {account_id}: {len(enrichment_results['updates'])} updates")
                
            except Exception as e:
                logger.error(f"Error during data enrichment for account {account_id}: {e}")
                enrichment_results["error"] = str(e)
            
            return enrichment_results
    
    async def _enrich_company_from_website(
        self, website: str, account: Account, db: AsyncSession
    ) -> Optional[Dict[str, Any]]:

        try:
            enhancement_data = await ai_suggestion_service.enhance_account_data(website)
            
            updates = []
            confidence_scores = {}
            sources = ["website_ai_analysis"]
            
            if enhancement_data.get("company_name") and enhancement_data.get("confidence", 0) > 0.8:
                if account.client_name != enhancement_data["company_name"]:
                    updates.append({
                        "field": "client_name",
                        "old_value": account.client_name,
                        "new_value": enhancement_data["company_name"],
                        "reason": "AI website analysis"
                    })
                    confidence_scores["client_name"] = enhancement_data.get("confidence", 0.8)
            
            if enhancement_data.get("industry") and enhancement_data.get("confidence", 0) > 0.7:
                if account.market_sector != enhancement_data["industry"]:
                    updates.append({
                        "field": "market_sector",
                        "old_value": account.market_sector,
                        "new_value": enhancement_data["industry"],
                        "reason": "AI website analysis"
                    })
                    confidence_scores["market_sector"] = enhancement_data.get("confidence", 0.7)
            
            return {
                "updates": updates,
                "confidence_scores": confidence_scores,
                "sources": sources
            }
            
        except Exception as e:
            logger.error(f"Error enriching company data from website: {e}")
            return None
    
    async def _enrich_contact_information(
        self, account: Account, db: AsyncSession
    ) -> Optional[Dict[str, Any]]:

        try:
            updates = []
            confidence_scores = {}
            sources = ["contact_ai_analysis"]
            
            if account.primary_contact_id:
                stmt = select(Contact).where(Contact.id == account.primary_contact_id)
                result = await db.execute(stmt)
                contact = result.scalar_one_or_none()
                
                if contact:
                    if contact.title:
                        role_insights = await self._analyze_contact_role(contact.title)
                        if role_insights:
                            updates.append({
                                "field": "contact_role_insights",
                                "old_value": None,
                                "new_value": role_insights,
                                "reason": "AI role analysis"
                            })
                            confidence_scores["contact_role_insights"] = 0.85
            
            return {
                "updates": updates,
                "confidence_scores": confidence_scores,
                "sources": sources
            }
            
        except Exception as e:
            logger.error(f"Error enriching contact information: {e}")
            return None
    
    async def _enrich_industry_classification(
        self, account: Account, db: AsyncSession
    ) -> Optional[Dict[str, Any]]:

        try:
            updates = []
            confidence_scores = {}
            sources = ["industry_ai_analysis"]
            
            if not account.market_sector:
                industry_suggestion = await self._suggest_industry(account)
                if industry_suggestion:
                    updates.append({
                        "field": "market_sector",
                        "old_value": None,
                        "new_value": industry_suggestion,
                        "reason": "AI industry inference"
                    })
                    confidence_scores["market_sector"] = 0.75
            
            return {
                "updates": updates,
                "confidence_scores": confidence_scores,
                "sources": sources
            }
            
        except Exception as e:
            logger.error(f"Error enriching industry classification: {e}")
            return None
    
    async def _enrich_address_information(
        self, account: Account, db: AsyncSession
    ) -> Optional[Dict[str, Any]]:

        try:
            updates = []
            confidence_scores = {}
            sources = ["address_ai_analysis"]
            
            if not account.client_address_id:
                address_suggestion = await self._suggest_address(account)
                if address_suggestion:
                    updates.append({
                        "field": "suggested_address",
                        "old_value": None,
                        "new_value": address_suggestion,
                        "reason": "AI address inference"
                    })
                    confidence_scores["suggested_address"] = 0.6
            
            return {
                "updates": updates,
                "confidence_scores": confidence_scores,
                "sources": sources
            }
            
        except Exception as e:
            logger.error(f"Error enriching address information: {e}")
            return None
    
    async def _analyze_contact_role(self, title: str) -> Optional[str]:

        title_lower = title.lower()
        
        if any(keyword in title_lower for keyword in ["ceo", "president", "founder", "owner"]):
            return "C-Level Executive"
        elif any(keyword in title_lower for keyword in ["cto", "cfo", "cmo", "coo"]):
            return "C-Level Executive"
        elif any(keyword in title_lower for keyword in ["director", "vp", "vice president"]):
            return "Director Level"
        elif any(keyword in title_lower for keyword in ["manager", "head of"]):
            return "Manager Level"
        elif any(keyword in title_lower for keyword in ["engineer", "developer", "analyst"]):
            return "Technical Role"
        else:
            return "General Business Role"
    
    async def _suggest_industry(self, account: Account) -> Optional[str]:

        company_name = account.client_name.lower() if account.client_name else ""
        website = account.company_website.lower() if account.company_website else ""
        
        tech_keywords = ["tech", "software", "digital", "app", "system", "data", "cloud"]
        finance_keywords = ["finance", "bank", "credit", "investment", "capital"]
        healthcare_keywords = ["health", "medical", "pharma", "care", "hospital"]
        
        if any(keyword in company_name or keyword in website for keyword in tech_keywords):
            return "Technology"
        elif any(keyword in company_name or keyword in website for keyword in finance_keywords):
            return "Financial Services"
        elif any(keyword in company_name or keyword in website for keyword in healthcare_keywords):
            return "Healthcare"
        else:
            return "Business Services"
    
    async def _suggest_address(self, account: Account) -> Optional[Dict[str, str]]:

        if account.client_name:
            return {
                "line1": "Address not available",
                "city": "Unknown",
                "state": "Unknown",
                "country": "Unknown"
            }
        return None
    
    async def batch_enrich_accounts(self, account_ids: List[str], org_id: str) -> Dict[str, Any]:

        results = {
            "total_accounts": len(account_ids),
            "successful": 0,
            "failed": 0,
            "results": []
        }
        
        for account_id in account_ids:
            try:
                enrichment_result = await self.enrich_account_data(account_id, org_id)
                results["results"].append(enrichment_result)
                results["successful"] += 1
            except Exception as e:
                logger.error(f"Failed to enrich account {account_id}: {e}")
                results["failed"] += 1
                results["results"].append({
                    "account_id": account_id,
                    "error": str(e)
                })
        
        return results

ai_data_enrichment_service = AIDataEnrichmentService()