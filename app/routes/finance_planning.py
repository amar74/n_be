"""
Finance planning API routes.

Serves planning data (annual snapshot and scenario planning) from the
mock service layer so the frontend can transition to API-driven data.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from datetime import datetime
import uuid

from app.db.session import get_request_transaction
from app.dependencies.user_auth import get_current_user
from app.schemas.auth import AuthUserResponse
from app.schemas.finance import (
    FinancePlanningAnnualResponse,
    FinancePlanningScenarioResponse,
    FinanceAnnualBudgetCreate,
    FinanceAnnualBudgetUpdate,
    FinancePlanningConfigUpdate,
    FinanceScenarioUpdate,
    ForecastCreate,
    ForecastResponse,
    ForecastListResponse,
    ForecastPeriodItem,
)
from app.services.finance_planning import (
    get_annual_planning_snapshot,
    get_annual_budget_from_db,
    get_scenario_planning_snapshot,
    save_annual_budget,
    update_annual_budget,
    save_planning_config,
    update_scenario,
)
from app.models.finance_planning import (
    FinanceAnnualBudget,
    FinanceRevenueLine,
    FinanceExpenseLine,
    FinanceBusinessUnit,
    FinancePlanningScenario,
    FinancePlanningConfig,
    FinanceForecast,
)


router = APIRouter(prefix="/v1/finance/planning", tags=["Finance Planning"])


@router.get("/annual", response_model=FinancePlanningAnnualResponse)
async def read_finance_planning_annual(
    budget_year: Optional[str] = None,
    db: AsyncSession = Depends(get_request_transaction),
) -> FinancePlanningAnnualResponse:
    """
    Return the annual planning snapshot (budget, revenue/expense breakdown, thresholds).
    Fetches from database if available, otherwise returns mock data.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Try to get from database first
    db_budget = await get_annual_budget_from_db(db, budget_year)
    
    if db_budget:
        logger.info(f"Returning budget from database for year: {budget_year or 'latest'}")
        return db_budget
    
    # Fallback to mock data if no database record exists
    logger.info("No budget found in database, returning mock data")
    return get_annual_planning_snapshot()


