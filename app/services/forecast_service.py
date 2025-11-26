import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
import google.generativeai as genai
import uuid

from app.models.finance_planning import FinanceForecast
from app.schemas.finance import ForecastPeriodItem, ForecastCreate, ForecastResponse
from app.models.finance_planning import FinanceAnnualBudget
from app.services.finance_dashboard import get_overhead, get_revenue
from app.services.finance_planning import get_annual_budget_from_db

logger = logging.getLogger(__name__)


class ForecastService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("VITE_GEMINI_API_KEY", "")
        if not api_key:
            logger.warning("GEMINI_API_KEY not set. AI forecasting will use fallback methods.")
            self.ai_enabled = False
            return
        
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            self.ai_enabled = True
            logger.info("✅ AI Forecasting Service initialized with Gemini")
        except Exception as e:
            logger.warning(f"Failed to initialize Gemini: {e}. Using fallback methods.")
            self.ai_enabled = False
    
    async def _get_historical_data(
        self,
        db: AsyncSession,
        months: int = 12
    ) -> List[Dict[str, Any]]:
        """Fetch historical financial data for forecasting"""
        try:
            # Get recent budget data
            budget_result = await db.execute(
                select(FinanceAnnualBudget).order_by(desc(FinanceAnnualBudget.budget_year)).limit(1)
            )
            budget = budget_result.scalar_one_or_none()
            
            historical = []
            if budget:
                # Get revenue and expense lines
                from app.models.finance_planning import FinanceRevenueLine, FinanceExpenseLine
                
                revenue_result = await db.execute(
                    select(FinanceRevenueLine).where(FinanceRevenueLine.budget_id == budget.id)
                )
                expense_result = await db.execute(
                    select(FinanceExpenseLine).where(FinanceExpenseLine.budget_id == budget.id)
                )
                
                revenue_lines = revenue_result.scalars().all()
                expense_lines = expense_result.scalars().all()
                
                total_revenue = sum(line.target for line in revenue_lines)
                total_expenses = sum(line.target for line in expense_lines)
                
                # Generate monthly historical data (simplified - in production, use actual monthly data)
                monthly_revenue = total_revenue / 12
                monthly_expenses = total_expenses / 12
                
                current_date = datetime.now()
                for i in range(months, 0, -1):
                    month_date = current_date - timedelta(days=30 * i)
                    revenue = monthly_revenue * (1 + (i * 0.01))
                    expenses = monthly_expenses * (1 + (i * 0.005))
                    profit = revenue - expenses
                    margin = (profit / revenue) * 100 if revenue > 0 else 0.0
                    historical.append({
                        "period": month_date.strftime("%b %Y"),
                        "revenue": revenue,
                        "expenses": expenses,
                        "profit": profit,
                        "margin": margin
                    })
            
            return historical
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            return []
    
    async def generate_ai_forecast(
        self,
        historical_data: List[Dict[str, Any]],
        forecast_params: ForecastCreate
    ) -> tuple[List[ForecastPeriodItem], Optional[float], Optional[str]]:
        """Generate forecast using AI (Gemini) with timeout handling"""
        if not self.ai_enabled:
            return self._generate_fallback_forecast(historical_data, forecast_params)
        
        try:
            import asyncio
            
            # Prepare historical data summary for AI
            historical_summary = json.dumps(historical_data[-12:], indent=2)  # Last 12 months
            
            prompt = f"""
You are a financial forecasting AI expert. Analyze the historical financial data and generate accurate forecasts.

Historical Data (Last 12 months):
{historical_summary}

Forecasting Parameters:
- Model: {forecast_params.forecasting_model}
- Forecast Period: {forecast_params.forecast_period_months} months
- Market Growth Rate: {forecast_params.market_growth_rate}% annually
- Inflation Rate: {forecast_params.inflation_rate}% annually
- Seasonal Adjustment: {"Enabled" if forecast_params.seasonal_adjustment else "Disabled"}

Instructions:
1. Analyze the historical revenue, expenses, and profit trends
2. Apply the {forecast_params.forecasting_model} model appropriately
3. Consider market growth rate ({forecast_params.market_growth_rate}%) and inflation ({forecast_params.inflation_rate}%)
4. Apply seasonal adjustments if enabled
5. Generate realistic forecasts for the next {forecast_params.forecast_period_months} months
6. Ensure forecasts are conservative and realistic based on historical patterns
7. Calculate profit margins accurately

Return ONLY a valid JSON array with this exact structure:
[
  {{
    "period": "Jan 2026",
    "revenue": 450000.0,
    "expenses": 350000.0,
    "profit": 100000.0,
    "margin": 22.2
  }},
  ...
]

Rules:
- Period format: "MMM YYYY" (e.g., "Jan 2026", "Feb 2026")
- Revenue and expenses should show realistic growth/trends
- Profit = Revenue - Expenses
- Margin = (Profit / Revenue) * 100
- Ensure margins are realistic (typically 15-30% for consulting)
- Apply gradual growth, not sudden jumps
- Consider seasonality if seasonal adjustment is enabled

Respond ONLY with the JSON array, no explanation or markdown.
"""
            
            logger.info("Calling Gemini API for financial forecast generation")
            # Use asyncio.wait_for with timeout (25 seconds for forecast generation)
            response = await asyncio.wait_for(
                asyncio.to_thread(self.model.generate_content, prompt),
                timeout=25.0
            )
            response_text = response.text.strip()
            
            # Clean response
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            forecast_data = json.loads(response_text)
            
            # Convert to ForecastPeriodItem format
            forecast_items = [
                ForecastPeriodItem(
                    period=item["period"],
                    revenue=float(item["revenue"]),
                    expenses=float(item["expenses"]),
                    profit=float(item["profit"]),
                    margin=float(item["margin"])
                )
                for item in forecast_data
            ]
            
            # Generate AI insights with timeout (10 seconds)
            insights_prompt = f"""
Based on the forecast generated, provide 2-3 key insights about:
1. Revenue growth trajectory
2. Expense management considerations
3. Profit margin trends
4. Any risks or opportunities

Keep insights concise (2-3 sentences total).
"""
            try:
                insights_response = await asyncio.wait_for(
                    asyncio.to_thread(self.model.generate_content, insights_prompt),
                    timeout=10.0
                )
                ai_insights = insights_response.text.strip()
            except asyncio.TimeoutError:
                logger.warning("AI insights generation timed out, using default insights")
                ai_insights = "Forecast generated successfully. Review the data for trends and opportunities."
            
            # Calculate confidence score based on data quality
            confidence = min(95.0, 70.0 + (len(historical_data) * 2.0))
            
            logger.info(f"✅ AI forecast generated successfully: {len(forecast_items)} periods")
            return forecast_items, confidence, ai_insights
            
        except asyncio.TimeoutError:
            logger.error("❌ Gemini API timeout after 25s, falling back to statistical forecast")
            return self._generate_fallback_forecast(historical_data, forecast_params)
        except Exception as e:
            logger.error(f"Error generating AI forecast: {e}")
            logger.info("Falling back to statistical forecast")
            return self._generate_fallback_forecast(historical_data, forecast_params)
    
    def _generate_fallback_forecast(
        self,
        historical_data: List[Dict[str, Any]],
        forecast_params: ForecastCreate
    ) -> tuple[List[ForecastPeriodItem], Optional[float], Optional[str]]:
        """Fallback forecast using statistical methods when AI is unavailable"""
        if not historical_data:
            # Default values if no historical data
            base_revenue = 400000.0
            base_expenses = 300000.0
        else:
            # Calculate averages from historical data
            base_revenue = sum(d.get("revenue", 0) for d in historical_data) / len(historical_data)
            base_expenses = sum(d.get("expenses", 0) for d in historical_data) / len(historical_data)
        
        monthly_growth = forecast_params.market_growth_rate / 100 / 12
        monthly_inflation = forecast_params.inflation_rate / 100 / 12
        
        forecast_items = []
        current_date = datetime.now()
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        for i in range(1, forecast_params.forecast_period_months + 1):
            growth_factor = (1 + monthly_growth) ** i
            inflation_factor = (1 + monthly_inflation) ** i
            
            seasonal_factor = 1.0
            if forecast_params.seasonal_adjustment:
                # Apply seasonal variation (sine wave)
                import math
                seasonal_factor = 1 + (0.08 * math.sin((i - 1) / 12 * 2 * math.pi))
            
            revenue = base_revenue * growth_factor * seasonal_factor
            expenses = base_expenses * inflation_factor * seasonal_factor
            profit = revenue - expenses
            margin = (profit / revenue) * 100 if revenue > 0 else 0
            
            month_index = (current_date.month + i - 1) % 12
            year = current_date.year + ((current_date.month + i - 1) // 12)
            
            forecast_items.append(ForecastPeriodItem(
                period=f"{month_names[month_index]} {year}",
                revenue=round(revenue, 2),
                expenses=round(expenses, 2),
                profit=round(profit, 2),
                margin=round(margin, 2)
            ))
        
        insights = "Forecast generated using statistical methods. Consider reviewing with AI for enhanced accuracy."
        confidence = 75.0
        
        return forecast_items, confidence, insights
    
    async def save_forecast(
        self,
        db: AsyncSession,
        forecast_params: ForecastCreate,
        forecast_data: List[ForecastPeriodItem],
        historical_data: List[Dict[str, Any]],
        ai_confidence: Optional[float],
        ai_insights: Optional[str],
        user_id: Optional[uuid.UUID] = None,
        org_id: Optional[uuid.UUID] = None
    ) -> FinanceForecast:
        """Save forecast to database"""
        # Convert forecast_data to dict format for JSONB storage
        forecast_data_dict = []
        for item in forecast_data:
            if isinstance(item, ForecastPeriodItem):
                # Try model_dump() for Pydantic v2, fallback to dict() for v1
                if hasattr(item, 'model_dump'):
                    forecast_data_dict.append(item.model_dump())
                else:
                    forecast_data_dict.append(item.dict())
            elif isinstance(item, dict):
                forecast_data_dict.append(item)
            else:
                # Convert to dict manually
                forecast_data_dict.append({
                    "period": getattr(item, 'period', ''),
                    "revenue": getattr(item, 'revenue', 0.0),
                    "expenses": getattr(item, 'expenses', 0.0),
                    "profit": getattr(item, 'profit', 0.0),
                    "margin": getattr(item, 'margin', 0.0)
                })
        
        forecast = FinanceForecast(
            forecast_name=forecast_params.forecast_name or f"Forecast {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            forecasting_model=forecast_params.forecasting_model,
            forecast_period_months=forecast_params.forecast_period_months,
            market_growth_rate=forecast_params.market_growth_rate,
            inflation_rate=forecast_params.inflation_rate,
            seasonal_adjustment=forecast_params.seasonal_adjustment,
            forecast_data=forecast_data_dict,
            historical_data=historical_data,
            ai_confidence_score=ai_confidence,
            ai_insights=ai_insights,
            created_by=user_id,
            org_id=org_id
        )
        
        db.add(forecast)
        # Don't commit here - RequestTransactionMiddleware handles it
        # await db.commit() and await db.refresh() removed to avoid transaction conflicts
        
        logger.info(f"Forecast will be saved with transaction commit")
        return forecast
    
    async def get_forecast(
        self,
        db: AsyncSession,
        forecast_id: int
    ) -> Optional[FinanceForecast]:
        """Get forecast by ID"""
        result = await db.execute(
            select(FinanceForecast).where(FinanceForecast.id == forecast_id)
        )
        return result.scalar_one_or_none()
    
    async def list_forecasts(
        self,
        db: AsyncSession,
        org_id: Optional[uuid.UUID] = None,
        limit: int = 50
    ) -> List[FinanceForecast]:
        """List recent forecasts"""
        query = select(FinanceForecast).order_by(desc(FinanceForecast.created_at))
        
        if org_id:
            query = query.where(FinanceForecast.org_id == org_id)
        
        result = await db.execute(query.limit(limit))
        return list(result.scalars().all())


# Singleton instance
forecast_service = ForecastService()

