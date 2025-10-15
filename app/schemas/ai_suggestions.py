from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any, Union
from uuid import UUID

class SuggestionValue(BaseModel):

    value: Any
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score from 0 to 1")
    source: str = Field(description="Source of the suggestion (scraped, inferred, extracted)")
    reasoning: Optional[str] = Field(None, description="Human-readable explanation")
    should_auto_apply: bool = Field(default=False, description="Auto-apply if confidence > 0.85")

class OrganizationNameRequest(BaseModel):

    website_url: HttpUrl
    context: Optional[Dict[str, str]] = Field(default_factory=dict, description="Additional context")

class OrganizationNameResponse(BaseModel):

    suggested_name: str
    confidence: float = Field(ge=0.0, le=1.0)
    alternatives: List[str] = Field(default_factory=list)
    source: str  # "meta_tags", "homepage_title", "about_page", etc., get from given URL and get the source of the suggestion from the url (https://www.softication.com/)
    reasoning: Optional[str] = None

class AccountEnhancementRequest(BaseModel):

    company_website: HttpUrl
    partial_data: Dict[str, Any] = Field(default_factory=dict, description="Already entered data")
    enhancement_options: Dict[str, bool] = Field(
        default_factory=lambda: {
            "suggest_contact": True,
            "suggest_address": True,
            "suggest_industry": True,
            "suggest_company_size": True,
            "validate_data": True
        },
        description="Which fields to enhance"
    )

class AccountEnhancementResponse(BaseModel):

    enhanced_data: Dict[str, SuggestionValue]
    processing_time_ms: int
    warnings: List[str] = Field(default_factory=list)
    suggestions_applied: int = Field(default=0, description="Number of suggestions auto-applied")

class AddressValidationRequest(BaseModel):

    address: Dict[str, Optional[str]] = Field(description="Address to validate")
    country_code: str = Field(default="US", description="Country for validation")

class AddressIssue(BaseModel):

    field: str
    current_value: Optional[str]
    suggested_value: Optional[str]
    issue_type: str  
    confidence: float = Field(ge=0.0, le=1.0)

class AddressValidationResponse(BaseModel):

    is_valid: bool
    issues: List[AddressIssue] = Field(default_factory=list)
    corrected_address: Dict[str, Optional[str]]
    confidence: float = Field(ge=0.0, le=1.0)

class ContactValidationRequest(BaseModel):

    email: Optional[str] = None
    phone: Optional[str] = None
    name: Optional[str] = None

class ContactValidationResponse(BaseModel):

    email_valid: bool = Field(default=True)
    phone_valid: bool = Field(default=True)
    name_valid: bool = Field(default=True)
    suggestions: Dict[str, SuggestionValue] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)

class IndustrySuggestionRequest(BaseModel):

    website_url: Optional[HttpUrl] = None
    company_name: Optional[str] = None
    description: Optional[str] = None

class IndustrySuggestionResponse(BaseModel):

    suggested_industry: str
    confidence: float = Field(ge=0.0, le=1.0)
    alternatives: List[str] = Field(default_factory=list)
    reasoning: Optional[str] = None

class CompanySizeSuggestionRequest(BaseModel):

    website_url: Optional[HttpUrl] = None
    company_name: Optional[str] = None
    industry: Optional[str] = None

class CompanySizeSuggestionResponse(BaseModel):

    suggested_size: str  # "1-10", "11-50", "51-200", "201-500", "501-1000", "1000+", get from given URL and get the source of the suggestion from the url (https://www.softication.com/)
    confidence: float = Field(ge=0.0, le=1.0)
    employee_estimate: Optional[int] = None
    reasoning: Optional[str] = None

class BulkEnhancementRequest(BaseModel):

    account_ids: List[UUID] = Field(description="Account IDs to enhance")
    enhancement_options: Dict[str, bool] = Field(
        default_factory=lambda: {
            "update_contact_info": True,
            "update_address": True,
            "update_industry": True,
            "validate_all": True
        }
    )

class BulkEnhancementResponse(BaseModel):

    job_id: str
    status: str  # "processing", "completed", "failed"
    total_accounts: int
    processed_accounts: int = 0
    successful_enhancements: int = 0
    failed_enhancements: int = 0
    estimated_completion_time: Optional[int] = None  # seconds

class EnhancementJobStatus(BaseModel):

    job_id: str
    status: str
    progress: float = Field(ge=0.0, le=1.0)
    results: Optional[Dict[str, Any]] = None
    errors: List[str] = Field(default_factory=list)
    created_at: str
    updated_at: str