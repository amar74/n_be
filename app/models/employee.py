from sqlalchemy import String, select, Boolean, Column, ForeignKey, DECIMAL, Enum as SQLEnum, Text, ARRAY, TIMESTAMP, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
import enum
from datetime import datetime
from app.db.base import Base
from app.db.session import get_transaction

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.user import User
    from app.models.account_team import AccountTeam

class EmployeeStatus(str, enum.Enum):
    PENDING = "pending"
    REVIEW = "review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    ACTIVE = "active"
    DEACTIVATED = "deactivated"

class EmployeeRole(str, enum.Enum):
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

class Employee(Base):
    __tablename__ = "employees"

    VOWELS = {"A", "E", "I", "O", "U"}

    @staticmethod
    def _build_org_abbreviation(org_name: Optional[str]) -> str:
        if not org_name:
            return "ORG"

        letters = [c.upper() for c in org_name if c.isalpha()]
        if not letters:
            return "ORG"

        abbreviation: List[str] = []

        # Always include the first letter
        first_letter = letters[0]
        abbreviation.append(first_letter)

        # Prefer consonants for remaining slots
        for char in letters[1:]:
            if len(abbreviation) == 3:
                break
            if char not in Employee.VOWELS:
                abbreviation.append(char)

        # If still short, allow vowels
        if len(abbreviation) < 3:
            for char in letters[1:]:
                if len(abbreviation) == 3:
                    break
                if char in Employee.VOWELS and char not in abbreviation:
                    abbreviation.append(char)

        while len(abbreviation) < 3:
            abbreviation.append("X")

        return "".join(abbreviation[:3])

    @staticmethod
    def _build_employee_initials(employee_name: Optional[str]) -> str:
        if not employee_name:
            return "XX"

        name_parts = [part for part in employee_name.strip().split() if part]
        if len(name_parts) >= 2:
            initials = (name_parts[0][0] + name_parts[-1][0]).upper()
        elif len(name_parts) == 1:
            initials = name_parts[0][:2].upper()
        else:
            initials = "XX"

        initials = "".join(filter(str.isalpha, initials))
        if len(initials) == 0:
            return "XX"
        if len(initials) == 1:
            return f"{initials}X"
        return initials[:2]

    @classmethod
    def _build_employee_prefix(cls, org_name: Optional[str], employee_name: Optional[str]) -> str:
        org_abbr = cls._build_org_abbreviation(org_name)
        initials = cls._build_employee_initials(employee_name)
        return f"{org_abbr}{initials}"

    @classmethod
    async def _next_employee_number(
        cls,
        db: AsyncSession,
        org_name: Optional[str],
        employee_name: Optional[str],
        offset: int = 0,
    ) -> str:
        prefix = cls._build_employee_prefix(org_name, employee_name)

        result = await db.execute(
            select(func.max(cls.employee_number)).where(cls.employee_number.like(f"{prefix}%"))
        )
        last_number = result.scalar_one_or_none()
        last_serial = 0

        if last_number and last_number.startswith(prefix):
            serial_part = last_number[len(prefix):]
            if serial_part.isdigit():
                last_serial = int(serial_part)

        next_serial = last_serial + 1 + offset
        serial_str = str(next_serial).zfill(3)
        return f"{prefix}{serial_str}"

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

    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True
    )

    employee_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)

    # Basic Information
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Job Information
    job_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    role: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Financial
    bill_rate: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 2), nullable=True)
    
    # AI Matching (for project requirements)
    ai_match_percentage: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ai_match_reasons: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    
    # Status and Onboarding
    status: Mapped[str] = mapped_column(
        String(20),
        default=EmployeeStatus.PENDING.value,
        nullable=False,
        index=True
    )
    
    invite_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, unique=True)
    invite_sent_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, nullable=True)
    onboarding_complete: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Experience and Skills (AI enriched)
    experience: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    skills: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    ai_suggested_role: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    ai_suggested_skills: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    
    # Review Notes
    review_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Interview Schedule Data
    interview_date: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, nullable=True)
    interview_time: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    interview_link: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    interview_platform: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    interviewer_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    interviewer_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    interview_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Interview Feedback Data
    interview_feedback: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    interview_completed_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, nullable=True)
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)

    # Relationships
    organization: Mapped[Optional["Organization"]] = relationship(
        "Organization", foreign_keys=[company_id]
    )
    user: Mapped[Optional["User"]] = relationship("User", foreign_keys=[user_id])
    resumes: Mapped[List["Resume"]] = relationship("Resume", back_populates="employee", cascade="all, delete-orphan")
    account_assignments: Mapped[List["AccountTeam"]] = relationship("AccountTeam", back_populates="employee", cascade="all, delete-orphan")
    attendance_records: Mapped[List["Attendance"]] = relationship("Attendance", back_populates="employee", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "company_id": str(self.company_id) if self.company_id else None,
            "user_id": str(self.user_id) if self.user_id else None,
            "employee_number": self.employee_number,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "job_title": self.job_title,
            "role": self.role,
            "department": self.department,
            "location": self.location,
            "bill_rate": float(self.bill_rate) if self.bill_rate else None,
            "status": self.status,
            "ai_match_percentage": self.ai_match_percentage,
            "ai_match_reasons": self.ai_match_reasons or [],
            "invite_sent_at": self.invite_sent_at.isoformat() if self.invite_sent_at else None,
            "onboarding_complete": self.onboarding_complete,
            "experience": self.experience,
            "skills": self.skills or [],
            "ai_suggested_role": self.ai_suggested_role,
            "ai_suggested_skills": self.ai_suggested_skills or [],
            "review_notes": self.review_notes,
            # Interview Schedule
            "interview_date": self.interview_date.isoformat() if self.interview_date else None,
            "interview_time": self.interview_time,
            "interview_link": self.interview_link,
            "interview_platform": self.interview_platform,
            "interviewer_name": self.interviewer_name,
            "interviewer_email": self.interviewer_email,
            "interview_notes": self.interview_notes,
            # Interview Feedback
            "interview_feedback": self.interview_feedback,
            "interview_completed_at": self.interview_completed_at.isoformat() if self.interview_completed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    async def create(
        cls,
        name: str,
        email: str,
        company_id: Optional[uuid.UUID] = None,
        **kwargs
    ) -> "Employee":
        async with get_transaction() as db:
            # Get organization name for employee number generation
            org_name = None
            if company_id:
                from app.models.organization import Organization
                org_result = await db.execute(
                    select(Organization).where(Organization.id == company_id)
                )
                org = org_result.scalar_one_or_none()
                if org:
                    org_name = org.name
            
            # Generate employee number with org name and employee name
            # Format: {ORG_ABBR}{NAME_INITIALS}{SERIAL} (e.g., SFTAM001)
            max_attempts = 10
            employee_number = None
            for offset in range(max_attempts):
                candidate = await cls._next_employee_number(db, org_name, name, offset=offset)
                existing = await db.execute(
                    select(cls).where(cls.employee_number == candidate)
                )
                if not existing.scalar_one_or_none():
                    employee_number = candidate
                    break

            if not employee_number:
                raise RuntimeError("Unable to generate unique employee number")
            
            employee = cls(
                name=name,
                email=email,
                company_id=company_id,
                employee_number=employee_number,
                **kwargs
            )
            db.add(employee)
            await db.flush()
            await db.refresh(employee)
            return employee

    @classmethod
    async def get_by_id(cls, employee_id: uuid.UUID) -> Optional["Employee"]:
        async with get_transaction() as db:
            result = await db.execute(select(cls).where(cls.id == employee_id))
            return result.scalar_one_or_none()

    @classmethod
    async def get_by_email(cls, email: str, company_id: Optional[uuid.UUID] = None) -> Optional["Employee"]:
        async with get_transaction() as db:
            query = select(cls).where(cls.email == email)
            if company_id:
                query = query.where(cls.company_id == company_id)
            result = await db.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def get_all(
        cls,
        company_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List["Employee"]:
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
    async def update(cls, employee_id: uuid.UUID, **kwargs) -> Optional["Employee"]:
        async with get_transaction() as db:
            result = await db.execute(select(cls).where(cls.id == employee_id))
            employee = result.scalar_one_or_none()
            if employee:
                for key, value in kwargs.items():
                    if hasattr(employee, key):
                        setattr(employee, key, value)
                await db.flush()
                await db.refresh(employee)
            return employee

    @classmethod
    async def delete(cls, employee_id: uuid.UUID) -> bool:
        async with get_transaction() as db:
            result = await db.execute(select(cls).where(cls.id == employee_id))
            employee = result.scalar_one_or_none()
            if employee:
                await db.delete(employee)
                await db.flush()
                return True
            return False


class ResumeStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    PARSING = "parsing"
    PARSED = "parsed"
    VERIFIED = "verified"
    FAILED = "failed"


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        primary_key=True,
        nullable=False,
        index=True,
    )

    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False, index=True
    )

    # File Information
    file_url: Mapped[str] = mapped_column(Text, nullable=False)
    file_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    file_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(nullable=True)

    # AI Parsed Data
    ai_parsed_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    skills: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    experience_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    certifications: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    
    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        default=ResumeStatus.UPLOADED.value,
        nullable=False
    )
    
    parse_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Audit
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    parsed_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, nullable=True)

    # Relationships
    employee: Mapped["Employee"] = relationship("Employee", back_populates="resumes")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "employee_id": str(self.employee_id),
            "file_url": self.file_url,
            "file_name": self.file_name,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "ai_parsed_json": self.ai_parsed_json,
            "skills": self.skills or [],
            "experience_summary": self.experience_summary,
            "certifications": self.certifications or [],
            "status": self.status,
            "parse_error": self.parse_error,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "parsed_at": self.parsed_at.isoformat() if self.parsed_at else None,
        }

    @classmethod
    async def create(cls, employee_id: uuid.UUID, file_url: str, **kwargs) -> "Resume":
        async with get_transaction() as db:
            resume = cls(employee_id=employee_id, file_url=file_url, **kwargs)
            db.add(resume)
            await db.flush()
            await db.refresh(resume)
            return resume

    @classmethod
    async def get_by_employee_id(cls, employee_id: uuid.UUID) -> Optional["Resume"]:
        async with get_transaction() as db:
            result = await db.execute(
                select(cls).where(cls.employee_id == employee_id).order_by(cls.created_at.desc())
            )
            return result.scalar_one_or_none()

    @classmethod
    async def update(cls, resume_id: uuid.UUID, **kwargs) -> Optional["Resume"]:
        async with get_transaction() as db:
            result = await db.execute(select(cls).where(cls.id == resume_id))
            resume = result.scalar_one_or_none()
            if resume:
                for key, value in kwargs.items():
                    if hasattr(resume, key):
                        setattr(resume, key, value)
                await db.flush()
                await db.refresh(resume)
            return resume

