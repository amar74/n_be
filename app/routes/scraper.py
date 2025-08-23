from fastapi import APIRouter, Request
from app.schemas.scraper import ScrapeRequest, ScrapeResponse
from app.services.scraper import scrape_urls
from app.models.user import User
from app.utils.logger import logger
from app.utils.error import MegapolisHTTPException
from app.environment import environment
import jwt

router = APIRouter(prefix="/scraper",tags=["scraper"])


@router.post(
    "/scrape", response_model=ScrapeResponse, status_code=200, operation_id="scrapeUrls"
)
async def scrape_urls_endpoint(
    payload: ScrapeRequest, request: Request
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

    # Get the authorization header
    bearer_token = request.headers.get("Authorization")
    if not bearer_token or not bearer_token.startswith("Bearer "):
        logger.warning("No valid Authorization header found")
        raise MegapolisHTTPException(
            status_code=401, message="Token is not provided or invalid"
        )

    token = bearer_token.replace("Bearer ", "")

    try:
        # Decode and verify JWT token
        secret_key = environment.JWT_SECRET_KEY
        if not secret_key:
            logger.error("JWT_SECRET_KEY is not set in the environment")
            raise MegapolisHTTPException(
                status_code=500, message="JWT secret key is not configured"
            )

        payload_jwt = jwt.decode(token, secret_key, algorithms=["HS256"])

        # Extract user ID from token
        user_id = payload_jwt.get("sub")
        logger.debug(f"Decoded JWT payload: {payload_jwt}")
        if not user_id:
            logger.error("No user ID found in token")
            raise MegapolisHTTPException(status_code=401, message="Invalid token")

        # Get user from database
        user = await User.get_by_id(int(user_id))
        if not user:
            logger.error(f"User with ID {user_id} not found in database")
            raise MegapolisHTTPException(status_code=404, message="User not found")

        logger.info(
            f"User {user.email} initiated scraping for {len(payload.urls)} URLs"
        )

        # Process scraping request
        result = await scrape_urls(payload)

        logger.info(
            f"Scraping completed for user {user.email}: {result.successful_scrapes} successful, {result.failed_scrapes} failed"
        )

        return result

    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        raise MegapolisHTTPException(status_code=401, message="Token has expired")
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {str(e)}")
        raise MegapolisHTTPException(status_code=401, message="Invalid token")
    except ValueError:
        logger.warning("Invalid user ID in token")
        raise MegapolisHTTPException(
            status_code=401, message="Invalid user ID in token"
        )
    except Exception as ex:
        logger.error(f"Error verifying token: {str(ex)}")
        raise MegapolisHTTPException(
            status_code=500, message=f"Error verifying token: {str(ex)}"
        )
