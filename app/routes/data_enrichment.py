from fastapi import APIRouter, Depends
from app.schemas.data_enrichment import AccountEnhancementRequest, AccountEnhancementResponse
from app.services.data_enrichment import data_enrichment_service
from app.services.ai_suggestions import data_enrichment_service as ai_data_enrichment_service
from app.models.user import User
from app.dependencies.user_auth import get_current_user
from app.utils.logger import logger
from app.utils.error import MegapolisHTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/ai", tags=["ai-suggestions"])

@router.post(
    "/enhance-opportunity-data", 
    response_model=AccountEnhancementResponse,
    operation_id="enhanceOpportunityData"
)
async def enhance_opportunity_data(
    request: AccountEnhancementRequest, 
    current_user: User = Depends(get_current_user)
) -> AccountEnhancementResponse:
    try:
        result = await data_enrichment_service.enhance_opportunity_data(request)
        
        logger.info(
            f"Opportunity enhancement completed for {request.company_website}: "
            f"{len(result.enhanced_data)} fields updated, "
            f"{result.suggestions_applied} auto-applied in {result.processing_time_ms}ms"
        )
        
        return result
        
    except MegapolisHTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in opportunity enhancement: {e}")
        raise MegapolisHTTPException(
            status_code=500,
            message="Internal server error during opportunity enhancement",
            details=str(e)
        )

@router.post(
    "/enhance-account-data", 
    response_model=AccountEnhancementResponse,
    operation_id="enhanceAccountData"
)
async def enhance_account_data(
    request: AccountEnhancementRequest, 
    current_user: User = Depends(get_current_user)
) -> AccountEnhancementResponse:
    try:
        result = await data_enrichment_service.enhance_account_data(request)
        
        logger.info(
            f"Account enhancement completed for {request.company_website}: "
            f"{len(result.enhanced_data)} fields updated, "
            f"{result.suggestions_applied} auto-applied in {result.processing_time_ms}ms"
        )
        
        return result
        
    except MegapolisHTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in account enhancement: {e}")
        raise MegapolisHTTPException(
            status_code=500,
            message="Internal server error during account enhancement",
            details=str(e)
        )

class AutoScraperRequest(BaseModel):
    website_url: str

class AIRefreshRequest(BaseModel):
    opportunity_id: str
    project_url: str

@router.post(
    "/discover-opportunities", 
    operation_id="discoverOpportunities"
)
async def discover_opportunities(
    request: AutoScraperRequest, 
    current_user: User = Depends(get_current_user)
):
    """
    Advanced auto-scraper that:
    1. Scans the website for project/opportunity pages
    2. Follows links to individual projects
    3. Extracts data from each project
    4. Returns multiple opportunities with documents and images
    """
    try:
        result = await ai_data_enrichment_service.discover_and_extract_opportunities(request.website_url)
        
        logger.info(
            f"Opportunity discovery completed for {request.website_url}: "
            f"{result.get('opportunities_found', 0)} opportunities found"
        )
        
        return result
        
    except MegapolisHTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in opportunity discovery: {e}")
        raise MegapolisHTTPException(
            status_code=500,
            message="Internal server error during opportunity discovery",
            details=str(e)
        )

