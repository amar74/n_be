import logging
from typing import Dict, Any, List, Optional
from uuid import UUID
import asyncio

from app.models.employee import Employee, Resume
from app.services.gemini_service import gemini_service

logger = logging.getLogger(__name__)


class AIAnalysisService:
    """
    Deep AI analysis service for comprehensive CV and candidate profile analysis
    Runs in background after employee/resume creation
    """

    @staticmethod
    async def deep_profile_analysis(employee_id: UUID, resume_text: Optional[str] = None) -> Dict[str, Any]:
        """
        Comprehensive AI analysis of employee profile
        Analyzes: Skills, Experience, Projects, Education, Certifications, Sector Expertise
        """
        try:
            logger.info(f"🤖 Starting deep AI analysis for employee {employee_id}")
            
            # Get employee data
            employee = await Employee.get_by_id(employee_id)
            if not employee:
                raise ValueError(f"Employee {employee_id} not found")

            # Get resume if available
            resume = None
            if not resume_text:
                from app.models.employee import Resume
                resume = await Resume.get_by_employee_id(employee_id)
                if resume and resume.file_url:
                    # Resume text would be extracted from file
                    resume_text = "Resume content placeholder"  # In production, extract from S3

            analysis_results = {}

            # Run multiple AI analyses in parallel
            tasks = [
                AIAnalysisService._analyze_skills_depth(employee, resume_text),
                AIAnalysisService._analyze_project_experience(employee, resume_text),
                AIAnalysisService._analyze_sector_expertise(employee, resume_text),
                AIAnalysisService._calculate_match_score(employee),
                AIAnalysisService._suggest_suitable_projects(employee),
                AIAnalysisService._extract_certifications(resume_text),
                AIAnalysisService._analyze_education_background(resume_text),
                AIAnalysisService._assess_leadership_experience(resume_text),
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            analysis_results = {
                'skills_analysis': results[0] if not isinstance(results[0], Exception) else None,
                'project_experience': results[1] if not isinstance(results[1], Exception) else None,
                'sector_expertise': results[2] if not isinstance(results[2], Exception) else None,
                'match_score': results[3] if not isinstance(results[3], Exception) else None,
                'suitable_projects': results[4] if not isinstance(results[4], Exception) else None,
                'certifications': results[5] if not isinstance(results[5], Exception) else None,
                'education': results[6] if not isinstance(results[6], Exception) else None,
                'leadership_assessment': results[7] if not isinstance(results[7], Exception) else None,
            }

            # Update employee record with analysis results
            await Employee.update(
                employee_id,
                ai_match_percentage=analysis_results.get('match_score', {}).get('percentage', 0),
                ai_match_reasons=analysis_results.get('match_score', {}).get('reasons', []),
                ai_suggested_skills=analysis_results.get('skills_analysis', {}).get('extracted_skills', []),
            )

            logger.info(f"✅ Deep AI analysis completed for employee {employee_id}")
            
            return analysis_results

        except Exception as e:
            logger.error(f"❌ Error in deep AI analysis: {e}")
            return {}

    @staticmethod
    async def _analyze_skills_depth(employee: Employee, resume_text: Optional[str]) -> Dict[str, Any]:
        """Analyze skills in depth using Gemini AI"""
        if not gemini_service.enabled or not resume_text:
            return {
                'extracted_skills': employee.skills or [],
                'skill_categories': [],
                'proficiency_levels': {},
            }

        try:
            prompt = f"""
Analyze the following candidate profile for an engineering/contractor consulting firm:

Job Title: {employee.job_title}
Current Skills: {', '.join(employee.skills or [])}
Department: {employee.department}
Experience: {employee.experience}

Resume excerpt: {resume_text[:2000] if resume_text else 'Not available'}

Extract and categorize skills into:
1. Technical Skills (software, tools, methodologies)
2. Domain Expertise (sectors, project types)
3. Soft Skills (leadership, communication, etc.)
4. Certifications & Licenses

Return JSON format:
{{
  "extracted_skills": ["skill1", "skill2", ...],
  "technical_skills": ["AutoCAD", "Revit", ...],
  "domain_expertise": ["Transportation", "Infrastructure", ...],
  "soft_skills": ["Leadership", "Communication", ...],
  "certifications": ["PE License", "PMP", ...],
  "proficiency_levels": {{"skill_name": "Expert/Advanced/Intermediate/Beginner"}}
}}
"""

            response = gemini_service.model.generate_content(prompt)
            import json
            result = json.loads(response.text.strip())
            return result

        except Exception as e:
            logger.error(f"Skills analysis error: {e}")
            return {'extracted_skills': employee.skills or []}

    @staticmethod
    async def _analyze_project_experience(employee: Employee, resume_text: Optional[str]) -> Dict[str, Any]:
        """Extract project experience, durations, and dollar values"""
        if not gemini_service.enabled or not resume_text:
            return {'projects': [], 'total_value': 0, 'avg_duration': 0}

        try:
            prompt = f"""
From this resume, extract all project experience with:
- Project name/type
- Duration (months/years)
- Dollar value (if mentioned)
- Role in project
- Technologies/methods used

Resume: {resume_text[:2000] if resume_text else ''}

Return JSON:
{{
  "projects": [
    {{"name": "Highway Expansion", "duration": "18 months", "value": 15000000, "role": "Lead Engineer", "technologies": ["AutoCAD", "Civil 3D"]}}
  ],
  "total_value": 50000000,
  "avg_duration_months": 12,
  "project_count": 5
}}
"""

            response = gemini_service.model.generate_content(prompt)
            import json
            result = json.loads(response.text.strip())
            return result

        except Exception as e:
            logger.error(f"Project experience analysis error: {e}")
            return {'projects': []}

    @staticmethod
    async def _analyze_sector_expertise(employee: Employee, resume_text: Optional[str]) -> Dict[str, Any]:
        """Identify sector expertise (Transportation, Infrastructure, etc.)"""
        if not gemini_service.enabled:
            return {'sectors': [], 'primary_sector': None}

        try:
            sectors = [
                'Transportation', 'Infrastructure', 'Environmental', 'Aviation',
                'Education', 'Healthcare', 'Energy', 'Water Resources',
                'Urban Planning', 'Industrial'
            ]

            prompt = f"""
Based on this professional profile, identify which sectors they have expertise in:

Job Title: {employee.job_title}
Department: {employee.department}
Skills: {', '.join(employee.skills or [])}

Available sectors: {', '.join(sectors)}

Return JSON:
{{
  "sectors": ["Transportation", "Infrastructure"],
  "primary_sector": "Transportation",
  "confidence": 0.85
}}
"""

            response = gemini_service.model.generate_content(prompt)
            import json
            result = json.loads(response.text.strip())
            return result

        except Exception as e:
            logger.error(f"Sector expertise analysis error: {e}")
            return {'sectors': []}

    @staticmethod
    async def _calculate_match_score(employee: Employee) -> Dict[str, Any]:
        """Calculate match percentage for current project demands"""
        try:
            # Simulate project demand matching
            # In production, this would compare against active projects

            skills = employee.skills or []
            skill_count = len(skills)
            
            # Simple scoring logic
            base_score = min(skill_count * 10, 70)  # Max 70 from skills
            experience_boost = 15 if employee.experience and 'years' in employee.experience.lower() else 0
            dept_match = 15 if employee.department else 0
            
            total_score = min(base_score + experience_boost + dept_match, 100)

            reasons = []
            if skill_count >= 5:
                reasons.append("Strong skill set")
            if employee.experience:
                reasons.append(f"Relevant experience: {employee.experience}")
            if employee.department:
                reasons.append(f"Department match: {employee.department}")

            return {
                'percentage': total_score,
                'reasons': reasons,
                'recommendation': 'High' if total_score >= 80 else 'Medium' if total_score >= 60 else 'Low'
            }

        except Exception as e:
            logger.error(f"Match score calculation error: {e}")
            return {'percentage': 0, 'reasons': []}

    @staticmethod
    async def _suggest_suitable_projects(employee: Employee) -> List[str]:
        """Suggest suitable projects based on skills and experience"""
        # Placeholder - would integrate with project module
        return ['Highway Expansion Project', 'Bridge Rehabilitation', 'Urban Transit Development']

    @staticmethod
    async def _extract_certifications(resume_text: Optional[str]) -> List[str]:
        """Extract professional licenses and certifications"""
        if not resume_text or not gemini_service.enabled:
            return []

        try:
            prompt = f"""
Extract all professional certifications, licenses, and qualifications from this resume:

{resume_text[:2000]}

Common in engineering/construction:
- PE (Professional Engineer)
- PMP (Project Management Professional)
- LEED AP (Green Building)
- OSHA certifications
- State licenses
- Technical certifications

Return JSON array: ["PE License - California", "PMP Certified", "OSHA 30-Hour"]
"""

            response = gemini_service.model.generate_content(prompt)
            import json
            certs = json.loads(response.text.strip())
            return certs if isinstance(certs, list) else []

        except Exception as e:
            logger.error(f"Certification extraction error: {e}")
            return []

    @staticmethod
    async def _analyze_education_background(resume_text: Optional[str]) -> Dict[str, Any]:
        """Extract education background"""
        if not resume_text or not gemini_service.enabled:
            return {'degrees': [], 'universities': []}

        try:
            prompt = f"""
Extract education background:

{resume_text[:2000]}

Return JSON:
{{
  "degrees": ["BS Civil Engineering", "MS Structural Engineering"],
  "universities": ["MIT", "Stanford"],
  "graduation_years": ["2010", "2012"]
}}
"""

            response = gemini_service.model.generate_content(prompt)
            import json
            education = json.loads(response.text.strip())
            return education

        except Exception as e:
            logger.error(f"Education analysis error: {e}")
            return {'degrees': []}

    @staticmethod
    async def _assess_leadership_experience(resume_text: Optional[str]) -> Dict[str, Any]:
        """Assess leadership and management experience"""
        if not resume_text or not gemini_service.enabled:
            return {'leadership_level': 'Individual Contributor', 'team_size': 0}

        try:
            prompt = f"""
Assess leadership experience from resume:

{resume_text[:2000]}

Return JSON:
{{
  "leadership_level": "Senior Manager",
  "team_size": 15,
  "management_years": 5,
  "leadership_skills": ["Team Building", "Strategic Planning"]
}}
"""

            response = gemini_service.model.generate_content(prompt)
            import json
            leadership = json.loads(response.text.strip())
            return leadership

        except Exception as e:
            logger.error(f"Leadership assessment error: {e}")
            return {'leadership_level': 'Individual Contributor'}

    @staticmethod
    async def bulk_analysis_queue(employee_ids: List[UUID]):
        """
        Queue multiple employees for background AI analysis
        For bulk upload scenarios
        """
        logger.info(f"📦 Queuing {len(employee_ids)} employees for background AI analysis")
        
        for emp_id in employee_ids:
            try:
                # Run analysis in background (in production, use Celery/Redis)
                asyncio.create_task(AIAnalysisService.deep_profile_analysis(emp_id))
                logger.info(f"✅ Queued analysis for employee {emp_id}")
            except Exception as e:
                logger.error(f"❌ Failed to queue analysis for {emp_id}: {e}")

        return {
            'queued': len(employee_ids),
            'status': 'processing',
            'message': f'{len(employee_ids)} candidates queued for AI analysis'
        }


# Global instance
ai_analysis_service = AIAnalysisService()

