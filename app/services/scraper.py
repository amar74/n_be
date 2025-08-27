from app.schemas.scraper import ScrapeRequest, ScrapeResponse, ScrapeResult, ScrapedInfo, ScrapedAddress
from app.utils.scraper import process_urls
from app.utils.logger import logger
from app.utils.error import MegapolisHTTPException


async def scrape_urls(payload: ScrapeRequest) -> ScrapeResponse:
    """
    Service function to scrape multiple URLs and extract contact information.
    
    Args:
        payload: ScrapeRequest containing list of URLs to scrape
        
    Returns:
        ScrapeResponse: Results with scraped information and statistics
        
    Raises:
        MegapolisHTTPException: If scraping fails or invalid URLs provided
    """
    logger.info(f"Starting scraping process for {len(payload.urls)} URLs")
    
    if not payload.urls:
        raise MegapolisHTTPException(
            status_code=400,
            message="No URLs provided for scraping"
        )
    
    # Convert HttpUrl objects to strings for the scraper utility
    url_strings = [str(url) for url in payload.urls]
    
    try:
        # Process URLs using the existing scraper utility
        raw_results = process_urls(url_strings)
        
        # Transform results into structured response
        results = []
        successful_scrapes = 0
        failed_scrapes = 0
        
        for result in raw_results:
            if "error" in result:
                results.append(ScrapeResult(
                    url=result["url"],
                    error=result["error"]
                ))
                failed_scrapes += 1
                logger.warning(f"Failed to scrape {result['url']}: {result['error']}")
            else:
                # Parse the scraped info into structured format
                info_data = result.get("info", {})
                
                # Handle address data
                address_data = info_data.get("address", {})
                address = None
                if address_data and isinstance(address_data, dict):
                    address = ScrapedAddress(**address_data)
                
                # Create structured info object
                scraped_info = ScrapedInfo(
                    name=info_data.get("name"),
                    email=info_data.get("email", []),
                    phone=info_data.get("phone", []),
                    address=address
                )
                
                results.append(ScrapeResult(
                    url=result["url"],
                    info=scraped_info
                ))
                successful_scrapes += 1
                logger.info(f"Successfully scraped {result['url']}")
        
        logger.info(f"Scraping completed: {successful_scrapes} successful, {failed_scrapes} failed")
        
        return ScrapeResponse(
            results=results,
            total_urls=len(payload.urls),
            successful_scrapes=successful_scrapes,
            failed_scrapes=failed_scrapes
        )
        
    except Exception as e:
        logger.error(f"Error during scraping process: {str(e)}")
        raise MegapolisHTTPException(
            status_code=500,
            message="Failed to process scraping request"
        )