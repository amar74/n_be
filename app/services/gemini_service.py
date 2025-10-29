import os
import json
import logging
from typing import Dict, Any, List, Optional
import google.generativeai as genai
from app.schemas.employee import AIRoleSuggestionResponse, ResumeAnalysisResponse

logger = logging.getLogger(__name__)

class GeminiService:
    """Service for Gemini AI integration"""
    
    def __init__(self):
        # Check for both GEMINI_API_KEY and VITE_GEMINI_API_KEY
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("VITE_GEMINI_API_KEY", "")
        if not api_key:
            logger.warning("GEMINI_API_KEY not set. AI features will not work.")
            self.enabled = False
            return
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.enabled = True
        logger.info("Gemini AI Service initialized successfully")

    async def suggest_role_and_skills(
        self,
        name: str,
        job_title: Optional[str] = None,
        department: Optional[str] = None,
        company_industry: str = "Technology Consulting"
    ) -> AIRoleSuggestionResponse:
        """
        Use Gemini AI to suggest role, skills, and bill rate based on job title and context
        """
        if not self.enabled:
            # Return fallback response
            return AIRoleSuggestionResponse(
                suggested_role="Developer",
                suggested_department=department or "Engineering",
                suggested_skills=["General Skills"],
                confidence=0.5,
                bill_rate_suggestion=150.0
            )

        try:
            prompt = f"""
You are an HR AI assistant for a contractor and real estate SaaS platform. Help suggest roles and skills for new employees in construction, real estate, and contractor industries.

Employee Information:
- Name: {name}
- Job Title: {job_title or "Not specified"}
- Department: {department or "Not specified"}
- Company Industry: {company_industry}

Based on the job title and department, suggest the most appropriate:
1. Role - Can be ANY job title relevant to construction/real estate/contractor industry (e.g., Contractor, Site Engineer, Mason, Plumber, Electrician, Project Manager, Architect, Civil Engineer, Labour Supervisor, Safety Officer, etc.)
2. Department - Can be: Construction, Civil Engineering, Electrical, Plumbing, HVAC, Architecture, Site Management, Quality Control, Safety & Compliance, Procurement, Operations, HR, Finance, Sales, Legal, Administration, IT
3. Top 5 relevant skills for this role in construction/contractor industry
4. Appropriate hourly bill rate (in USD) for this role in the industry

Respond ONLY with valid JSON in this exact format:
{{
  "suggested_role": "Role Name",
  "suggested_department": "Department Name",
  "suggested_skills": ["skill1", "skill2", "skill3", "skill4", "skill5"],
  "confidence": 0.95,
  "bill_rate_suggestion": 200.0
}}

Do not include any explanation, only the JSON object.
"""

            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Try to extract JSON from response
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            data = json.loads(response_text)
            
            logger.info(f"AI role suggestion successful for {name}: {data.get('suggested_role')}")
            
            return AIRoleSuggestionResponse(
                suggested_role=data.get("suggested_role", "Developer"),
                suggested_department=data.get("suggested_department", department or "Engineering"),
                suggested_skills=data.get("suggested_skills", []),
                confidence=data.get("confidence", 0.85),
                bill_rate_suggestion=data.get("bill_rate_suggestion", 150.0)
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini JSON response: {e}")
            logger.error(f"Response text: {response_text}")
            # Return fallback
            return self._get_fallback_role_suggestion(job_title, department)
        except Exception as e:
            logger.error(f"Error in Gemini role suggestion: {e}")
            return self._get_fallback_role_suggestion(job_title, department)

    def _get_fallback_role_suggestion(
        self, 
        job_title: Optional[str], 
        department: Optional[str]
    ) -> AIRoleSuggestionResponse:
        """Fallback role suggestion based on keywords for contractor/real estate industry"""
        title_lower = (job_title or "").lower()
        
        # Construction & Contractor roles
        if any(word in title_lower for word in ["contractor", "general contractor"]):
            return AIRoleSuggestionResponse(
                suggested_role="Contractor",
                suggested_department="Construction",
                suggested_skills=["Project Management", "Cost Estimation", "Site Supervision", "Contract Negotiation", "Quality Control"],
                confidence=0.7,
                bill_rate_suggestion=180.0
            )
        elif any(word in title_lower for word in ["site engineer", "site", "civil engineer"]):
            return AIRoleSuggestionResponse(
                suggested_role="Site Engineer",
                suggested_department="Civil Engineering",
                suggested_skills=["AutoCAD", "Site Planning", "Construction Management", "Quality Assurance", "Blueprint Reading"],
                confidence=0.7,
                bill_rate_suggestion=150.0
            )
        elif any(word in title_lower for word in ["architect", "design architect"]):
            return AIRoleSuggestionResponse(
                suggested_role="Architect",
                suggested_department="Architecture",
                suggested_skills=["AutoCAD", "Revit", "3D Modeling", "Building Codes", "Project Design"],
                confidence=0.7,
                bill_rate_suggestion=200.0
            )
        elif any(word in title_lower for word in ["plumber", "plumbing"]):
            return AIRoleSuggestionResponse(
                suggested_role="Plumber",
                suggested_department="Plumbing",
                suggested_skills=["Pipe Installation", "Leak Detection", "Fixture Installation", "Drainage Systems", "Safety Protocols"],
                confidence=0.7,
                bill_rate_suggestion=80.0
            )
        elif any(word in title_lower for word in ["electrician", "electrical"]):
            return AIRoleSuggestionResponse(
                suggested_role="Electrician",
                suggested_department="Electrical",
                suggested_skills=["Wiring", "Circuit Installation", "Electrical Safety", "Troubleshooting", "Code Compliance"],
                confidence=0.7,
                bill_rate_suggestion=85.0
            )
        elif any(word in title_lower for word in ["mason", "bricklayer"]):
            return AIRoleSuggestionResponse(
                suggested_role="Mason",
                suggested_department="Construction",
                suggested_skills=["Bricklaying", "Concrete Work", "Plastering", "Measurements", "Tool Operation"],
                confidence=0.7,
                bill_rate_suggestion=70.0
            )
        elif any(word in title_lower for word in ["carpenter", "woodwork"]):
            return AIRoleSuggestionResponse(
                suggested_role="Carpenter",
                suggested_department="Construction",
                suggested_skills=["Woodworking", "Frame Construction", "Finish Work", "Blueprint Reading", "Tool Operation"],
                confidence=0.7,
                bill_rate_suggestion=75.0
            )
        elif any(word in title_lower for word in ["foreman", "supervisor", "site supervisor"]):
            return AIRoleSuggestionResponse(
                suggested_role="Site Supervisor",
                suggested_department="Site Management",
                suggested_skills=["Team Leadership", "Site Coordination", "Safety Management", "Progress Tracking", "Quality Control"],
                confidence=0.7,
                bill_rate_suggestion=120.0
            )
        elif any(word in title_lower for word in ["safety officer", "safety engineer"]):
            return AIRoleSuggestionResponse(
                suggested_role="Safety Officer",
                suggested_department="Safety & Compliance",
                suggested_skills=["OSHA Compliance", "Risk Assessment", "Safety Training", "Incident Investigation", "Safety Protocols"],
                confidence=0.7,
                bill_rate_suggestion=100.0
            )
        elif any(word in title_lower for word in ["project manager", "manager"]):
            return AIRoleSuggestionResponse(
                suggested_role="Project Manager",
                suggested_department="Site Management",
                suggested_skills=["Project Planning", "Budget Management", "Team Coordination", "Stakeholder Communication", "Risk Management"],
                confidence=0.7,
                bill_rate_suggestion=250.0
            )
        elif any(word in title_lower for word in ["labour", "labor", "worker"]):
            return AIRoleSuggestionResponse(
                suggested_role="Labour Supervisor",
                suggested_department="Construction",
                suggested_skills=["Team Management", "Task Allocation", "Safety Compliance", "Progress Monitoring", "Quality Control"],
                confidence=0.7,
                bill_rate_suggestion=60.0
            )
        # Tech roles (if contractor has IT dept)
        elif any(word in title_lower for word in ["frontend", "react", "vue", "angular"]):
            return AIRoleSuggestionResponse(
                suggested_role="Developer",
                suggested_department="IT & Technology",
                suggested_skills=["React", "TypeScript", "JavaScript", "HTML/CSS", "Git"],
                confidence=0.7,
                bill_rate_suggestion=200.0
            )
        elif any(word in title_lower for word in ["backend", "node", "python", "java"]):
            return AIRoleSuggestionResponse(
                suggested_role="Developer",
                suggested_department="IT & Technology",
                suggested_skills=["Python", "Node.js", "SQL", "API Development", "Git"],
                confidence=0.7,
                bill_rate_suggestion=220.0
            )
        else:
            return AIRoleSuggestionResponse(
                suggested_role=job_title or "Contractor",
                suggested_department=department or "Construction",
                suggested_skills=["Industry Knowledge", "Communication", "Teamwork", "Safety Awareness", "Time Management"],
                confidence=0.5,
                bill_rate_suggestion=100.0
            )

    async def parse_resume(self, resume_text: str) -> ResumeAnalysisResponse:
        """
        Parse resume text using Gemini AI to extract structured information
        """
        if not self.enabled:
            return ResumeAnalysisResponse(
                skills=["Unable to parse - AI not configured"],
                experience_summary="AI parsing not available",
                certifications=[],
                job_titles=[],
                education=[],
            )

        try:
            prompt = f"""
You are an AI assistant specialized in parsing resumes.

Parse the following resume text and extract structured information.

Resume Text:
{resume_text[:4000]}

Extract and return ONLY a valid JSON object with this exact structure:
{{
  "full_name": "Full Name",
  "email": "email@example.com",
  "phone": "+1234567890",
  "skills": ["skill1", "skill2", "skill3", ...],
  "experience_summary": "Brief 2-3 sentence summary of work experience",
  "certifications": ["cert1", "cert2", ...],
  "job_titles": ["title1", "title2", ...],
  "education": ["degree1", "degree2", ...],
  "years_of_experience": 5
}}

Rules:
- Extract all technical and soft skills mentioned
- Provide a concise experience summary
- List all certifications found
- List previous job titles
- List educational qualifications
- Estimate years of experience based on work history
- If any field is not found, use an empty string or empty array
- Respond ONLY with the JSON object, no explanation

Do not include any text before or after the JSON object.
"""

            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean response
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            data = json.loads(response_text)
            
            logger.info(f"Resume parsed successfully. Found {len(data.get('skills', []))} skills")
            
            return ResumeAnalysisResponse(
                full_name=data.get("full_name"),
                email=data.get("email"),
                phone=data.get("phone"),
                skills=data.get("skills", []),
                experience_summary=data.get("experience_summary", ""),
                certifications=data.get("certifications", []),
                job_titles=data.get("job_titles", []),
                education=data.get("education", []),
                years_of_experience=data.get("years_of_experience")
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini resume response: {e}")
            logger.error(f"Response text: {response_text[:500]}")
            return ResumeAnalysisResponse(
                skills=[],
                experience_summary="Failed to parse resume",
                certifications=[],
                job_titles=[],
                education=[],
            )
        except Exception as e:
            logger.error(f"Error in Gemini resume parsing: {e}")
            return ResumeAnalysisResponse(
                skills=[],
                experience_summary=f"Error parsing resume: {str(e)}",
                certifications=[],
                job_titles=[],
                education=[],
            )

    async def generate_welcome_email(
        self,
        employee_name: str,
        role: str,
        company_name: str = "SoftiCation Business Suite"
    ) -> str:
        """
        Generate personalized welcome email using Gemini AI
        """
        if not self.enabled:
            return self._get_fallback_welcome_email(employee_name, role, company_name)

        try:
            prompt = f"""
Generate a short, professional, and friendly onboarding email for a new employee.

Details:
- Employee Name: {employee_name}
- Role: {role}
- Company: {company_name}

Requirements:
- Warm and welcoming tone
- Professional but not overly formal
- Include excitement about them joining
- Mention they've been assigned the {role} role
- Encourage them to log in and explore their dashboard
- Keep it concise (4-5 sentences)
- Add a simple emoji at the end

Do not include subject line, just the email body.
"""

            response = self.model.generate_content(prompt)
            email_body = response.text.strip()
            
            logger.info(f"Welcome email generated for {employee_name}")
            return email_body

        except Exception as e:
            logger.error(f"Error generating welcome email: {e}")
            return self._get_fallback_welcome_email(employee_name, role, company_name)

    def _get_fallback_welcome_email(
        self,
        employee_name: str,
        role: str,
        company_name: str
    ) -> str:
        """Fallback welcome email template"""
        return f"""Hi {employee_name},

Welcome to {company_name}! 🎉

Your account is ready! You've been assigned the role of {role}.

Log in to explore your dashboard and upcoming projects. If you have any questions, feel free to reach out to your team lead or HR.

Best regards,
The {company_name} Team"""


# Global instance
gemini_service = GeminiService()

