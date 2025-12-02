"""
Opportunity Scheduler Service
Handles automated scheduling and execution of opportunity source scrapes and AI agent runs.
"""
import uuid
import hashlib
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.opportunity_source import (
    OpportunitySource,
    OpportunityScrapeHistory,
    OpportunityTemp,
    OpportunityAgent,
    OpportunityAgentRun,
    OpportunitySourceFrequency,
    OpportunitySourceStatus,
    ScrapeJobStatus,
    TempOpportunityStatus,
    AgentFrequency,
    AgentStatus,
    AgentRunStatus,
)
from app.services.opportunity_ingestion import OpportunityIngestionService
from app.utils.scraper import process_urls, scrape_text_with_bs4
from app.utils.logger import get_logger

logger = get_logger("opportunity_scheduler")


def generate_url_hash(url: str) -> str:
    """Generate SHA256 hash for URL deduplication."""
    return hashlib.sha256(url.encode('utf-8')).hexdigest()


def calculate_next_run_time(frequency: OpportunitySourceFrequency, last_run: Optional[datetime] = None) -> datetime:
    """Calculate next run time based on frequency."""
    now = datetime.utcnow()
    if not last_run:
        return now
    
    if frequency == OpportunitySourceFrequency.daily:
        return last_run + timedelta(days=1)
    elif frequency == OpportunitySourceFrequency.weekly:
        return last_run + timedelta(weeks=1)
    elif frequency == OpportunitySourceFrequency.monthly:
        return last_run + timedelta(days=30)
    else:  # manual
        return now + timedelta(days=365)  # Far future


def calculate_agent_next_run_time(frequency: AgentFrequency, last_run: Optional[datetime] = None) -> datetime:
    """Calculate next run time for AI agent based on frequency."""
    now = datetime.utcnow()
    if not last_run:
        return now
    
    if frequency == AgentFrequency.twelve_hours:
        return last_run + timedelta(hours=12)
    elif frequency == AgentFrequency.one_day:
        return last_run + timedelta(days=1)
    elif frequency == AgentFrequency.three_days:
        return last_run + timedelta(days=3)
    elif frequency == AgentFrequency.seven_days:
        return last_run + timedelta(days=7)
    else:
        return now + timedelta(days=365)


