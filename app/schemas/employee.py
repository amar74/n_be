from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum

class EmployeeStatus(str, Enum):
    PENDING = "pending"
    REVIEW = "review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    ACTIVE = "active"
    DEACTIVATED = "deactivated"

class EmployeeRole(str, Enum):
    ADMIN = "Admin"
    DEVELOPER = "Developer"
    DESIGNER = "Designer"
    PROJECT_MANAGER = "Project Manager"
    BUSINESS_ANALYST = "Business Analyst"
    QA_ENGINEER = "QA Engineer"
    DEVOPS_ENGINEER = "DevOps Engineer"
    DATA_SCIENTIST = "Data Scientist"
    PRODUCT_MANAGER = "Product Manager"
    SALES_EXECUTIVE = "Sales Executive"
    MARKETING_MANAGER = "Marketing Manager"
    HR_MANAGER = "HR Manager"

# Base Schema
class EmployeeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    job_title: Optional[str] = Field(None, max_length=255, description="Any job title (Contractor, Plumber, Site Engineer, etc.)")
    role: Optional[str] = Field(None, max_length=100, description="Can be any custom role")
    department: Optional[str] = Field(None, max_length=100, description="Can be any custom department")
    location: Optional[str] = Field(None, max_length=200, description="Any USA city/state")
    bill_rate: Optional[float] = Field(None, gt=0, description="Hourly rate - AI will suggest if not provided")
    experience: Optional[str] = Field(None, max_length=100, description="e.g., '5 years' or 'Entry Level'")
    skills: Optional[List[str]] = Field(default_factory=list, description="Will be populated by AI if not provided")

# Create Schema
class EmployeeCreate(EmployeeBase):
    use_ai_suggestion: bool = Field(default=False, description="Use AI to suggest role and skills")
    model_config = ConfigDict(from_attributes=True)

# Update Schema
class EmployeeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    job_title: Optional[str] = Field(None, max_length=255)
    role: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=100)
    bill_rate: Optional[float] = Field(None, gt=0)
    status: Optional[EmployeeStatus] = None
    experience: Optional[str] = Field(None, max_length=100)
    skills: Optional[List[str]] = None
    review_notes: Optional[str] = None
    onboarding_complete: Optional[bool] = None
    
    model_config = ConfigDict(from_attributes=True)

# Response Schema
class EmployeeResponse(EmployeeBase):
    id: UUID
    company_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    employee_number: str
    status: str
    ai_match_percentage: Optional[int] = None
    ai_match_reasons: Optional[List[str]] = Field(default_factory=list)
    invite_sent_at: Optional[datetime] = None
    onboarding_complete: bool
    ai_suggested_role: Optional[str] = None
    ai_suggested_skills: Optional[List[str]] = Field(default_factory=list)
    review_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Bulk Import Schema
class BulkEmployeeImport(BaseModel):
    employees: List[EmployeeCreate]
    ai_enrich: bool = Field(default=False, description="Use AI to enrich all employee data")
    send_invites: bool = Field(default=True, description="Send email invites to all employees")
    
    model_config = ConfigDict(from_attributes=True)

# AI Suggestion Request
class AIRoleSuggestionRequest(BaseModel):
    name: str
    job_title: Optional[str] = None
    department: Optional[str] = None
    company_industry: Optional[str] = "Technology Consulting"
    
    model_config = ConfigDict(from_attributes=True)

# AI Suggestion Response
class AIRoleSuggestionResponse(BaseModel):
    suggested_role: str
    suggested_department: Optional[str] = None
    suggested_skills: List[str]
    confidence: float = Field(..., ge=0.0, le=1.0)
    bill_rate_suggestion: Optional[float] = None
    
    model_config = ConfigDict(from_attributes=True)

# Resume Schemas
class ResumeStatus(str, Enum):
    UPLOADED = "uploaded"
    PARSING = "parsing"
    PARSED = "parsed"
    VERIFIED = "verified"
    FAILED = "failed"

class ResumeUpload(BaseModel):
    employee_id: UUID
    file_name: str
    file_type: str
    file_size: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)

class ResumeResponse(BaseModel):
    id: UUID
    employee_id: UUID
    file_url: str
    file_name: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    ai_parsed_json: Optional[Dict[str, Any]] = None
    skills: List[str] = Field(default_factory=list)
    experience_summary: Optional[str] = None
    certifications: List[str] = Field(default_factory=list)
    status: str
    parse_error: Optional[str] = None
    created_at: datetime
    parsed_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

# Resume Analysis Response
class ResumeAnalysisResponse(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str]
    experience_summary: str
    certifications: List[str]
    job_titles: List[str]
    education: List[str]
    years_of_experience: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)

# Skills Gap Analysis
class SkillGapAnalysis(BaseModel):
    skill: str
    required: int
    available: int
    gap: int
    priority: str  # high, medium, low
    
    model_config = ConfigDict(from_attributes=True)

class SkillsGapResponse(BaseModel):
    total_employees: int
    accepted_employees: int
    total_gap: int
    critical_gaps: int
    skill_gaps: List[SkillGapAnalysis]
    
    model_config = ConfigDict(from_attributes=True)

# Onboarding Dashboard
class OnboardingDashboard(BaseModel):
    total_employees: int
    pending_count: int
    review_count: int
    accepted_count: int
    rejected_count: int
    active_count: int
    pending_invites: int
    onboarding_complete: int
    recent_hires: List[EmployeeResponse]
    
    model_config = ConfigDict(from_attributes=True)

# Permission Update
class PermissionUpdate(BaseModel):
    permissions: List[str] = Field(..., description="List of permission IDs")
    
    model_config = ConfigDict(from_attributes=True)

# CSV Row Schema for Bulk Import
class EmployeeCSVRow(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    job_title: Optional[str] = None
    role: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    bill_rate: Optional[float] = None
    
    model_config = ConfigDict(from_attributes=True)

# Interview Schedule Schema
class InterviewSchedule(BaseModel):
    interview_date: str = Field(..., description="Interview date (YYYY-MM-DD)")
    interview_time: str = Field(..., description="Interview time (HH:MM)")
    interview_link: str = Field(..., description="Zoom/Google Meet/Teams link")
    platform: str = Field(..., description="Platform: zoom, google-meet, teams, other")
    interviewer_name: str = Field(..., description="Interviewer name")
    interviewer_email: Optional[str] = Field(None, description="Interviewer email")
    notes: Optional[str] = Field(None, description="Interview preparation notes")
    send_email: bool = Field(default=False, description="Send invitation email")
    
    model_config = ConfigDict(from_attributes=True)

# Interview Feedback Schema
class InterviewFeedback(BaseModel):
    interview_date: str = Field(..., description="Interview date")
    interviewer_name: str = Field(..., description="Interviewer name")
    technical_skills: int = Field(..., ge=1, le=5, description="Technical skills rating (1-5)")
    communication_skills: int = Field(..., ge=1, le=5, description="Communication skills rating (1-5)")
    cultural_fit: int = Field(..., ge=1, le=5, description="Cultural fit rating (1-5)")
    overall_rating: int = Field(..., ge=1, le=5, description="Overall rating (1-5)")
    strengths: Optional[str] = Field(None, description="Candidate strengths")
    weaknesses: Optional[str] = Field(None, description="Areas for improvement")
    recommendation: str = Field(..., description="Recommendation: accept, reject, review")
    notes: Optional[str] = Field(None, description="Additional interview notes")
    
    model_config = ConfigDict(from_attributes=True)

