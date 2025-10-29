import logging
import os
import boto3
from botocore.exceptions import ClientError
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
import PyPDF2
import io
from docx import Document
import asyncio

from app.models.employee import Resume, Employee, ResumeStatus
from app.schemas.employee import ResumeResponse, ResumeAnalysisResponse
from app.services.gemini_service import gemini_service

logger = logging.getLogger(__name__)


class ResumeService:
    """Service for resume upload and AI parsing"""

    def __init__(self):
        # Initialize S3 client
        self.s3_enabled = all([
            os.getenv("AWS_ACCESS_KEY_ID"),
            os.getenv("AWS_SECRET_ACCESS_KEY"),
            os.getenv("AWS_S3_BUCKET_NAME")
        ])
        
        if self.s3_enabled:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                region_name=os.getenv("AWS_REGION", "us-east-1")
            )
            self.bucket_name = os.getenv("AWS_S3_BUCKET_NAME")
            logger.info("S3 client initialized successfully")
        else:
            logger.warning("S3 credentials not configured. File uploads will use local storage.")

    async def upload_resume(
        self,
        employee_id: UUID,
        file_content: bytes,
        file_name: str,
        file_type: str
    ) -> ResumeResponse:
        """
        Upload resume to S3 and create database record
        """
        try:
            # Generate S3 key
            file_extension = file_name.split('.')[-1]
            s3_key = f"resumes/{employee_id}/{datetime.utcnow().timestamp()}.{file_extension}"

            # Upload to S3
            if self.s3_enabled:
                try:
                    self.s3_client.put_object(
                        Bucket=self.bucket_name,
                        Key=s3_key,
                        Body=file_content,
                        ContentType=file_type
                    )
                    file_url = f"https://{self.bucket_name}.s3.amazonaws.com/{s3_key}"
                    logger.info(f"Resume uploaded to S3: {s3_key}")
                except ClientError as e:
                    logger.error(f"S3 upload failed: {e}")
                    # Fallback to local storage indication
                    file_url = f"/local/resumes/{employee_id}/{file_name}"
            else:
                # Local storage fallback
                file_url = f"/local/resumes/{employee_id}/{file_name}"
                logger.info(f"Using local storage path: {file_url}")

            # Create resume record
            resume = await Resume.create(
                employee_id=employee_id,
                file_url=file_url,
                file_name=file_name,
                file_type=file_type,
                file_size=len(file_content),
                status=ResumeStatus.UPLOADED.value
            )

            logger.info(f"Resume record created for employee {employee_id}")

            # Trigger async parsing (in production, this would be a background job)
            try:
                await self.parse_resume(resume.id, file_content, file_type)
                
                # After parsing, trigger deep AI analysis in background
                from app.services.ai_analysis_service import ai_analysis_service
                asyncio.create_task(ai_analysis_service.deep_profile_analysis(employee_id))
                logger.info(f"🚀 Deep AI analysis queued for employee {employee_id}")
                
            except Exception as e:
                logger.error(f"Resume parsing failed: {e}")
                await Resume.update(
                    resume.id,
                    status=ResumeStatus.FAILED.value,
                    parse_error=str(e)
                )

            # Refresh resume data
            resume = await Resume.get_by_employee_id(employee_id)
            return ResumeResponse.model_validate(resume.to_dict())

        except Exception as e:
            logger.error(f"Error uploading resume: {e}")
            raise

    async def parse_resume(
        self,
        resume_id: UUID,
        file_content: bytes,
        file_type: str
    ) -> ResumeAnalysisResponse:
        """
        Extract text from resume and parse using Gemini AI
        """
        try:
            # Update status to parsing
            await Resume.update(resume_id, status=ResumeStatus.PARSING.value)

            # Extract text based on file type
            resume_text = self._extract_text_from_file(file_content, file_type)

            if not resume_text:
                raise ValueError("Could not extract text from resume")

            logger.info(f"Extracted {len(resume_text)} characters from resume")

            # Parse using Gemini AI
            analysis = await gemini_service.parse_resume(resume_text)

            # Update resume record with parsed data
            await Resume.update(
                resume_id,
                ai_parsed_json=analysis.model_dump(),
                skills=analysis.skills,
                experience_summary=analysis.experience_summary,
                certifications=analysis.certifications,
                status=ResumeStatus.PARSED.value,
                parsed_at=datetime.utcnow()
            )

            logger.info(f"Resume {resume_id} parsed successfully")

            # Update employee record with extracted skills
            resume = await Resume.update(resume_id, status=ResumeStatus.PARSED.value)
            if resume and analysis.skills:
                await Employee.update(
                    resume.employee_id,
                    skills=analysis.skills,
                    experience=f"{analysis.years_of_experience} years" if analysis.years_of_experience else None
                )

            return analysis

        except Exception as e:
            logger.error(f"Error parsing resume {resume_id}: {e}")
            await Resume.update(
                resume_id,
                status=ResumeStatus.FAILED.value,
                parse_error=str(e)
            )
            raise

    def _extract_text_from_file(self, file_content: bytes, file_type: str) -> str:
        """Extract text from PDF or DOCX file"""
        try:
            if file_type == "application/pdf" or file_type.endswith("pdf"):
                return self._extract_text_from_pdf(file_content)
            elif file_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
                return self._extract_text_from_docx(file_content)
            else:
                # Try as plain text
                return file_content.decode('utf-8', errors='ignore')
        except Exception as e:
            logger.error(f"Error extracting text from file: {e}")
            return ""

    def _extract_text_from_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF file"""
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return ""

    def _extract_text_from_docx(self, file_content: bytes) -> str:
        """Extract text from DOCX file"""
        try:
            doc_file = io.BytesIO(file_content)
            doc = Document(doc_file)
            
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {e}")
            return ""

    async def get_resume_by_employee_id(
        self,
        employee_id: UUID
    ) -> Optional[ResumeResponse]:
        """Get resume for an employee"""
        try:
            resume = await Resume.get_by_employee_id(employee_id)
            if resume:
                return ResumeResponse.model_validate(resume.to_dict())
            return None
        except Exception as e:
            logger.error(f"Error fetching resume: {e}")
            raise

    async def get_resume_analysis(
        self,
        employee_id: UUID
    ) -> Optional[ResumeAnalysisResponse]:
        """Get parsed resume analysis"""
        try:
            resume = await Resume.get_by_employee_id(employee_id)
            if resume and resume.ai_parsed_json:
                return ResumeAnalysisResponse(**resume.ai_parsed_json)
            return None
        except Exception as e:
            logger.error(f"Error fetching resume analysis: {e}")
            raise


# Global instance
resume_service = ResumeService()

