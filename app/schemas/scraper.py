from pydantic import BaseModel, HttpUrl,Field
from typing import List, Optional

class ScrapedAddress(BaseModel):
    line1: Optional[str] = None
    line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country_code: Optional[str] = None
    pincode: Optional[str] = None

class ScrapedInfo(BaseModel):
    name: Optional[str] = None
    email: List[str] = Field(default_factory=list)
    phone: List[str] = Field(default_factory=list)
    address: Optional[ScrapedAddress] = None

class ScrapeRequest(BaseModel):
    urls: List[HttpUrl]

class ScrapeResult(BaseModel):
    url: str
    info: Optional[ScrapedInfo] = None
    error: Optional[str] = None

class ScrapeResponse(BaseModel):
    results: List[ScrapeResult]
    total_urls: int
    successful_scrapes: int
    failed_scrapes: int

    model_config = {
        "from_attributes": True}
