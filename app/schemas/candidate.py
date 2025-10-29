from pydantic import BaseModel, EmailStr, Field, HttpUrl, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from decimal import Decimal


# Profile Extraction Request
class ProfileExtractRequest(BaseModel):
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile URL")
    portfolio_url: Optional[str] = Field(None, description="Portfolio/personal website URL")
    other_profile_url: Optional[str] = Field(None, description="Any other profile URL")
    name: Optional[str] = Field(None, description="Candidate name (optional)")
    
    model_config = ConfigDict(from_attributes=True)


# CV Upload Request (multipart/form-data)
class CVUploadRequest(BaseModel):
    candidate_id: Optional[UUID] = Field(None, description="Existing candidate ID to link CV to")
    name: Optional[str] = Field(None, description="Candidate name if not existing")
    email: Optional[EmailStr] = Field(None, description="Candidate email")
    
    model_config = ConfigDict(from_attributes=True)


# Skills Matrix Item
class SkillMatrixItem(BaseModel):
    skill: str
    proficiency: int = Field(..., ge=0, le=10, description="Proficiency level 0-10")
    experience_years: Optional[float] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)


# Project Experience Item
class ProjectExperienceItem(BaseModel):
    name: str
    duration: str  # "18 months", "2 years"
    value: Optional[float] = Field(None, description="Project value in USD")
    role: Optional[str] = None
    technologies: Optional[List[str]] = []
    description: Optional[str] = None


# Education Item
class EducationItem(BaseModel):
    degree: str
    university: str
    graduation_year: Optional[str] = None
    honors: Optional[str] = None


# Document Checklist Item
class DocumentChecklistItem(BaseModel):
    doc_type: str
    required: bool = True
    uploaded: bool = False
    url: Optional[str] = None
    description: Optional[str] = None


# AI Enrichment Response (from Gemini)
class AIEnrichmentResponse(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    experience_summary: str
    total_experience_years: Optional[float] = None
    
    # Skills
    top_skills: List[str] = []
    technical_skills: List[str] = []
    soft_skills: List[str] = []
    skills_matrix: List[SkillMatrixItem] = []
    
    # Sectors, Services, Projects
    sectors: List[str] = []
    services: List[str] = []
    project_types: List[str] = []
    
    # Projects & Education
    project_experience: List[ProjectExperienceItem] = []
    education: List[EducationItem] = []
    certifications: List[str] = []
    
    # Document Checklist
    document_checklist: List[DocumentChecklistItem] = []
    
    # Match & Confidence
    match_percentage: Optional[int] = Field(None, ge=0, le=100)
    match_reasons: List[str] = []
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    
    # Raw Gemini output
    raw_json: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(from_attributes=True)


# Candidate Base Schema
class CandidateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    other_profile_url: Optional[str] = None


# Candidate Create
class CandidateCreate(CandidateBase):
    company_id: Optional[UUID] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    compensation_type: Optional[str] = Field(None, description="hourly or salary")
    hourly_rate: Optional[float] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None


# Candidate Response
class CandidateResponse(CandidateBase):
    id: UUID
    company_id: Optional[UUID] = None
    candidate_number: str
    
    resume_url: Optional[str] = None
    resume_filename: Optional[str] = None
    
    ai_experience: Optional[str] = None
    ai_skills: List[str] = []
    ai_sectors: List[str] = []
    ai_services: List[str] = []
    ai_project_types: List[str] = []
    ai_doc_checklist: Optional[Dict[str, Any]] = None
    
    skills_matrix: Optional[Dict[str, Any]] = None
    project_experience: Optional[Dict[str, Any]] = None
    education: Optional[Dict[str, Any]] = None
    certifications: List[str] = []
    
    ai_match_percentage: Optional[int] = None
    ai_match_reasons: List[str] = []
    ai_confidence_score: Optional[float] = None
    
    status: str
    enrichment_started_at: Optional[datetime] = None
    enrichment_completed_at: Optional[datetime] = None
    
    job_title: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    compensation_type: Optional[str] = None
    hourly_rate: Optional[float] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    
    converted_to_employee_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Approval Request
class CandidateApprovalRequest(BaseModel):
    candidate_id: UUID
    job_title: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    compensation_type: Optional[str] = Field(None, description="hourly or salary")
    hourly_rate: Optional[float] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    
    # Allow manual overrides of AI suggestions
    override_skills: Optional[List[str]] = None
    override_sectors: Optional[List[str]] = None
    override_services: Optional[List[str]] = None
    
    model_config = ConfigDict(from_attributes=True)


# Enrichment Status Response
class EnrichmentStatusResponse(BaseModel):
    candidate_id: UUID
    status: str  # pending, enriching, enriched, approved
    progress: int = Field(..., ge=0, le=100, description="Enrichment progress %")
    message: str
    enrichment_started_at: Optional[datetime] = None
    enrichment_completed_at: Optional[datetime] = None
    error: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


# Bulk Upload Response
class BulkCandidateUploadResponse(BaseModel):
    total: int
    success: int
    failed: int
    candidates: List[CandidateResponse] = []
    errors: List[str] = []
    enrichment_queued: int = 0
    
    model_config = ConfigDict(from_attributes=True)

