from sqlalchemy import String, select, Boolean, Column, ForeignKey, DECIMAL, Text, ARRAY, TIMESTAMP, Integer, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
import random
import enum
from datetime import datetime
from typing import Optional, List, Dict, Any, TYPE_CHECKING

from app.db.base import Base
from app.db.session import get_session, get_transaction

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.employee import Employee

class CandidateStatus(str, enum.Enum):
    PENDING = "pending"
    ENRICHING = "enriching"
    ENRICHED = "enriched"
    APPROVED = "approved"
    REJECTED = "rejected"

def generate_candidate_number() -> str:
    """Generate candidate number like CND-001"""
    return f"CND-{str(random.randint(1, 9999)).zfill(4)}"

class Candidate(Base):
    """Candidates table for AI-enriched profile processing"""
    __tablename__ = "candidates"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        primary_key=True,
        nullable=False,
        index=True,
    )

    company_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True, index=True
    )

    candidate_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)

    # Basic Information
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Profile Links
    linkedin_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    portfolio_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    other_profile_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Resume/CV
    resume_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resume_filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # AI Raw Data
    ai_raw_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True, comment="Full Gemini API response")
    ai_experience: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="AI-generated experience summary")
    
    # AI Extracted Arrays
    ai_skills: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True, comment="Extracted skills")
    ai_sectors: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True, comment="Sector expertise")
    ai_services: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True, comment="Services provided")
    ai_project_types: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True, comment="Project type experience")
    
    # AI Document Checklist
    ai_doc_checklist: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB, nullable=True, 
        comment="Required documents: {doc_type: {required: bool, uploaded: bool, url: str}}"
    )

    # Skills Matrix (Detailed)
    skills_matrix: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB, nullable=True,
        comment="Detailed skills with proficiency: [{skill, proficiency, years}]"
    )

    # Project Experience
    project_experience: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB, nullable=True,
        comment="Projects with duration and value: [{name, duration, value, role}]"
    )

    # Education & Certifications
    education: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB, nullable=True,
        comment="Degrees, universities, years"
    )
    certifications: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)

    # Match Scoring
    ai_match_percentage: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="0-100 match score")
    ai_match_reasons: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    ai_confidence_score: Mapped[Optional[float]] = mapped_column(DECIMAL(3, 2), nullable=True, comment="0.00-1.00")

    # Status and Workflow
    status: Mapped[str] = mapped_column(
        String(20),
        default=CandidateStatus.PENDING.value,
        nullable=False,
        index=True
    )
    
    enrichment_started_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, nullable=True)
    enrichment_completed_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, nullable=True)
    
    # Job Information (after enrichment)
    job_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    compensation_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, comment="hourly or salary")
    hourly_rate: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 2), nullable=True)
    salary_min: Mapped[Optional[float]] = mapped_column(DECIMAL(12, 2), nullable=True)
    salary_max: Mapped[Optional[float]] = mapped_column(DECIMAL(12, 2), nullable=True)

    # Conversion tracking
    converted_to_employee_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True
    )

    # Audit
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)

    # Relationships
    organization: Mapped[Optional["Organization"]] = relationship("Organization", foreign_keys=[company_id])
    converted_employee: Mapped[Optional["Employee"]] = relationship("Employee", foreign_keys=[converted_to_employee_id])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "company_id": str(self.company_id) if self.company_id else None,
            "candidate_number": self.candidate_number,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "linkedin_url": self.linkedin_url,
            "portfolio_url": self.portfolio_url,
            "other_profile_url": self.other_profile_url,
            "resume_url": self.resume_url,
            "resume_filename": self.resume_filename,
            "ai_raw_json": self.ai_raw_json,
            "ai_experience": self.ai_experience,
            "ai_skills": self.ai_skills or [],
            "ai_sectors": self.ai_sectors or [],
            "ai_services": self.ai_services or [],
            "ai_project_types": self.ai_project_types or [],
            "ai_doc_checklist": self.ai_doc_checklist,
            "skills_matrix": self.skills_matrix,
            "project_experience": self.project_experience,
            "education": self.education,
            "certifications": self.certifications or [],
            "ai_match_percentage": self.ai_match_percentage,
            "ai_match_reasons": self.ai_match_reasons or [],
            "ai_confidence_score": float(self.ai_confidence_score) if self.ai_confidence_score else None,
            "status": self.status,
            "enrichment_started_at": self.enrichment_started_at.isoformat() if self.enrichment_started_at else None,
            "enrichment_completed_at": self.enrichment_completed_at.isoformat() if self.enrichment_completed_at else None,
            "job_title": self.job_title,
            "department": self.department,
            "location": self.location,
            "compensation_type": self.compensation_type,
            "hourly_rate": float(self.hourly_rate) if self.hourly_rate else None,
            "salary_min": float(self.salary_min) if self.salary_min else None,
            "salary_max": float(self.salary_max) if self.salary_max else None,
            "converted_to_employee_id": str(self.converted_to_employee_id) if self.converted_to_employee_id else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    async def create(cls, name: str, company_id: Optional[uuid.UUID] = None, **kwargs) -> "Candidate":
        async with get_transaction() as db:
            candidate = cls(
                name=name,
                company_id=company_id,
                candidate_number=generate_candidate_number(),
                **kwargs
            )
            db.add(candidate)
            await db.flush()
            await db.refresh(candidate)
            return candidate

    @classmethod
    async def get_by_id(cls, candidate_id: uuid.UUID) -> Optional["Candidate"]:
        async with get_transaction() as db:
            result = await db.execute(select(cls).where(cls.id == candidate_id))
            return result.scalar_one_or_none()

    @classmethod
    async def get_all(
        cls,
        company_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List["Candidate"]:
        async with get_transaction() as db:
            query = select(cls)
            if company_id:
                query = query.where(cls.company_id == company_id)
            if status:
                query = query.where(cls.status == status)
            query = query.offset(skip).limit(limit).order_by(cls.created_at.desc())
            result = await db.execute(query)
            return list(result.scalars().all())

    @classmethod
    async def update(cls, candidate_id: uuid.UUID, **kwargs) -> Optional["Candidate"]:
        async with get_transaction() as db:
            result = await db.execute(select(cls).where(cls.id == candidate_id))
            candidate = result.scalar_one_or_none()
            if candidate:
                for key, value in kwargs.items():
                    if hasattr(candidate, key):
                        setattr(candidate, key, value)
                await db.flush()
                await db.refresh(candidate)
            return candidate

    @classmethod
    async def delete(cls, candidate_id: uuid.UUID) -> bool:
        async with get_transaction() as db:
            result = await db.execute(select(cls).where(cls.id == candidate_id))
            candidate = result.scalar_one_or_none()
            if candidate:
                await db.delete(candidate)
                await db.flush()
                return True
            return False

