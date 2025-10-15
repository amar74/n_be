from fastapi import APIRouter, Depends
from app.schemas.scraper import ScrapeRequest, ScrapeResponse
from app.services.scraper import scrape_urls
from app.models.user import User
from app.utils.logger import logger
from app.utils.error import MegapolisHTTPException
import jwt
from app.dependencies.user_auth import get_current_user
router = APIRouter(prefix="/scraper", tags=["scraper"])

@router.post(
    "/scrape", response_model=ScrapeResponse, status_code=200, operation_id="scrapeUrls"
)
async def scrape_urls_endpoint(
    payload: ScrapeRequest, current_user: User = Depends(get_current_user)
) -> ScrapeResponse:
    
    try:
        result = await scrape_urls(payload)
        return result
    
    except Exception as ex:
        logger.error(f"Error on scraping urls: {str(ex)}")
        raise MegapolisHTTPException(
            status_code=500, message=f"Error on scraping urls: {str(ex)} put correct url"
        )
