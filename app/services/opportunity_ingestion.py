import uuid
import re
import mimetypes
from datetime import datetime, timedelta
from typing import List, Optional, Sequence, Any, Dict

from sqlalchemy import select, desc, delete, func
from sqlalchemy.exc import IntegrityError
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
)
from app.models.opportunity import OpportunityStage, RiskLevel
from app.models.user import User
from app.schemas.opportunity_ingestion import (
    OpportunitySourceCreate,
    OpportunitySourceUpdate,
    OpportunitySourceResponse,
    ScrapeHistoryResponse,
    OpportunityTempCreate,
    OpportunityTempResponse,
    OpportunityTempUpdate,
    OpportunityAgentCreate,
    OpportunityAgentUpdate,
    OpportunityAgentResponse,
    OpportunityAgentRunResponse,
)
from app.schemas.opportunity import OpportunityCreate, OpportunityResponse
from app.services.opportunity import OpportunityService
from app.services.opportunity_tabs import OpportunityTabsService
from app.schemas.opportunity_tabs import OpportunityOverviewUpdate
from app.services.opportunity_document import OpportunityDocumentService
from app.schemas.opportunity_document import OpportunityDocumentCreate
from app.utils.scraper import process_urls
from app.utils.logger import get_logger

logger = get_logger("opportunity_ingestion_service")


class OpportunityIngestionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def _coerce_numeric(value: Any) -> Optional[float]:
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            cleaned = (
                value.replace(",", "")
                .replace("$", "")
                .replace("USD", "")
                .strip()
            )
            if not cleaned:
                return None
            try:
                return float(cleaned)
            except ValueError:
                return None
        return None

    @staticmethod
    def _derive_risk_level(
        risk_score: Optional[int],
        tags: Optional[List[str]],
    ) -> Optional[RiskLevel]:
        if risk_score is not None:
            if risk_score >= 70:
                return RiskLevel.high_risk
            if risk_score >= 40:
                return RiskLevel.medium_risk
            return RiskLevel.low_risk

        if tags:
            lowered = [tag.lower() for tag in tags]
            if any("high" in tag for tag in lowered):
                return RiskLevel.high_risk
            if any("medium" in tag for tag in lowered):
                return RiskLevel.medium_risk
            if any("low" in tag for tag in lowered):
                return RiskLevel.low_risk
        return None

    @staticmethod
    def _parse_datetime(value: Any) -> Optional[datetime]:
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            sanitized = value.strip()
            if not sanitized:
                return None
            try:
                # Support trailing Z / timezone offsets
                if sanitized.endswith("Z"):
                    sanitized = sanitized[:-1] + "+00:00"
                return datetime.fromisoformat(sanitized)
            except ValueError:
                return None
        return None

    @staticmethod
    def _extract_state_from_location(location: Optional[str]) -> Optional[str]:
        if not location or not isinstance(location, str):
            return None

        # Prefer last comma-separated token, otherwise fall back to trimmed string
        tokens = [token.strip() for token in re.split(r"[,|/|\n|-]", location) if token.strip()]
        if not tokens:
            candidate = location.strip()
        else:
            candidate = tokens[-1]

        if not candidate:
            return None
        return candidate[:100]

    @staticmethod
    def _normalize_scope_items(*sources: Any) -> List[str]:
        items: List[str] = []
        for source in sources:
            if not source:
                continue
            if isinstance(source, list):
                for entry in source:
                    if not entry:
                        continue
                    text = str(entry).strip()
                    if text and text not in items:
                        items.append(text)
            elif isinstance(source, str):
                segments = [
                    segment.strip()
                    for segment in re.split(r"[\n•\-]", source)
                    if segment.strip()
                ]
                for segment in segments:
                    if segment and segment not in items:
                        items.append(segment)
        return items[:20]

    @staticmethod
    def _guess_mime_type(url: Optional[str]) -> str:
        if not url:
            return "application/octet-stream"
        mime, _ = mimetypes.guess_type(url)
        return mime or "application/octet-stream"

    def _extract_document_sources(
        self,
        record: OpportunityTemp,
        raw_payload: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        documents: List[Dict[str, Any]] = []

        metadata_opportunity = None
        if isinstance(record.ai_metadata, dict):
            metadata_opportunity = record.ai_metadata.get("opportunity")
        structured_docs = []
        if isinstance(metadata_opportunity, dict):
            structured_docs = metadata_opportunity.get("documents") or []
        if not structured_docs:
            structured_docs = raw_payload.get("documents") or []

        def append_entries(doc_list: Any) -> None:
            if not doc_list:
                return
            for entry in doc_list:
                if isinstance(entry, dict):
                    title = (
                        entry.get("title")
                        or entry.get("name")
                        or entry.get("label")
                        or entry.get("url")
                        or "Supporting document"
                    )
                    documents.append(
                        {
                            "title": title[:255],
                            "url": entry.get("url") or entry.get("link"),
                            "type": entry.get("type") or entry.get("format"),
                            "category": entry.get("category") or entry.get("type") or "Scraped Document",
                            "description": entry.get("description"),
                            "size": entry.get("size"),
                        }
                    )
                elif isinstance(entry, str):
                    documents.append(
                        {
                            "title": entry[:255],
                            "url": entry if entry.startswith("http") else None,
                            "type": None,
                            "category": "Scraped Document",
                            "description": None,
                            "size": None,
                        }
                    )

        append_entries(structured_docs)

        if not documents and isinstance(record.documents, list):
            append_entries(record.documents)

        return documents

    async def _seed_overview_from_ingestion(
        self,
        opportunity_id: uuid.UUID,
        user: User,
        record: OpportunityTemp,
        raw_payload: Dict[str, Any],
        description: Optional[str],
        project_value: Optional[float],
        expected_rfp_date: Optional[datetime],
        deadline: Optional[datetime],
        market_sector: Optional[str],
    ) -> None:
        scope_items = self._normalize_scope_items(
            raw_payload.get("scope_items"),
            raw_payload.get("scopeItems"),
            raw_payload.get("scope_summary"),
            (
                record.ai_metadata.get("opportunity", {}).get("scope_items")
                if isinstance(record.ai_metadata, dict)
                else None
            ),
        )

        documents = self._extract_document_sources(record, raw_payload)
        source_url = (
            raw_payload.get("source_url")
            or raw_payload.get("detail_url")
            or raw_payload.get("company_website")
            or raw_payload.get("companyWebsite")
            or raw_payload.get("company_url")
            or raw_payload.get("url")
        )

        key_metrics = {
            "project_value": project_value,
            "win_probability": raw_payload.get("win_probability"),
            "expected_rfp_date": expected_rfp_date.isoformat() if expected_rfp_date else None,
            "deadline": deadline.isoformat() if deadline else None,
            "current_stage": OpportunityStage.lead.value,
            "location": record.location,
            "market_sector": market_sector,
            "ai_match_score": record.match_score,
            "documents_total": len(documents),
            "source_url": source_url,
        }

        # Remove empty values
        key_metrics = {k: v for k, v in key_metrics.items() if v not in (None, "", [])}

        documents_summary = None
        if documents:
            documents_summary = {
                "total_uploaded": len(documents),
                "available_for_proposal": 0,
                "sources": [
                    {"title": doc.get("title"), "url": doc.get("url")}
                    for doc in documents[:10]
                ],
            }

        overview_service = OpportunityTabsService(self.db)
        await overview_service.update_overview(
            opportunity_id,
            OpportunityOverviewUpdate(
                project_description=description,
                project_scope=scope_items or None,
                key_metrics=key_metrics or None,
                documents_summary=documents_summary,
            ),
        )

    async def _import_documents_from_ingestion(
        self,
        opportunity_id: uuid.UUID,
        user: User,
        record: OpportunityTemp,
        raw_payload: Dict[str, Any],
    ) -> None:
        documents = self._extract_document_sources(record, raw_payload)
        if not documents:
            return

        doc_service = OpportunityDocumentService(self.db)
        for doc in documents:
            title = doc.get("title") or "Supporting document"
            try:
                document_payload = OpportunityDocumentCreate(
                    file_name=title[:255],
                    original_name=title[:255],
                    file_type=doc.get("type") or self._guess_mime_type(doc.get("url")),
                    file_size=max(int(doc.get("size") or 1), 1),
                    category=doc.get("category") or "Scraped Document",
                    purpose="Reference",
                    description=doc.get("description") or "Imported from ingestion source",
                    tags=None,
                    status="external",
                    is_available_for_proposal=False,
                    file_url=doc.get("url"),
                )
                await doc_service.create_document(opportunity_id, document_payload, user)
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.warning(
                    "Failed to import document '%s' for opportunity %s: %s",
                    title,
                    opportunity_id,
                    exc,
                )

    async def list_sources(self, org_id: uuid.UUID) -> List[OpportunitySourceResponse]:
        stmt = (
            select(OpportunitySource)
            .where(OpportunitySource.org_id == org_id)
            .order_by(desc(OpportunitySource.updated_at))
        )
        result = await self.db.execute(stmt)
        records: Sequence[OpportunitySource] = result.scalars().all()
        return [OpportunitySourceResponse.model_validate(record) for record in records]

    async def create_source(
        self,
        org_id: uuid.UUID,
        user_id: uuid.UUID,
        data: OpportunitySourceCreate,
    ) -> OpportunitySourceResponse:
        source = OpportunitySource(
            id=uuid.uuid4(),
            org_id=org_id,
            created_by=user_id,
            name=data.name.strip(),
            url=str(data.url),
            category=data.category.strip() if data.category else None,
            frequency=OpportunitySourceFrequency(data.frequency.value),
            status=OpportunitySourceStatus(data.status.value),
            tags=data.tags,
            notes=data.notes.strip() if data.notes else None,
            is_auto_discovery_enabled=data.is_auto_discovery_enabled,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.db.add(source)
        try:
            await self.db.flush()
        except IntegrityError as exc:
            await self.db.rollback()
            raise exc
        await self.db.refresh(source)
        return OpportunitySourceResponse.model_validate(source)

    async def update_source(
        self,
        source_id: uuid.UUID,
        org_id: uuid.UUID,
        data: OpportunitySourceUpdate,
    ) -> Optional[OpportunitySourceResponse]:
        stmt = (
            select(OpportunitySource)
            .where(
                OpportunitySource.id == source_id,
                OpportunitySource.org_id == org_id,
            )
        )
        result = await self.db.execute(stmt)
        source: Optional[OpportunitySource] = result.scalar_one_or_none()
        if not source:
            return None

        if data.name is not None:
            source.name = data.name.strip()
        if data.url is not None:
            source.url = str(data.url)
        if data.category is not None:
            source.category = data.category.strip() if data.category else None
        if data.frequency is not None:
            source.frequency = OpportunitySourceFrequency(data.frequency.value)
        if data.status is not None:
            source.status = OpportunitySourceStatus(data.status.value)
        if data.tags is not None:
            source.tags = data.tags
        if data.notes is not None:
            source.notes = data.notes.strip() if data.notes else None
        if data.is_auto_discovery_enabled is not None:
            source.is_auto_discovery_enabled = data.is_auto_discovery_enabled

        source.updated_at = datetime.utcnow()

        await self.db.flush()
        await self.db.refresh(source)
        return OpportunitySourceResponse.model_validate(source)

    async def delete_source(self, source_id: uuid.UUID, org_id: uuid.UUID) -> bool:
        stmt = (
            select(OpportunitySource.id)
            .where(
                OpportunitySource.id == source_id,
                OpportunitySource.org_id == org_id,
            )
        )
        result = await self.db.execute(stmt)
        exists = result.scalar_one_or_none()
        if not exists:
            return False
        await self.db.execute(
            delete(OpportunitySource).where(
                OpportunitySource.id == source_id,
                OpportunitySource.org_id == org_id,
            )
        )
        await self.db.flush()
        return True

    async def list_scrape_history(
        self,
        org_id: uuid.UUID,
        source_id: Optional[uuid.UUID] = None,
        limit: int = 100,
    ) -> List[ScrapeHistoryResponse]:
        stmt = (
            select(OpportunityScrapeHistory)
            .where(OpportunityScrapeHistory.org_id == org_id)
            .order_by(desc(OpportunityScrapeHistory.scraped_at))
            .limit(limit)
        )
        if source_id:
            stmt = stmt.where(OpportunityScrapeHistory.source_id == source_id)
        result = await self.db.execute(stmt)
        records = result.scalars().all()
        return [ScrapeHistoryResponse.model_validate(record) for record in records]

    async def list_temp_opportunities(
        self,
        org_id: uuid.UUID,
        status: Optional[TempOpportunityStatus] = None,
        limit: int = 100,
    ) -> List[OpportunityTempResponse]:
        stmt = (
            select(OpportunityTemp)
            .where(OpportunityTemp.org_id == org_id)
            .order_by(desc(OpportunityTemp.created_at))
            .limit(limit)
        )
        if status:
            stmt = stmt.where(OpportunityTemp.status == status)
        result = await self.db.execute(stmt)
        records = result.scalars().all()
        return [OpportunityTempResponse.model_validate(record) for record in records]

    async def create_temp_opportunity(
        self,
        org_id: uuid.UUID,
        data: OpportunityTempCreate,
    ) -> OpportunityTempResponse:
        temp_identifier = await self.next_available_identifier(org_id)
        record = OpportunityTemp(
            id=uuid.uuid4(),
            org_id=org_id,
            source_id=data.source_id,
            history_id=data.history_id,
            reviewer_id=None,
            temp_identifier=temp_identifier,
            project_title=data.project_title.strip(),
            client_name=data.client_name.strip() if data.client_name else None,
            location=data.location.strip() if data.location else None,
            budget_text=data.budget_text.strip() if data.budget_text else None,
            deadline=data.deadline,
            documents=data.documents,
            tags=data.tags,
            ai_summary=data.ai_summary,
            ai_metadata=data.ai_metadata,
            raw_payload=data.raw_payload,
            match_score=data.match_score,
            risk_score=data.risk_score,
            strategic_fit_score=data.strategic_fit_score,
            status=TempOpportunityStatus.pending_review,
            reviewer_notes=data.reviewer_notes,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.db.add(record)
        await self.db.flush()
        await self.db.refresh(record)
        return OpportunityTempResponse.model_validate(record)

    async def promote_temp_opportunity(
        self,
        temp_id: uuid.UUID,
        user: User,
        account_id: Optional[uuid.UUID] = None,
    ) -> Optional[OpportunityResponse]:
        if not user.org_id:
            raise ValueError("User must belong to an organization.")

        stmt = (
            select(OpportunityTemp)
            .where(
                OpportunityTemp.id == temp_id,
                OpportunityTemp.org_id == user.org_id,
            )
        )
        result = await self.db.execute(stmt)
        record: Optional[OpportunityTemp] = result.scalar_one_or_none()
        if not record:
            return None

        raw_payload: dict[str, Any] = record.raw_payload or {}
        project_value = self._coerce_numeric(
            raw_payload.get("project_value_numeric")
            or raw_payload.get("project_value")
            or record.ai_metadata.get("project_value_numeric") if record.ai_metadata else None
        )

        description = (
            raw_payload.get("description")
            or record.ai_summary
            or raw_payload.get("summary")
        )

        location_details = raw_payload.get("location_details") or {}
        manual_location = record.location.strip() if isinstance(record.location, str) else None
        state = manual_location or (
            raw_payload.get("state")
            or location_details.get("state")
            or location_details.get("state_code")
            or self._extract_state_from_location(raw_payload.get("location"))
            or self._extract_state_from_location(record.location)
        )
        if state:
            state = state[:100]

        market_sector = raw_payload.get("market_sector")
        if not market_sector and record.tags:
            market_sector = ", ".join(record.tags)

        risk_level = self._derive_risk_level(record.risk_score, record.tags)

        expected_rfp_date = self._parse_datetime(raw_payload.get("expected_rfp_date"))
        if expected_rfp_date is None:
            expected_rfp_date = self._parse_datetime(record.deadline)

        deadline = self._parse_datetime(record.deadline)
        if expected_rfp_date and not deadline:
            # If we have expected_rfp_date but no deadline, set deadline to 1 day after
            deadline = expected_rfp_date + timedelta(days=1)
        if deadline and expected_rfp_date and deadline <= expected_rfp_date:
            # Ensure deadline is always at least 1 day after expected_rfp_date
            deadline = expected_rfp_date + timedelta(days=1)

        opportunity_payload = OpportunityCreate(
            project_name=record.project_title,
            client_name=record.client_name or "Unknown client",
            account_id=account_id,
            description=description,
            stage=OpportunityStage.lead,
            risk_level=risk_level,
            project_value=project_value,
            currency="USD",
            expected_rfp_date=expected_rfp_date,
            deadline=deadline,
            state=state,
            market_sector=market_sector,
            match_score=record.match_score,
        )

        service = OpportunityService(self.db)
        opportunity = await service.create_opportunity(opportunity_payload, user)

        try:
            await self._seed_overview_from_ingestion(
                opportunity.id,
                user,
                record,
                raw_payload,
                description,
                project_value,
                expected_rfp_date,
                deadline,
                market_sector,
            )
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.warning(
                "Failed to seed overview for opportunity %s: %s", opportunity.id, exc
            )

        try:
            await self._import_documents_from_ingestion(
                opportunity.id,
                user,
                record,
                raw_payload,
            )
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.warning(
                "Failed to import documents for opportunity %s: %s", opportunity.id, exc
            )

        record.status = TempOpportunityStatus.promoted
        record.reviewer_id = user.id
        record.updated_at = datetime.utcnow()
        await self.db.flush()

        return opportunity

    async def update_temp_opportunity(
        self,
        temp_id: uuid.UUID,
        org_id: uuid.UUID,
        reviewer_id: uuid.UUID,
        data: OpportunityTempUpdate,
    ) -> Optional[OpportunityTempResponse]:
        stmt = (
            select(OpportunityTemp)
            .where(
                OpportunityTemp.id == temp_id,
                OpportunityTemp.org_id == org_id,
            )
        )
        result = await self.db.execute(stmt)
        record: Optional[OpportunityTemp] = result.scalar_one_or_none()
        if not record:
            return None

        if data.status is not None:
            record.status = TempOpportunityStatus(data.status.value)
        if data.reviewer_notes is not None:
            record.reviewer_notes = data.reviewer_notes
        if data.match_score is not None:
            record.match_score = data.match_score
        if data.risk_score is not None:
            record.risk_score = data.risk_score
        if data.strategic_fit_score is not None:
            record.strategic_fit_score = data.strategic_fit_score
        if data.location is not None:
            record.location = data.location.strip() if data.location else None
        if data.project_title is not None:
            record.project_title = data.project_title.strip() or record.project_title
        if data.client_name is not None:
            record.client_name = data.client_name.strip() if data.client_name else None
        if data.budget_text is not None:
            record.budget_text = data.budget_text.strip() if data.budget_text else None
        if data.deadline is not None:
            record.deadline = data.deadline
        if data.tags is not None:
            record.tags = data.tags
        if data.ai_summary is not None:
            record.ai_summary = data.ai_summary
        if data.source_url is not None:
            raw_payload = dict(record.raw_payload or {})
            sanitized = data.source_url.strip() if data.source_url else None
            if sanitized:
                raw_payload["source_url"] = sanitized
                raw_payload["company_website"] = sanitized
                raw_payload["companyWebsite"] = sanitized
            else:
                raw_payload.pop("source_url", None)
                raw_payload.pop("company_website", None)
                raw_payload.pop("companyWebsite", None)
            record.raw_payload = raw_payload

        record.reviewer_id = reviewer_id
        record.updated_at = datetime.utcnow()
        await self.db.flush()
        await self.db.refresh(record)
        return OpportunityTempResponse.model_validate(record)

    async def refresh_temp_opportunity(
        self,
        temp_id: uuid.UUID,
        org_id: uuid.UUID,
    ) -> Optional[OpportunityTempResponse]:
        stmt = (
            select(OpportunityTemp)
            .where(
                OpportunityTemp.id == temp_id,
                OpportunityTemp.org_id == org_id,
            )
        )
        result = await self.db.execute(stmt)
        record: Optional[OpportunityTemp] = result.scalar_one_or_none()
        if not record:
            return None

        raw_payload = record.raw_payload or {}
        ai_metadata = record.ai_metadata or {}

        source_url = (
            raw_payload.get("source_url")
            or raw_payload.get("detail_url")
            or ai_metadata.get("sourceUrl")
            or ai_metadata.get("source_url")
        )

        if not source_url:
            raise ValueError("No source URL available for this draft.")

        scrape_results = await process_urls([source_url])
        if not scrape_results:
            raise ValueError("Unable to refresh data from source.")

        scrape_record = scrape_results[0]
        if "error" in scrape_record:
            raise ValueError(scrape_record["error"] or "Scraper returned an error.")

        opportunities = scrape_record.get("opportunities") or []
        if not opportunities:
            raise ValueError("Scraper did not return any opportunities.")

        detail_reference = raw_payload.get("source_url") or raw_payload.get("detail_url")
        candidate = None

        if detail_reference:
            for opportunity in opportunities:
                if opportunity.get("detail_url") == detail_reference:
                    candidate = opportunity
                    break

        if not candidate and record.project_title:
            normalized_title = record.project_title.strip().lower()
            for opportunity in opportunities:
                title = (opportunity.get("title") or "").strip().lower()
                if title and title == normalized_title:
                    candidate = opportunity
                    break

        if not candidate:
            candidate = opportunities[0]

        record.project_title = candidate.get("title") or record.project_title
        record.client_name = candidate.get("client") or record.client_name

        location_details = candidate.get("location_details") or {}
        resolved_location = (
            candidate.get("location")
            or location_details.get("line1")
            or location_details.get("city")
            or record.location
        )
        record.location = resolved_location

        record.budget_text = (
            candidate.get("project_value_text")
            or candidate.get("budget_text")
            or record.budget_text
        )

        if candidate.get("tags"):
            record.tags = candidate.get("tags")

        documents = candidate.get("documents") or []
        if documents:
            record.documents = [
                doc.get("url") or doc.get("title")
                for doc in documents
                if isinstance(doc, dict) and (doc.get("url") or doc.get("title"))
            ]

        record.ai_summary = (
            candidate.get("overview")
            or candidate.get("description")
            or record.ai_summary
        )

        merged_payload = {**raw_payload}
        merged_payload["source_url"] = source_url
        merged_payload["detail_url"] = candidate.get("detail_url") or detail_reference or source_url
        merged_payload["opportunity"] = candidate
        record.raw_payload = merged_payload

        merged_metadata = {**ai_metadata}
        merged_metadata["opportunity"] = candidate
        merged_metadata["last_refreshed_at"] = datetime.utcnow().isoformat()
        record.ai_metadata = merged_metadata
        record.updated_at = datetime.utcnow()

        await self.db.flush()
        await self.db.refresh(record)
        return OpportunityTempResponse.model_validate(record)

    async def list_agents(
        self,
        org_id: uuid.UUID,
    ) -> List[OpportunityAgentResponse]:
        stmt = (
            select(OpportunityAgent)
            .where(OpportunityAgent.org_id == org_id)
            .order_by(desc(OpportunityAgent.updated_at))
        )
        result = await self.db.execute(stmt)
        agents = result.scalars().all()
        return [OpportunityAgentResponse.model_validate(agent) for agent in agents]

    async def create_agent(
        self,
        org_id: uuid.UUID,
        user_id: uuid.UUID,
        data: OpportunityAgentCreate,
    ) -> OpportunityAgentResponse:
        agent = OpportunityAgent(
            id=uuid.uuid4(),
            org_id=org_id,
            created_by=user_id,
            source_id=data.source_id,
            name=data.name.strip(),
            prompt=data.prompt.strip(),
            base_url=str(data.base_url),
            frequency=AgentFrequency(data.frequency.value),
            status=AgentStatus(data.status.value),
            next_run_at=data.next_run_at,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.db.add(agent)
        await self.db.flush()
        await self.db.refresh(agent)
        return OpportunityAgentResponse.model_validate(agent)

    async def update_agent(
        self,
        agent_id: uuid.UUID,
        org_id: uuid.UUID,
        data: OpportunityAgentUpdate,
    ) -> Optional[OpportunityAgentResponse]:
        stmt = (
            select(OpportunityAgent)
            .where(
                OpportunityAgent.id == agent_id,
                OpportunityAgent.org_id == org_id,
            )
        )
        result = await self.db.execute(stmt)
        agent: Optional[OpportunityAgent] = result.scalar_one_or_none()
        if not agent:
            return None

        if data.name is not None:
            agent.name = data.name.strip()
        if data.prompt is not None:
            agent.prompt = data.prompt.strip()
        if data.base_url is not None:
            agent.base_url = str(data.base_url)
        if data.frequency is not None:
            agent.frequency = AgentFrequency(data.frequency.value)
        if data.status is not None:
            agent.status = AgentStatus(data.status.value)
        if data.source_id is not None:
            agent.source_id = data.source_id
        if data.next_run_at is not None:
            agent.next_run_at = data.next_run_at

        agent.updated_at = datetime.utcnow()

        await self.db.flush()
        await self.db.refresh(agent)
        return OpportunityAgentResponse.model_validate(agent)

    async def delete_agent(self, agent_id: uuid.UUID, org_id: uuid.UUID) -> bool:
        stmt = (
            select(OpportunityAgent.id)
            .where(
                OpportunityAgent.id == agent_id,
                OpportunityAgent.org_id == org_id,
            )
        )
        result = await self.db.execute(stmt)
        exists = result.scalar_one_or_none()
        if not exists:
            return False
        await self.db.execute(
            delete(OpportunityAgent).where(
                OpportunityAgent.id == agent_id,
                OpportunityAgent.org_id == org_id,
            )
        )
        await self.db.flush()
        return True

    async def list_agent_runs(
        self,
        org_id: uuid.UUID,
        agent_id: Optional[uuid.UUID] = None,
        limit: int = 100,
    ) -> List[OpportunityAgentRunResponse]:
        stmt = (
            select(OpportunityAgentRun)
            .where(OpportunityAgentRun.org_id == org_id)
            .order_by(desc(OpportunityAgentRun.started_at))
            .limit(limit)
        )
        if agent_id:
            stmt = stmt.where(OpportunityAgentRun.agent_id == agent_id)

        result = await self.db.execute(stmt)
        runs = result.scalars().all()
        return [OpportunityAgentRunResponse.model_validate(run) for run in runs]

    async def next_available_identifier(self, org_id: uuid.UUID) -> str:
        stmt = (
            select(func.count(OpportunityTemp.id))
            .where(OpportunityTemp.org_id == org_id)
        )
        result = await self.db.execute(stmt)
        count = result.scalar_one() or 0
        return f"TEMP-{count + 1:05d}"