@router.post(
    "/refresh-opportunity-data",
    operation_id="refreshOpportunityData"
)
async def refresh_opportunity_data(
    request: AIRefreshRequest,
    current_user: User = Depends(get_current_user)
):
    """
    AI Refresh: Re-scrape project URL and auto-update all opportunity data
    Updates:
    - Project Description
    - Project Scope  
    - Contact Details
    - Documents
    - Milestones
    - All metadata
    """
    try:
        from app.utils.scraper import scrape_text_with_bs4
        from app.models.opportunity import Opportunity
        from app.models.opportunity_tabs import OpportunityOverview
        from app.models.opportunity_document import OpportunityDocument
        from app.db.session import get_request_transaction
        from sqlalchemy import select
        import uuid
        
        db = get_request_transaction()
        
        # Get opportunity
        opportunity_uuid = uuid.UUID(request.opportunity_id)
        opportunity = await db.scalar(select(Opportunity).where(Opportunity.id == opportunity_uuid))
        
        if not opportunity:
            raise MegapolisHTTPException(
                status_code=404,
                message="Opportunity not found"
            )
        
        # Scrape the project URL
        logger.info(f"Scraping project data from: {request.project_url}")
        page_data = await scrape_text_with_bs4(request.project_url)
        
        if "error" in page_data:
            raise MegapolisHTTPException(
                status_code=400,
                message=f"Failed to scrape project: {page_data['error']}"
            )
        
        # Extract comprehensive data
        extracted_data = await ai_data_enrichment_service._extract_opportunity_from_page(
            request.project_url, 
            page_data
        )
        
        # Update Opportunity basic fields
        if extracted_data.get("opportunity_name"):
            opportunity.project_name = extracted_data["opportunity_name"]
        if extracted_data.get("project_value") and extracted_data["project_value"] != "Not available":
            # Parse value string to number
            value_str = extracted_data["project_value"].replace("$", "").replace(",", "")
            try:
                opportunity.project_value = float(value_str.split()[0])
            except:
                pass
        if extracted_data.get("market_sector"):
            opportunity.market_sector = extracted_data["market_sector"]
        if extracted_data.get("location"):
            opportunity.state = extracted_data["location"]
        
        # Update or create OpportunityOverview
        overview = await db.scalar(
            select(OpportunityOverview).where(OpportunityOverview.opportunity_id == opportunity_uuid)
        )
        
        if not overview:
            overview = OpportunityOverview(
                opportunity_id=opportunity_uuid,
                project_description=extracted_data.get("project_description", ""),
                project_scope=extracted_data.get("project_scope", "").split("\n") if extracted_data.get("project_scope") else [],
                key_metrics={
                    "project_status": extracted_data.get("project_status", ""),
                    "start_date": extracted_data.get("start_date", ""),
                    "end_date": extracted_data.get("end_date", ""),
                    "contact_phone": extracted_data.get("contact_phone", ""),
                    "contact_emails": extracted_data.get("contact_emails", []),
                    "milestones": extracted_data.get("milestones", [])
                },
                documents_summary={
                    "documents": extracted_data.get("documents", []),
                    "images": extracted_data.get("images", [])
                }
            )
            db.add(overview)
        else:
            overview.project_description = extracted_data.get("project_description", "")
            overview.project_scope = extracted_data.get("project_scope", "").split("\n") if extracted_data.get("project_scope") else []
            overview.key_metrics = {
                "project_status": extracted_data.get("project_status", ""),
                "start_date": extracted_data.get("start_date", ""),
                "end_date": extracted_data.get("end_date", ""),
                "contact_phone": extracted_data.get("contact_phone", ""),
                "contact_emails": extracted_data.get("contact_emails", []),
                "milestones": extracted_data.get("milestones", [])
            }
            overview.documents_summary = {
                "documents": extracted_data.get("documents", []),
                "images": extracted_data.get("images", [])
            }
        
        # Add documents
        for doc_url in extracted_data.get("documents", [])[:10]:  # Limit to 10 docs
            doc = OpportunityDocument(
                opportunity_id=opportunity_uuid,
                document_name=doc_url.split("/")[-1],
                document_url=doc_url,
                document_type="external",
                uploaded_by=current_user.id
            )
            db.add(doc)
        
        await db.flush()
        
        logger.info(f"Opportunity {opportunity_uuid} refreshed successfully")
        
        return {
            "success": True,
            "message": "Opportunity data refreshed successfully",
            "opportunity_id": str(opportunity_uuid),
            "updated_fields": {
                "project_name": extracted_data.get("opportunity_name"),
                "project_description": extracted_data.get("project_description")[:100] + "...",
                "project_scope_items": len(extracted_data.get("project_scope", "").split("\n")),
                "documents_added": len(extracted_data.get("documents", [])),
                "images_found": len(extracted_data.get("images", [])),
                "contact_details": {
                    "phone": extracted_data.get("contact_phone"),
                    "emails": extracted_data.get("contact_emails", [])
                }
            }
        }
        
    except MegapolisHTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in opportunity refresh: {e}", exc_info=True)
        raise MegapolisHTTPException(
            status_code=500,
            message="Internal server error during opportunity refresh",
            details=str(e)
        )
# @author rose11