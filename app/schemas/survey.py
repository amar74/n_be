from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum

class SurveyTypeEnum(str, Enum):
    account_feedback = "account_feedback"
    customer_satisfaction = "customer_satisfaction"
    nps = "nps"
    opportunity_feedback = "opportunity_feedback"
    general = "general"

class SurveyStatusEnum(str, Enum):
    draft = "draft"
    active = "active"
    paused = "paused"
    completed = "completed"
    archived = "archived"

# ========== Survey Creation ==========
class SurveyCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=2000)
    survey_type: SurveyTypeEnum
    
    # Survey configuration
    questions: List[Dict[str, Any]] = Field(..., description="Survey questions")
    settings: Optional[Dict[str, Any]] = Field(None, description="Survey settings")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Q4 Customer Satisfaction Survey",
                "description": "Quarterly feedback from our key accounts",
                "survey_type": "customer_satisfaction",
                "questions": [
                    {
                        "id": "q1",
                        "type": "rating",
                        "headline": "How satisfied are you with our service?",
                        "required": True,
                        "range": 5
                    }
                ],
                "settings": {
                    "displayOption": "respondMultiple",
                    "autoClose": 30
                }
            }
        }

class SurveyResponse(BaseModel):
    id: UUID
    survey_code: str
    title: str
    description: Optional[str]
    survey_type: str
    status: str
    questions: Optional[List[Dict[str, Any]]] = None
    settings: Optional[Dict[str, Any]] = None
    org_id: UUID
    created_by: Optional[UUID]
    created_at: datetime
    updated_at: Optional[datetime]
    # Optional computed fields
    total_responses: Optional[int] = None
    avg_rating: Optional[float] = None
    
    class Config:
        from_attributes = True

# ========== Survey Distribution ==========
class SurveyDistributionCreate(BaseModel):
    survey_id: UUID
    account_ids: Optional[List[UUID]] = Field(None, description="Specific accounts to target")
    contact_ids: Optional[List[UUID]] = Field(None, description="Specific contacts to target")
    
    # If neither account_ids nor contact_ids provided, can use filters
    filters: Optional[Dict[str, Any]] = Field(
        None, 
        description="Filters to select accounts (e.g., client_type, market_sector)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "survey_id": "550e8400-e29b-41d4-a716-446655440000",
                "account_ids": [
                    "660e8400-e29b-41d4-a716-446655440000",
                    "770e8400-e29b-41d4-a716-446655440000"
                ]
            }
        }

class SurveyDistributionResponse(BaseModel):
    id: UUID
    survey_id: UUID
    account_id: Optional[UUID]
    contact_id: Optional[UUID]
    survey_link: Optional[str]
    sent_at: Optional[datetime]
    is_sent: bool
    is_completed: bool
    
    class Config:
        from_attributes = True

class BulkDistributionResponse(BaseModel):
    success: bool
    message: str
    distributions_created: int
    distributions: List[SurveyDistributionResponse]

# ========== Survey Response Submission ==========
class SurveyResponseSubmission(BaseModel):
    survey_id: UUID
    contact_id: UUID
    account_id: UUID
    responses: Dict[str, Any] = Field(..., description="Survey responses")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Response metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "survey_id": "123e4567-e89b-12d3-a456-426614174000",
                "contact_id": "123e4567-e89b-12d3-a456-426614174001",
                "account_id": "123e4567-e89b-12d3-a456-426614174002",
                "responses": {
                    "q1": 5,
                    "q2": "Great service!"
                },
                "metadata": {
                    "userAgent": "Mozilla/5.0...",
                    "country": "US",
                    "ipAddress": "192.168.1.1"
                }
            }
        }

class SurveyResponseModel(BaseModel):
    id: UUID
    response_code: str
    survey_id: UUID
    account_id: Optional[UUID]
    contact_id: Optional[UUID]
    response_data: Dict[str, Any]
    finished: bool
    meta: Optional[Dict[str, Any]]
    time_to_complete: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# ========== Analytics ==========
class SurveyAnalyticsByAccount(BaseModel):
    account_id: UUID
    account_name: str
    total_surveys_sent: int
    total_responses: int
    response_rate: float  # percentage
    avg_satisfaction_score: Optional[float]
    last_response_date: Optional[datetime]

class SurveyAnalyticsSummary(BaseModel):
    survey_id: UUID
    survey_title: str
    total_sent: int
    total_responses: int
    response_rate: float
    avg_completion_time: Optional[int]  # in seconds
    by_account: List[SurveyAnalyticsByAccount]

# ========== List/Filter ==========
class SurveyListResponse(BaseModel):
    surveys: List[SurveyResponse]
    total: int
    page: int
    page_size: int

class SurveyStatusUpdate(BaseModel):
    status: SurveyStatusEnum

# ========== Survey Target Accounts ==========
class SurveyContactResponse(BaseModel):
    id: str
    name: str
    email: str
    title: str = ""

class SurveyAccountResponse(BaseModel):
    id: str
    name: str
    client_type: str
    market_sector: Optional[str] = None
    contacts: List[SurveyContactResponse] = []
