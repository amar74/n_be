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
    """
    Scrape multiple URLs and extract contact information.

    Only authenticated users can access this endpoint.

    Args:
        payload: ScrapeRequest containing URLs to scrape
        request: FastAPI request object for JWT token extraction

    Returns:
        ScrapeResponse: Scraped contact information and statistics
    """
    logger.info("Endpoint hit: /scrape")
    try:
        # Process scraping request
        result = await scrape_urls(payload)

        logger.info(
            f"Scraping completed for user {current_user.id}: {result.successful_scrapes} successful, {result.failed_scrapes} failed"
        )

        return result
    
    except Exception as ex:
        logger.error(f"Error scraping urls: {str(ex)}")
        raise MegapolisHTTPException(
            status_code=500, message=f"Error scraping urls: {str(ex)}"
        )