class OpportunitySchedulerService:
    """Service for scheduling and executing opportunity source scrapes and AI agent runs."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.ingestion_service = OpportunityIngestionService(db)
    
    async def get_sources_due_for_scraping(self) -> List[OpportunitySource]:
        """Get all active sources that are due for scraping."""
        now = datetime.utcnow()
        stmt = select(OpportunitySource).where(
            and_(
                OpportunitySource.status == OpportunitySourceStatus.active,
                OpportunitySource.is_auto_discovery_enabled == True,
                or_(
                    OpportunitySource.next_run_at.is_(None),
                    OpportunitySource.next_run_at <= now
                )
            )
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_agents_due_for_execution(self) -> List[OpportunityAgent]:
        """Get all active agents that are due for execution."""
        now = datetime.utcnow()
        stmt = select(OpportunityAgent).where(
            and_(
                OpportunityAgent.status == AgentStatus.active,
                or_(
                    OpportunityAgent.next_run_at.is_(None),
                    OpportunityAgent.next_run_at <= now
                )
            )
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def is_url_already_scraped(self, url: str, org_id: uuid.UUID) -> bool:
        """Check if URL has already been scraped (deduplication)."""
        url_hash = generate_url_hash(url)
        stmt = select(OpportunityScrapeHistory).where(
            and_(
                OpportunityScrapeHistory.org_id == org_id,
                OpportunityScrapeHistory.url_hash == url_hash
            )
        ).limit(1)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    async def create_scrape_history_record(
        self,
        source: OpportunitySource,
        url: str,
        status: ScrapeJobStatus = ScrapeJobStatus.queued,
        error_message: Optional[str] = None
    ) -> OpportunityScrapeHistory:
        """Create a scrape history record."""
        url_hash = generate_url_hash(url)
        history = OpportunityScrapeHistory(
            id=uuid.uuid4(),
            org_id=source.org_id,
            source_id=source.id,
            url=url,
            url_hash=url_hash,
            status=status,
            error_message=error_message,
            scraped_at=datetime.utcnow()
        )
        self.db.add(history)
        await self.db.flush()
        return history
    
    async def scrape_source(self, source: OpportunitySource) -> Dict[str, Any]:
        """Scrape a single opportunity source and create temp opportunities."""
        logger.info(f"Starting scrape for source: {source.name} ({source.url})")
        
        results = {
            "source_id": str(source.id),
            "source_name": source.name,
            "urls_scraped": 0,
            "opportunities_found": 0,
            "opportunities_created": 0,
            "errors": []
        }
        
        try:
            # Check if base URL already scraped (skip if recently done)
            if await self.is_url_already_scraped(source.url, source.org_id):
                logger.info(f"Source {source.name} already scraped, skipping")
                results["errors"].append("URL already scraped (deduplication)")
                return results
            
            # Create scrape history record
            history = await self.create_scrape_history_record(
                source,
                source.url,
                ScrapeJobStatus.running
            )
            
            # Scrape the source URL
            scrape_results = await process_urls([source.url])
            
            if not scrape_results or "error" in scrape_results[0]:
                error_msg = scrape_results[0].get("error", "Unknown error") if scrape_results else "No results"
                history.status = ScrapeJobStatus.error
                history.error_message = error_msg
                history.completed_at = datetime.utcnow()
                results["errors"].append(error_msg)
                await self.db.flush()
                return results
            
            result = scrape_results[0]
            opportunities = result.get("opportunities", [])
            results["urls_scraped"] = 1
            results["opportunities_found"] = len(opportunities)
            
            # Create temp opportunities for each found opportunity
            for opp_data in opportunities:
                try:
                    # Check if detail URL already scraped
                    detail_url = opp_data.get("detail_url") or opp_data.get("source_url")
                    if detail_url and await self.is_url_already_scraped(detail_url, source.org_id):
                        logger.info(f"Skipping duplicate opportunity: {detail_url}")
                        continue
                    
                    # Create temp opportunity
                    temp_opp_data = {
                        "source_id": source.id,
                        "history_id": history.id,
                        "project_title": opp_data.get("title") or opp_data.get("project_title") or "Untitled Opportunity",
                        "client_name": opp_data.get("client") or opp_data.get("client_name"),
                        "location": opp_data.get("location") or opp_data.get("location_details", {}).get("city"),
                        "budget_text": opp_data.get("budget_text") or opp_data.get("project_value_text"),
                        "deadline": self.ingestion_service._parse_datetime(opp_data.get("deadline")),
                        "documents": opp_data.get("documents", []),
                        "tags": opp_data.get("tags", []),
                        "ai_summary": opp_data.get("overview") or opp_data.get("description"),
                        "ai_metadata": {"opportunity": opp_data},
                        "raw_payload": opp_data,
                        "match_score": None,
                        "risk_score": None,
                        "strategic_fit_score": None,
                    }
                    
                    temp_opp = await self.ingestion_service.create_temp_opportunity(
                        source.org_id,
                        OpportunityTempCreate(**temp_opp_data)
                    )
                    results["opportunities_created"] += 1
                    
                    # Create scrape history for detail URL if exists
                    if detail_url:
                        await self.create_scrape_history_record(
                            source,
                            detail_url,
                            ScrapeJobStatus.success
                        )
                    
                except Exception as e:
                    logger.error(f"Error creating temp opportunity: {e}")
                    results["errors"].append(f"Error creating opportunity: {str(e)}")
            
            # Update history record
            history.status = ScrapeJobStatus.success
            history.extracted_data = {"opportunities_count": len(opportunities)}
            history.completed_at = datetime.utcnow()
            
            # Update source timestamps
            source.last_run_at = datetime.utcnow()
            source.last_success_at = datetime.utcnow()
            source.next_run_at = calculate_next_run_time(source.frequency, source.last_run_at)
            
            await self.db.flush()
            logger.info(f"Completed scrape for {source.name}: {results['opportunities_created']} opportunities created")
            
        except Exception as e:
            logger.error(f"Error scraping source {source.name}: {e}")
            results["errors"].append(f"Scraping error: {str(e)}")
            source.last_run_at = datetime.utcnow()
            source.next_run_at = calculate_next_run_time(source.frequency, source.last_run_at)
            await self.db.flush()
        
        return results
    
    async def execute_agent(self, agent: OpportunityAgent) -> Dict[str, Any]:
        """Execute an AI agent to discover opportunities."""
        logger.info(f"Executing agent: {agent.name} ({agent.base_url})")
        
        results = {
            "agent_id": str(agent.id),
            "agent_name": agent.name,
            "opportunities_found": 0,
            "opportunities_created": 0,
            "errors": []
        }
        
        # Create agent run record
        agent_run = OpportunityAgentRun(
            id=uuid.uuid4(),
            agent_id=agent.id,
            org_id=agent.org_id,
            status=AgentRunStatus.running,
            started_at=datetime.utcnow(),
            new_opportunities=0
        )
        self.db.add(agent_run)
        await self.db.flush()
        
        try:
            # Scrape the base URL
            scrape_results = await process_urls([agent.base_url])
            
            if not scrape_results or "error" in scrape_results[0]:
                error_msg = scrape_results[0].get("error", "Unknown error") if scrape_results else "No results"
                agent_run.status = AgentRunStatus.failed
                agent_run.error_message = error_msg
                agent_run.finished_at = datetime.utcnow()
                results["errors"].append(error_msg)
                await self.db.flush()
                return results
            
            result = scrape_results[0]
            opportunities = result.get("opportunities", [])
            results["opportunities_found"] = len(opportunities)
            
            # Create temp opportunities for each found opportunity
            for opp_data in opportunities:
                try:
                    # Check if detail URL already scraped
                    detail_url = opp_data.get("detail_url") or opp_data.get("source_url")
                    if detail_url and await self.is_url_already_scraped(detail_url, agent.org_id):
                        logger.info(f"Skipping duplicate opportunity: {detail_url}")
                        continue
                    
                    # Create temp opportunity
                    temp_opp_data = {
                        "source_id": agent.source_id,
                        "project_title": opp_data.get("title") or opp_data.get("project_title") or "Untitled Opportunity",
                        "client_name": opp_data.get("client") or opp_data.get("client_name"),
                        "location": opp_data.get("location") or opp_data.get("location_details", {}).get("city"),
                        "budget_text": opp_data.get("budget_text") or opp_data.get("project_value_text"),
                        "deadline": self.ingestion_service._parse_datetime(opp_data.get("deadline")),
                        "documents": opp_data.get("documents", []),
                        "tags": opp_data.get("tags", []),
                        "ai_summary": opp_data.get("overview") or opp_data.get("description"),
                        "ai_metadata": {
                            "opportunity": opp_data,
                            "agent_prompt": agent.prompt,
                            "agent_name": agent.name
                        },
                        "raw_payload": opp_data,
                        "match_score": None,
                        "risk_score": None,
                        "strategic_fit_score": None,
                    }
                    
                    from app.schemas.opportunity_ingestion import OpportunityTempCreate
                    temp_opp = await self.ingestion_service.create_temp_opportunity(
                        agent.org_id,
                        OpportunityTempCreate(**temp_opp_data)
                    )
                    results["opportunities_created"] += 1
                    
                except Exception as e:
                    logger.error(f"Error creating temp opportunity from agent: {e}")
                    results["errors"].append(f"Error creating opportunity: {str(e)}")
            
            # Update agent run
            agent_run.status = AgentRunStatus.succeeded
            agent_run.new_opportunities = results["opportunities_created"]
            agent_run.finished_at = datetime.utcnow()
            agent_run.metadata_payload = {"opportunities_found": len(opportunities)}
            
            # Update agent timestamps
            agent.last_run_at = datetime.utcnow()
            agent.next_run_at = calculate_agent_next_run_time(agent.frequency, agent.last_run_at)
            
            await self.db.flush()
            logger.info(f"Completed agent execution {agent.name}: {results['opportunities_created']} opportunities created")
            
        except Exception as e:
            logger.error(f"Error executing agent {agent.name}: {e}")
            results["errors"].append(f"Agent execution error: {str(e)}")
            agent_run.status = AgentRunStatus.failed
            agent_run.error_message = str(e)
            agent_run.finished_at = datetime.utcnow()
            agent.last_run_at = datetime.utcnow()
            agent.next_run_at = calculate_agent_next_run_time(agent.frequency, agent.last_run_at)
            await self.db.flush()
        
        return results
    
    async def run_scheduled_scrapes(self) -> Dict[str, Any]:
        """Run all scheduled source scrapes."""
        logger.info("Running scheduled opportunity source scrapes")
        sources = await self.get_sources_due_for_scraping()
        
        results = {
            "sources_processed": 0,
            "total_opportunities_created": 0,
            "errors": []
        }
        
        for source in sources:
            try:
                scrape_result = await self.scrape_source(source)
                results["sources_processed"] += 1
                results["total_opportunities_created"] += scrape_result["opportunities_created"]
                if scrape_result["errors"]:
                    results["errors"].extend(scrape_result["errors"])
            except Exception as e:
                logger.error(f"Error processing source {source.name}: {e}")
                results["errors"].append(f"Source {source.name}: {str(e)}")
        
        logger.info(f"Scheduled scrapes completed: {results['sources_processed']} sources, {results['total_opportunities_created']} opportunities")
        return results
    
    async def run_scheduled_agents(self) -> Dict[str, Any]:
        """Run all scheduled AI agents."""
        logger.info("Running scheduled AI agents")
        agents = await self.get_agents_due_for_execution()
        
        results = {
            "agents_processed": 0,
            "total_opportunities_created": 0,
            "errors": []
        }
        
        for agent in agents:
            try:
                agent_result = await self.execute_agent(agent)
                results["agents_processed"] += 1
                results["total_opportunities_created"] += agent_result["opportunities_created"]
                if agent_result["errors"]:
                    results["errors"].extend(agent_result["errors"])
            except Exception as e:
                logger.error(f"Error processing agent {agent.name}: {e}")
                results["errors"].append(f"Agent {agent.name}: {str(e)}")
        
        logger.info(f"Scheduled agents completed: {results['agents_processed']} agents, {results['total_opportunities_created']} opportunities")
        return results

