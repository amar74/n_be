"""
Opportunity AI Analysis Service
Provides comprehensive AI analysis for opportunities including:
- Competition analysis
- Technical fit analysis
- Financial predictions
- Strategic recommendations
"""
from typing import Dict, Any, List, Optional
from uuid import UUID
import google.generativeai as genai
from app.environment import environment
from app.utils.logger import get_logger
from app.models.opportunity import Opportunity
from app.models.opportunity_tabs import (
    OpportunityOverview,
    OpportunityCompetitor,
    OpportunityStrategy
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json
import re
import asyncio
from functools import lru_cache

logger = get_logger("opportunity_ai_analysis")

# Configure Gemini with fallback models
genai.configure(api_key=environment.GEMINI_API_KEY)

# Try to use newer models, fallback to gemini-pro
def get_model():
    """Get the best available Gemini model."""
    try:
        # Try gemini-1.5-pro first (better for complex analysis)
        return genai.GenerativeModel('gemini-1.5-pro')
    except Exception:
        try:
            # Fallback to gemini-1.5-flash (faster, still good)
            return genai.GenerativeModel('gemini-1.5-flash')
        except Exception:
            # Final fallback to gemini-pro
            return genai.GenerativeModel('gemini-pro')

model = get_model()


class OpportunityAIAnalysisService:
    """Service for comprehensive AI analysis of opportunities."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = get_model()
        self._cache = {}  # Simple in-memory cache for analysis results
    
    async def _call_ai_with_retry(
        self,
        prompt: str,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ) -> str:
        """Call AI model with retry logic and better error handling."""
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config={
                        "temperature": 0.7,
                        "top_p": 0.95,
                        "top_k": 40,
                        "max_output_tokens": 8192,
                    }
                )
                return response.text
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"AI call failed (attempt {attempt + 1}/{max_retries}): {e}. Retrying...")
                    await asyncio.sleep(retry_delay * (attempt + 1))
                else:
                    logger.error(f"AI call failed after {max_retries} attempts: {e}")
                    raise
    
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON response with multiple fallback strategies."""
        if not response_text:
            return {"error": "Empty response from AI"}
        
        # Clean up response text
        response_text = response_text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            response_text = response_text.strip("```")
            # Remove language identifier
            lines = response_text.split("\n")
            if lines[0].strip() in ["json", "JSON"]:
                lines = lines[1:]
            response_text = "\n".join(lines).strip()
        
        # Try to find JSON object in the response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(0)
        
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parsing failed: {e}. Attempting to fix...")
            
            # Try to fix common JSON issues
            # Remove trailing commas
            response_text = re.sub(r',\s*}', '}', response_text)
            response_text = re.sub(r',\s*]', ']', response_text)
            
            # Fix unquoted keys
            response_text = re.sub(r'(\w+):', r'"\1":', response_text)
            
            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON after fixes. Response: {response_text[:500]}")
                # Return a structured error response
                return {
                    "error": "Failed to parse AI response",
                    "raw_response": response_text[:1000],
                    "parse_error": str(e)
                }
    
    async def analyze_competition(
        self,
        opportunity: Opportunity,
        overview: Optional[OpportunityOverview] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze competition for an opportunity.
        Identifies potential competitors and their strengths/weaknesses.
        """
        try:
            # Check cache first
            if use_cache:
                cache_key = self._get_cache_key(opportunity.id, "competition")
                cached_result = self._get_cached_result(cache_key)
                if cached_result:
                    return cached_result
            project_value_str = f"${opportunity.project_value:,.0f}" if opportunity.project_value else 'TBD'
            description = ""
            if overview and overview.project_description:
                description = overview.project_description[:2000]  # Increased context
            elif opportunity.description:
                description = opportunity.description[:2000]
            else:
                description = 'No description available'
            
            project_context = f"""
Project: {opportunity.project_name}
Client: {opportunity.client_name}
Value: {project_value_str}
Sector: {opportunity.market_sector or 'Not specified'}
Location: {opportunity.state or 'Not specified'}
Stage: {opportunity.stage.value if opportunity.stage else 'Not specified'}
Risk Level: {opportunity.risk_level.value if opportunity.risk_level else 'Not specified'}
Match Score: {opportunity.match_score or 'N/A'}
Description: {description}
"""
            
            prompt = f"""You are an expert competitive intelligence analyst specializing in infrastructure, consulting, and engineering projects.

Analyze the following opportunity and provide comprehensive competitive intelligence:

{project_context}

**Your Task:**
1. Identify 3-7 potential competitors who are likely to bid on this project
2. Assess each competitor's threat level and capabilities
3. Identify market dynamics and competitive landscape
4. Provide actionable recommendations for competitive positioning

**Output Format (JSON only, no markdown):**
{{
  "competitors": [
    {{
      "company_name": "string (actual company name if known, or 'Typical Competitor Type' if unknown)",
      "threat_level": "High|Medium|Low",
      "strengths": ["string", ...],
      "weaknesses": ["string", ...],
      "win_probability": number (0-100, estimated probability they win if we don't bid strategically),
      "differentiation_opportunities": ["string", ...],
      "market_position": "string (e.g., 'Market Leader', 'Niche Player', 'Price Competitor')"
    }}
  ],
  "market_landscape": "string (2-3 sentence description of the competitive market)",
  "competitive_advantages": ["string", ...],
  "recommendations": ["string", ...],
  "market_trends": ["string", ...],
  "pricing_insights": "string (brief insight on expected pricing dynamics)"
}}

**Guidelines:**
- Be specific and actionable
- Base analysis on project type, sector, and location
- Consider both direct and indirect competitors
- Focus on differentiation opportunities
- Provide realistic win probability estimates

Return ONLY valid JSON, no additional text."""

            response_text = await self._call_ai_with_retry(prompt)
            analysis = self._parse_json_response(response_text)
            
            if "error" in analysis:
                logger.error(f"Error in competition analysis: {analysis.get('error')}")
                return {"competitors": [], "error": analysis.get("error")}
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing competition: {e}")
            return {"competitors": [], "error": str(e)}
    
    async def analyze_technical_fit(
        self,
        opportunity: Opportunity,
        overview: Optional[OpportunityOverview] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze technical fit by comparing opportunity requirements with firm capabilities.
        Integrates with Resource module skill matrix.
        """
        try:
            # Check cache first
            if use_cache:
                cache_key = self._get_cache_key(opportunity.id, "technical")
                cached_result = self._get_cached_result(cache_key)
                if cached_result:
                    return cached_result
            scope_items = overview.project_scope if overview and overview.project_scope else []
            scope_text = "\n".join([f"- {item}" for item in scope_items[:20]])
            
            # Get available skills from employees/resources
            available_skills = await self._get_organization_skills(opportunity.org_id)
            
            project_context = f"""
Project: {opportunity.project_name}
Sector: {opportunity.market_sector or 'Not specified'}
Scope Items:
{scope_text if scope_text else (overview.project_description[:1000] if overview and overview.project_description else 'No scope details')}

Available Organization Skills: {', '.join(available_skills[:50]) if available_skills else 'Not available'}
"""
            
            prompt = f"""You are a technical capability analyst for a consulting/engineering firm.

Analyze the technical fit for this opportunity:

{project_context}

Provide analysis in JSON format:
{{
  "required_skills": ["string", ...],
  "required_expertise": ["string", ...],
  "technical_gaps": ["string", ...],
  "technical_strengths": ["string", ...],
  "fit_score": number (0-100),
  "skill_match_percentage": number (0-100),
  "team_recommendations": [
    {{
      "role": "string",
      "required_skills": ["string", ...],
      "experience_level": "string",
      "suggested_employees": ["employee_id or name", ...]
    }}
  ],
  "resource_requirements": {{
    "team_size": number,
    "duration_estimate": "string",
    "key_roles": ["string", ...]
  }},
  "recommendations": ["string", ...]
}}

Focus on:
- Skills and expertise required
- Compare required skills with available organization skills
- Identify gaps in our capabilities
- Team composition recommendations with specific employee suggestions
- Resource requirements

Return ONLY valid JSON."""

            response_text = await self._call_ai_with_retry(prompt)
            analysis = self._parse_json_response(response_text)
            
            if "error" in analysis:
                logger.error(f"Error in technical fit analysis: {analysis.get('error')}")
                return {"fit_score": 0, "error": analysis.get("error")}
            
            # Enhance with actual employee matching
            if available_skills and analysis.get("required_skills"):
                matching_employees = await self._find_matching_employees(
                    opportunity.org_id,
                    analysis.get("required_skills", [])
                )
                analysis["available_team_members"] = matching_employees
                analysis["skill_match_percentage"] = self._calculate_skill_match(
                    analysis.get("required_skills", []),
                    available_skills
                )
            
            # Cache successful result
            if use_cache and "error" not in analysis:
                cache_key = self._get_cache_key(opportunity.id, "technical")
                self._set_cached_result(cache_key, analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing technical fit: {e}")
            return {"fit_score": 0, "error": str(e)}
    
    async def _get_organization_skills(self, org_id: UUID) -> List[str]:
        """Get all skills from employees in the organization."""
        try:
            from app.models.employee import Employee
            from sqlalchemy import select
            
            stmt = select(Employee).where(
                Employee.company_id == org_id,
                Employee.status.in_(["accepted", "active"])
            )
            result = await self.db.execute(stmt)
            employees = result.scalars().all()
            
            all_skills = set()
            for emp in employees:
                if emp.skills:
                    all_skills.update(emp.skills)
                if emp.ai_suggested_skills:
                    all_skills.update(emp.ai_suggested_skills)
            
            return list(all_skills)
        except Exception as e:
            logger.error(f"Error getting organization skills: {e}")
            return []
    
    async def _find_matching_employees(
        self,
        org_id: UUID,
        required_skills: List[str]
    ) -> List[Dict[str, Any]]:
        """Find employees matching required skills."""
        try:
            from app.models.employee import Employee
            from sqlalchemy import select
            
            stmt = select(Employee).where(
                Employee.company_id == org_id,
                Employee.status.in_(["accepted", "active"])
            )
            result = await self.db.execute(stmt)
            employees = result.scalars().all()
            
            matches = []
            for emp in employees:
                emp_skills = set((emp.skills or []) + (emp.ai_suggested_skills or []))
                required_skills_set = set([s.lower() for s in required_skills])
                emp_skills_lower = set([s.lower() for s in emp_skills])
                
                matched_skills = required_skills_set.intersection(emp_skills_lower)
                match_percentage = (len(matched_skills) / len(required_skills_set) * 100) if required_skills_set else 0
                
                if match_percentage > 0:
                    matches.append({
                        "id": str(emp.id),
                        "name": emp.name,
                        "job_title": emp.job_title,
                        "matched_skills": list(matched_skills),
                        "match_percentage": round(match_percentage, 1),
                        "all_skills": list(emp_skills)
                    })
            
            # Sort by match percentage
            matches.sort(key=lambda x: x["match_percentage"], reverse=True)
            return matches[:10]  # Top 10 matches
        except Exception as e:
            logger.error(f"Error finding matching employees: {e}")
            return []
    
    def _calculate_skill_match(self, required_skills: List[str], available_skills: List[str]) -> float:
        """Calculate percentage of required skills that are available."""
        if not required_skills:
            return 100.0
        
        required_lower = set([s.lower() for s in required_skills])
        available_lower = set([s.lower() for s in available_skills])
        
        matched = required_lower.intersection(available_lower)
        return (len(matched) / len(required_lower) * 100) if required_lower else 0.0
    
    async def analyze_financial_viability(
        self,
        opportunity: Opportunity,
        overview: Optional[OpportunityOverview] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze financial viability and provide predictions.
        """
        try:
            # Check cache first
            if use_cache:
                cache_key = self._get_cache_key(opportunity.id, "financial")
                cached_result = self._get_cached_result(cache_key)
                if cached_result:
                    return cached_result
            project_value = opportunity.project_value or 0
            project_value_str = f"${project_value:,.0f}" if project_value > 0 else 'TBD'
            deadline_str = opportunity.deadline.isoformat() if opportunity.deadline else 'TBD'
            
            # Get scope information if available
            scope_text = ""
            if overview and overview.project_scope:
                scope_text = "\n".join([f"- {item}" for item in overview.project_scope[:15]])
            elif overview and overview.project_description:
                scope_text = overview.project_description[:1000]
            
            project_context = f"""
Project: {opportunity.project_name}
Client: {opportunity.client_name}
Project Value: {project_value_str}
Sector: {opportunity.market_sector or 'Not specified'}
Location: {opportunity.state or 'Not specified'}
Deadline: {deadline_str}
Stage: {opportunity.stage.value if opportunity.stage else 'Not specified'}
Scope/Description:
{scope_text if scope_text else 'No scope details available'}
"""
            
            prompt = f"""You are an expert financial analyst specializing in infrastructure, consulting, and engineering project financial analysis.

Analyze the financial viability and provide comprehensive financial projections for this opportunity:

{project_context}

**Your Task:**
1. Estimate realistic revenue, costs, and profit margins
2. Provide budget breakdown by category
3. Assess financial risks and mitigation strategies
4. Create revenue scenarios (best/worst/most likely)
5. Provide actionable financial recommendations

**Output Format (JSON only, no markdown):**
{{
  "projected_revenue": number (in USD, based on project value or realistic estimate),
  "estimated_costs": number (in USD, total project costs),
  "profit_margin_percentage": number (0-100, calculated as ((revenue - costs) / revenue) * 100),
  "break_even_analysis": {{
    "break_even_point": "string (e.g., 'Month 8' or '60% completion')",
    "risk_factors": ["string", ...],
    "break_even_revenue": number (minimum revenue needed)
  }},
  "budget_recommendations": [
    {{
      "category": "string (e.g., 'Labor', 'Materials', 'Equipment', 'Overhead', 'Contingency')",
      "estimated_amount": number (in USD),
      "percentage": number (0-100, percentage of total budget)
    }}
  ],
  "financial_risks": ["string", ...],
  "revenue_scenarios": {{
    "best_case": number (optimistic revenue projection),
    "worst_case": number (conservative revenue projection),
    "most_likely": number (realistic revenue projection)
  }},
  "cost_breakdown": {{
    "direct_costs": number,
    "indirect_costs": number,
    "overhead": number,
    "contingency": number
  }},
  "recommendations": ["string", ...],
  "financial_health_score": number (0-100, overall financial viability score)
}}

**Guidelines:**
- Use realistic industry benchmarks for cost estimates
- Consider project type, sector, and location in estimates
- Include appropriate contingency (typically 10-20%)
- Be conservative in worst-case scenarios
- Provide actionable recommendations

Return ONLY valid JSON, no additional text."""

            response_text = await self._call_ai_with_retry(prompt)
            analysis = self._parse_json_response(response_text)
            
            if "error" in analysis:
                logger.error(f"Error in competition analysis: {analysis.get('error')}")
                return {"competitors": [], "error": analysis.get("error")}
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing financial viability: {e}")
            return {"error": str(e)}
    
    async def generate_strategic_recommendations(
        self,
        opportunity: Opportunity,
        competition_analysis: Optional[Dict[str, Any]] = None,
        technical_analysis: Optional[Dict[str, Any]] = None,
        financial_analysis: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate strategic recommendations including go/no-go decision.
        """
        try:
            analyses_summary = f"""
Competition Analysis: {competition_analysis.get('market_landscape', 'N/A')[:500] if competition_analysis else 'Not available'}
Technical Fit Score: {technical_analysis.get('fit_score', 'N/A') if technical_analysis else 'Not available'}
Financial Margin: {financial_analysis.get('profit_margin_percentage', 'N/A') if financial_analysis else 'Not available'}%
"""
            
            project_value_str = f"${opportunity.project_value:,.0f}" if opportunity.project_value else 'TBD'
            
            project_context = f"""
Project: {opportunity.project_name}
Client: {opportunity.client_name}
Value: {project_value_str}
Stage: {opportunity.stage.value if opportunity.stage else 'Not specified'}
Risk Level: {opportunity.risk_level.value if opportunity.risk_level else 'Not specified'}
Match Score: {opportunity.match_score or 'N/A'}
Sector: {opportunity.market_sector or 'Not specified'}
Location: {opportunity.state or 'Not specified'}
Deadline: {opportunity.deadline.isoformat() if opportunity.deadline else 'TBD'}

**Analysis Summary:**
{analyses_summary}
"""
            
            prompt = f"""You are a senior strategic advisor and decision-maker for a consulting/engineering firm.

Based on the comprehensive analysis provided, make a strategic go/no-go decision and provide actionable recommendations:

{project_context}

**Your Task:**
1. Make a clear Go/No-Go/Conditional decision with confidence level
2. Assess strategic value and win probability
3. Provide prioritized action strategies
4. Identify key success factors and risks
5. Recommend next steps and timeline

**Output Format (JSON only, no markdown):**
{{
  "go_no_go_decision": "Go|No-Go|Conditional",
  "decision_confidence": number (0-100, how confident you are in this decision),
  "decision_reasons": ["string", ...],
  "strategic_value": "High|Medium|Low",
  "win_probability": number (0-100, estimated probability of winning if we pursue),
  "recommended_strategies": [
    {{
      "strategy": "string (specific, actionable strategy)",
      "priority": number (1-10, 10 = highest priority),
      "rationale": "string (why this strategy matters)",
      "timeline": "string (when to execute)"
    }}
  ],
  "key_success_factors": ["string", ...],
  "risk_mitigation": ["string", ...],
  "next_steps": ["string", ...],
  "timeline_recommendations": "string (overall project timeline and key milestones)",
  "resource_requirements": {{
    "team_size": number,
    "key_roles": ["string", ...],
    "estimated_effort": "string"
  }},
  "roi_estimate": number (estimated return on investment percentage)
}}

**Decision Guidelines:**
- **Go**: Strong fit, good win probability, strategic value, manageable risks
- **No-Go**: Poor fit, low win probability, high risks, low strategic value
- **Conditional**: Good potential but requires specific conditions (e.g., team availability, pricing, scope changes)

**Focus Areas:**
- Be decisive and clear in recommendation
- Base decision on all provided analyses
- Consider strategic value beyond just financials
- Provide actionable, prioritized strategies
- Identify realistic risks and mitigations

Return ONLY valid JSON, no additional text."""

            response_text = await self._call_ai_with_retry(prompt)
            recommendations = self._parse_json_response(response_text)
            
            if "error" in recommendations:
                logger.error(f"Error in strategic recommendations: {recommendations.get('error')}")
                return {"go_no_go_decision": "Conditional", "error": recommendations.get("error")}
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating strategic recommendations: {e}")
            return {"go_no_go_decision": "Conditional", "error": str(e)}
    
    async def perform_comprehensive_analysis(
        self,
        opportunity_id: UUID
    ) -> Dict[str, Any]:
        """
        Perform comprehensive AI analysis including all aspects.
        """
        try:
            # Get opportunity
            opportunity = await Opportunity.get_by_id(opportunity_id, None)  # org_id check handled elsewhere
            if not opportunity:
                return {"error": "Opportunity not found"}
            
            # Get overview if available
            stmt = select(OpportunityOverview).where(
                OpportunityOverview.opportunity_id == opportunity_id
            )
            result = await self.db.execute(stmt)
            overview = result.scalar_one_or_none()
            
            # Run all analyses
            competition = await self.analyze_competition(opportunity, overview)
            technical = await self.analyze_technical_fit(opportunity, overview)
            financial = await self.analyze_financial_viability(opportunity, overview)
            recommendations = await self.generate_strategic_recommendations(
                opportunity,
                competition,
                technical,
                financial
            )
            
            return {
                "opportunity_id": str(opportunity_id),
                "competition_analysis": competition,
                "technical_analysis": technical,
                "financial_analysis": financial,
                "strategic_recommendations": recommendations,
                "summary": {
                    "win_probability": recommendations.get("win_probability", 0),
                    "go_no_go": recommendations.get("go_no_go_decision", "Conditional"),
                    "strategic_value": recommendations.get("strategic_value", "Medium"),
                    "fit_score": technical.get("fit_score", 0)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {e}")
            return {"error": str(e)}

