from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class OrganizationNameRequest(BaseModel):
    partial_name: str
    context: Optional[str] = None


class OrganizationNameResponse(BaseModel):
    suggestions: List[str]
    confidence_scores: List[float]


class AccountEnhancementRequest(BaseModel):
    company_website: str
    company_name: Optional[str] = None
    context: Optional[str] = None


class AccountEnhancementResponse(BaseModel):
    enhanced_data: Dict[str, Any]
    suggestions_applied: int
    processing_time_ms: int


class AddressValidationRequest(BaseModel):
    address: str
    country: Optional[str] = None


class AddressValidationResponse(BaseModel):
    is_valid: bool
    normalized_address: Optional[str] = None
    suggestions: List[str]


class ContactValidationRequest(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    name: Optional[str] = None


class ContactValidationResponse(BaseModel):
    email_valid: bool
    phone_valid: bool
    name_valid: bool
    suggestions: Dict[str, List[str]]


class IndustrySuggestionRequest(BaseModel):
    company_description: str
    website_content: Optional[str] = None


class IndustrySuggestionResponse(BaseModel):
    primary_industry: str
    secondary_industries: List[str]
    confidence_score: float


class CompanySizeSuggestionRequest(BaseModel):
    company_name: str
    website: Optional[str] = None
    description: Optional[str] = None


class CompanySizeSuggestionResponse(BaseModel):
    estimated_size: str
    confidence_score: float
    reasoning: str


class SuggestionValue(BaseModel):
    value: str
    confidence: float
    source: str


class AISuggestionRequest(BaseModel):
    context: str
    suggestion_type: str
    user_id: Optional[str] = None
    account_id: Optional[str] = None
    opportunity_id: Optional[str] = None


class AISuggestionResponse(BaseModel):
    id: str
    suggestion: str
    confidence_score: float
    suggestion_type: str
    context: str
    created_at: datetime
    user_id: Optional[str] = None
    account_id: Optional[str] = None
    opportunity_id: Optional[str] = None


class AISuggestionListResponse(BaseModel):
    suggestions: List[AISuggestionResponse]
    total: int
    page: int
    size: int


class AISuggestionUpdateRequest(BaseModel):
    suggestion: Optional[str] = None
    confidence_score: Optional[float] = None
    is_implemented: Optional[bool] = None


class AISuggestionFeedbackRequest(BaseModel):
    suggestion_id: str
    feedback: str
    rating: Optional[int] = None  # 1-5 scale
    is_helpful: Optional[bool] = None


class AISuggestionAnalyticsResponse(BaseModel):
    total_suggestions: int
    implemented_suggestions: int
    average_rating: float
    most_common_type: str
    success_rate: float