@router.post("/annual", response_model=FinancePlanningAnnualResponse)
async def create_finance_planning_annual(
    budget_data: FinanceAnnualBudgetCreate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: AuthUserResponse = Depends(get_current_user),
) -> FinancePlanningAnnualResponse:
    """
    Create or update annual budget planning data.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Saving annual budget for year {budget_data.budget_year}, user: {current_user.id}")
        logger.info(f"Budget data: revenue_lines={len(budget_data.revenue_lines)}, expense_lines={len(budget_data.expense_lines)}, business_units={len(budget_data.business_units) if budget_data.business_units else 0}")
        budget = await save_annual_budget(db, budget_data, current_user.id)
        logger.info(f"Successfully saved budget ID: {budget.id}")
        # Return updated data from database
        db_response = await get_annual_budget_from_db(db, budget_data.budget_year)
        if db_response:
            return db_response
        # Fallback to mock if conversion fails
        return get_annual_planning_snapshot()
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Error saving annual budget: {str(e)}\n{error_trace}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save annual budget: {str(e)}"
        )


@router.patch("/annual", response_model=FinancePlanningAnnualResponse)
async def update_finance_planning_annual(
    budget_data: FinanceAnnualBudgetUpdate,
    budget_year: Optional[str] = None,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: AuthUserResponse = Depends(get_current_user),
) -> FinancePlanningAnnualResponse:
    """
    Update annual budget planning data.
    If budget doesn't exist, create it using POST endpoint data.
    """
    try:
        year = budget_year or "2026"
        await update_annual_budget(db, year, budget_data, current_user.id)
        return get_annual_planning_snapshot()
    except ValueError as e:
        # Budget doesn't exist, but we can't create it here with PATCH
        # Return error suggesting to use POST instead
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Budget for year {year} not found. Please create it first using POST /annual"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update annual budget: {str(e)}"
        )


@router.get("/scenarios", response_model=FinancePlanningScenarioResponse)
async def read_finance_planning_scenarios(
    db: AsyncSession = Depends(get_request_transaction),
) -> FinancePlanningScenarioResponse:
    """
    Return planning scenarios, projections, KPI targets, timeline, and AI playbook.
    """
    try:
        # Try to get from database first, fallback to mock data
        from app.services.finance_planning import get_scenarios_from_db
        scenarios_data = await get_scenarios_from_db(db)
        if scenarios_data:
            return scenarios_data
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to query scenarios from database, using mock data: {str(e)}")
    
    return get_scenario_planning_snapshot()


@router.patch("/scenarios/config", response_model=FinancePlanningScenarioResponse)
async def update_planning_config(
    config_data: FinancePlanningConfigUpdate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: AuthUserResponse = Depends(get_current_user),
) -> FinancePlanningScenarioResponse:
    """
    Update planning configuration (base year, planning period, etc.).
    """
    try:
        await save_planning_config(db, config_data, current_user.id)
        # Return updated data from database, fallback to mock if not found
        from app.services.finance_planning import get_scenarios_from_db
        scenarios_data = await get_scenarios_from_db(db)
        if scenarios_data:
            return scenarios_data
        return get_scenario_planning_snapshot()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update planning config: {str(e)}"
        )


@router.patch("/scenarios/{scenario_key}", response_model=FinancePlanningScenarioResponse)
async def update_scenario_data(
    scenario_key: str,
    scenario_data: FinanceScenarioUpdate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: AuthUserResponse = Depends(get_current_user),
) -> FinancePlanningScenarioResponse:
    """
    Update a specific scenario (e.g., activate it, update parameters).
    """
    try:
        await update_scenario(db, scenario_key, scenario_data, current_user.id)
        # Return updated data from database, fallback to mock if not found
        from app.services.finance_planning import get_scenarios_from_db
        scenarios_data = await get_scenarios_from_db(db)
        if scenarios_data:
            return scenarios_data
        return get_scenario_planning_snapshot()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update scenario: {str(e)}"
        )


@router.post("/forecasts/generate", response_model=ForecastResponse)
async def generate_forecast(
    forecast_params: ForecastCreate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: AuthUserResponse = Depends(get_current_user),
) -> ForecastResponse:
    """
    Generate a financial forecast using AI.
    """
    try:
        from app.services.forecast_service import forecast_service
        import logging
        logger = logging.getLogger(__name__)
        
        # Get historical data
        historical_data = await forecast_service._get_historical_data(db, months=12)
        logger.info(f"Fetched {len(historical_data)} months of historical data")
        
        # Generate forecast using AI (this may take time)
        logger.info("Starting AI forecast generation...")
        forecast_items, ai_confidence, ai_insights = await forecast_service.generate_ai_forecast(
            historical_data,
            forecast_params
        )
        logger.info(f"Forecast generated: {len(forecast_items)} periods")
        
        # Save forecast
        forecast = await forecast_service.save_forecast(
            db=db,
            forecast_params=forecast_params,
            forecast_data=forecast_items,
            historical_data=historical_data,
            ai_confidence=ai_confidence,
            ai_insights=ai_insights,
            user_id=current_user.id,
            org_id=getattr(current_user, 'org_id', None)
        )
        
        # Flush to get the ID without committing (middleware will commit)
        await db.flush()
        
        # Convert to response
        return ForecastResponse(
            id=forecast.id,
            forecast_name=forecast.forecast_name,
            forecasting_model=forecast.forecasting_model,
            forecast_period_months=forecast.forecast_period_months,
            market_growth_rate=forecast.market_growth_rate,
            inflation_rate=forecast.inflation_rate,
            seasonal_adjustment=forecast.seasonal_adjustment,
            forecast_data=forecast_items,
            historical_data=[
                ForecastPeriodItem(
                    period=item.get("period", ""),
                    revenue=item.get("revenue", 0.0),
                    expenses=item.get("expenses", 0.0),
                    profit=item.get("profit", 0.0),
                    margin=item.get("margin", 0.0)
                ) if isinstance(item, dict) else item
                for item in (historical_data or [])
            ] if historical_data else None,
            ai_confidence_score=ai_confidence,
            ai_insights=ai_insights,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
    except Exception as e:
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        logger.error(f"Error generating forecast: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate forecast: {str(e)}"
        )


@router.get("/forecasts", response_model=ForecastListResponse)
async def list_forecasts(
    db: AsyncSession = Depends(get_request_transaction),
    current_user: AuthUserResponse = Depends(get_current_user),
    limit: int = 50,
) -> ForecastListResponse:
    """
    List saved forecasts.
    """
    try:
        import logging
        logger = logging.getLogger(__name__)
        from app.services.forecast_service import forecast_service
        
        org_id = getattr(current_user, 'org_id', None)
        logger.info(f"Listing forecasts for org_id: {org_id}, limit: {limit}")
        forecasts = await forecast_service.list_forecasts(db, org_id=org_id, limit=limit)
        logger.info(f"Found {len(forecasts)} forecasts")
        
        forecast_responses = []
        for forecast in forecasts:
            # Safely convert forecast_data and historical_data
            # JSONB fields might need explicit conversion
            import json
            forecast_data_items = []
            if forecast.forecast_data:
                try:
                    # Handle JSONB - might be string, dict, or list
                    forecast_data_raw = forecast.forecast_data
                    if isinstance(forecast_data_raw, str):
                        forecast_data_raw = json.loads(forecast_data_raw)
                    
                    if isinstance(forecast_data_raw, list):
                        for item in forecast_data_raw:
                            if isinstance(item, dict):
                                try:
                                    forecast_data_items.append(ForecastPeriodItem(**item))
                                except Exception as e:
                                    logger.warning(f"Failed to parse forecast_data item: {item}, error: {e}")
                                    # Skip invalid items
                            elif isinstance(item, ForecastPeriodItem):
                                forecast_data_items.append(item)
                    elif isinstance(forecast_data_raw, dict):
                        try:
                            forecast_data_items.append(ForecastPeriodItem(**forecast_data_raw))
                        except Exception as e:
                            logger.warning(f"Failed to parse forecast_data dict: {forecast_data_raw}, error: {e}")
                except Exception as e:
                    logger.error(f"Error processing forecast_data for forecast {forecast.id}: {e}", exc_info=True)
            
            historical_data_items = []
            if forecast.historical_data:
                try:
                    # Handle JSONB - might be string, dict, or list
                    historical_data_raw = forecast.historical_data
                    if isinstance(historical_data_raw, str):
                        historical_data_raw = json.loads(historical_data_raw)
                    
                    if isinstance(historical_data_raw, list):
                        for item in historical_data_raw:
                            if isinstance(item, dict):
                                try:
                                    # Historical data might have different structure, try to convert
                                    historical_data_items.append(ForecastPeriodItem(**item))
                                except Exception as e:
                                    logger.warning(f"Failed to parse historical_data item: {item}, error: {e}")
                                    # Skip invalid items
                            elif isinstance(item, ForecastPeriodItem):
                                historical_data_items.append(item)
                    elif isinstance(historical_data_raw, dict):
                        try:
                            historical_data_items.append(ForecastPeriodItem(**historical_data_raw))
                        except Exception as e:
                            logger.warning(f"Failed to parse historical_data dict: {historical_data_raw}, error: {e}")
                except Exception as e:
                    logger.error(f"Error processing historical_data for forecast {forecast.id}: {e}", exc_info=True)
            
            try:
                forecast_responses.append(ForecastResponse(
                    id=forecast.id,
                    forecast_name=forecast.forecast_name,
                    forecasting_model=forecast.forecasting_model,
                    forecast_period_months=forecast.forecast_period_months,
                    market_growth_rate=forecast.market_growth_rate,
                    inflation_rate=forecast.inflation_rate,
                    seasonal_adjustment=forecast.seasonal_adjustment,
                    forecast_data=forecast_data_items,
                    historical_data=historical_data_items if historical_data_items else None,
                    ai_confidence_score=forecast.ai_confidence_score,
                    ai_insights=forecast.ai_insights,
                    created_at=forecast.created_at,
                    updated_at=forecast.updated_at,
                ))
            except Exception as e:
                logger.error(f"Failed to create ForecastResponse for forecast {forecast.id}: {e}")
                # Skip this forecast if it can't be converted
                continue
        
        return ForecastListResponse(forecasts=forecast_responses, total=len(forecast_responses))
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error listing forecasts: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list forecasts: {str(e)}"
        )


@router.get("/forecasts/{forecast_id}", response_model=ForecastResponse)
async def get_forecast(
    forecast_id: int,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: AuthUserResponse = Depends(get_current_user),
) -> ForecastResponse:
    """
    Get a specific forecast by ID.
    """
    try:
        from app.services.forecast_service import forecast_service
        
        forecast = await forecast_service.get_forecast(db, forecast_id)
        if not forecast:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Forecast {forecast_id} not found"
            )
        
        return ForecastResponse(
            id=forecast.id,
            forecast_name=forecast.forecast_name,
            forecasting_model=forecast.forecasting_model,
            forecast_period_months=forecast.forecast_period_months,
            market_growth_rate=forecast.market_growth_rate,
            inflation_rate=forecast.inflation_rate,
            seasonal_adjustment=forecast.seasonal_adjustment,
            forecast_data=[ForecastPeriodItem(**item) for item in forecast.forecast_data],
            historical_data=[ForecastPeriodItem(**item) for item in (forecast.historical_data or [])],
            ai_confidence_score=forecast.ai_confidence_score,
            ai_insights=forecast.ai_insights,
            created_at=forecast.created_at,
            updated_at=forecast.updated_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get forecast: {str(e)}"
        )


@router.get("/forecasts/{forecast_id}/export")
async def export_forecast(
    forecast_id: int,
    format: str = "csv",  # csv, excel, json
    db: AsyncSession = Depends(get_request_transaction),
    current_user: AuthUserResponse = Depends(get_current_user),
):
    """
    Export forecast data in various formats.
    """
    try:
        from app.services.forecast_service import forecast_service
        from fastapi.responses import Response
        import csv
        import io
        
        forecast = await forecast_service.get_forecast(db, forecast_id)
        if not forecast:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Forecast {forecast_id} not found"
            )
        
        if format == "csv":
            # Generate CSV
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Header
            writer.writerow(["Period", "Revenue Forecast", "Expense Forecast", "Profit Forecast", "Margin (%)"])
            
            # Data rows
            for item in forecast.forecast_data:
                writer.writerow([
                    item["period"],
                    f"{item['revenue']:.2f}",
                    f"{item['expenses']:.2f}",
                    f"{item['profit']:.2f}",
                    f"{item['margin']:.2f}"
                ])
            
            csv_content = output.getvalue()
            output.close()
            
            return Response(
                content=csv_content,
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename=forecast_{forecast_id}_{datetime.now().strftime('%Y%m%d')}.csv"
                }
            )
        
        elif format == "json":
            import json
            return Response(
                content=json.dumps({
                    "forecast_id": forecast.id,
                    "forecast_name": forecast.forecast_name,
                    "forecasting_model": forecast.forecasting_model,
                    "generated_at": forecast.created_at.isoformat(),
                    "data": forecast.forecast_data
                }, indent=2),
                media_type="application/json",
                headers={
                    "Content-Disposition": f"attachment; filename=forecast_{forecast_id}_{datetime.now().strftime('%Y%m%d')}.json"
                }
            )
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported format: {format}. Supported formats: csv, json"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export forecast: {str(e)}"
        )

