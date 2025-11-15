from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Dict, Any


class ScrapedAddress(BaseModel):
    line1: Optional[str] = None
    line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country_code: Optional[str] = None
    pincode: Optional[str] = None


class ScrapedDocument(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None
    type: Optional[str] = None


class ScrapedContact(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    organization: Optional[str] = None
    email: List[str] = Field(default_factory=list)
    phone: List[str] = Field(default_factory=list)


class ScrapedOpportunity(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None
    client: Optional[str] = None
    location: Optional[str] = None
    location_details: Optional[ScrapedAddress] = None
    budget_text: Optional[str] = None
    project_value_numeric: Optional[float] = None
    project_value_text: Optional[str] = None
    deadline: Optional[str] = None
    expected_rfp_date: Optional[str] = None
    start_date: Optional[str] = None
    completion_date: Optional[str] = None
    detail_url: Optional[str] = None
    tags: Optional[List[str]] = None
    overview: Optional[str] = None
    scope_summary: Optional[str] = None
    scope_items: List[str] = Field(default_factory=list)
    documents: List[ScrapedDocument] = Field(default_factory=list)
    contacts: List[ScrapedContact] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


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
    opportunities: List[ScrapedOpportunity] = Field(default_factory=list)

class ScrapeResponse(BaseModel):
    results: List[ScrapeResult]
    total_urls: int
    successful_scrapes: int
    failed_scrapes: int

    model_config = {
        "from_attributes": True}
