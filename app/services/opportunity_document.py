import os
import re
import uuid
from datetime import datetime
from typing import Optional

import boto3
from botocore.exceptions import ClientError
from sqlalchemy import and_, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.environment import environment
from app.models.opportunity import Opportunity
from app.models.opportunity_document import OpportunityDocument
from app.models.user import User
from app.schemas.opportunity_document import (
    OpportunityDocumentCreate,
    OpportunityDocumentDeleteResponse,
    OpportunityDocumentListResponse,
    OpportunityDocumentResponse,
    OpportunityDocumentUpdate,
)
from app.db.session import engine
from app.utils.logger import get_logger

logger = get_logger("opportunity_document_service")


class OpportunityDocumentService:
    """Business logic for managing opportunity documents."""

    _schema_ensured: bool = False

    def __init__(self, db: AsyncSession):
        self.db = db
        self.upload_root = os.path.join("uploads", "opportunity_documents")

        self.s3_bucket = environment.AWS_S3_BUCKET_NAME
        self.s3_region = environment.AWS_S3_REGION
        self._s3_enabled = all(
            [
                environment.AWS_ACCESS_KEY_ID,
                environment.AWS_SECRET_ACCESS_KEY,
                self.s3_bucket,
            ]
        )

        if self._s3_enabled:
            self.s3_client = boto3.client(
                "s3",
                aws_access_key_id=environment.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=environment.AWS_SECRET_ACCESS_KEY,
                region_name=self.s3_region,
            )
            logger.info("OpportunityDocumentService initialised with S3 storage")
        else:
            self.s3_client = None
            logger.warning(
                "S3 credentials missing. Falling back to local storage for opportunity documents"
            )

    async def _ensure_schema(self) -> None:
        if OpportunityDocumentService._schema_ensured:
            return

        async with engine.begin() as conn:
            result = await conn.execute(
                text(
                    """
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'opportunity_documents'
                    """
                )
            )
            columns = {row[0] for row in result}

            statements = []
            if "file_name" not in columns:
                statements.append(
                    "ALTER TABLE opportunity_documents ADD COLUMN file_name VARCHAR(255)"
                )
            if "original_name" not in columns:
                statements.append(
                    "ALTER TABLE opportunity_documents ADD COLUMN original_name VARCHAR(255)"
                )
            if "file_type" not in columns:
                statements.append(
                    "ALTER TABLE opportunity_documents ADD COLUMN file_type VARCHAR(100)"
                )
            if "file_path" not in columns:
                statements.append(
                    "ALTER TABLE opportunity_documents ADD COLUMN file_path VARCHAR(500)"
                )
            if "file_url" not in columns:
                statements.append(
                    "ALTER TABLE opportunity_documents ADD COLUMN file_url VARCHAR(500)"
                )
            if "category" not in columns:
                statements.append(
                    "ALTER TABLE opportunity_documents ADD COLUMN category VARCHAR(100) DEFAULT 'Documents & Reports'"
                )
            if "purpose" not in columns:
                statements.append(
                    "ALTER TABLE opportunity_documents ADD COLUMN purpose VARCHAR(100) DEFAULT 'Project Reference'"
                )
            if "description" not in columns:
                statements.append(
                    "ALTER TABLE opportunity_documents ADD COLUMN description TEXT"
                )
            if "status" not in columns:
                statements.append(
                    "ALTER TABLE opportunity_documents ADD COLUMN status VARCHAR(50) DEFAULT 'uploaded'"
                )
            if "is_available_for_proposal" not in columns:
                statements.append(
                    "ALTER TABLE opportunity_documents ADD COLUMN is_available_for_proposal BOOLEAN DEFAULT true"
                )
            if "tags" not in columns:
                statements.append(
                    "ALTER TABLE opportunity_documents ADD COLUMN tags TEXT"
                )
            if "upload_date" not in columns:
                statements.append(
                    "ALTER TABLE opportunity_documents ADD COLUMN upload_date TIMESTAMPTZ DEFAULT now()"
                )
            if "uploaded_at" not in columns:
                statements.append(
                    "ALTER TABLE opportunity_documents ADD COLUMN uploaded_at TIMESTAMPTZ DEFAULT now()"
                )
            if "updated_at" not in columns:
                statements.append(
                    "ALTER TABLE opportunity_documents ADD COLUMN updated_at TIMESTAMPTZ DEFAULT now()"
                )

            for stmt in statements:
                await conn.execute(text(stmt))

            legacy_columns_present = "document_name" in columns

            if statements:
                await conn.execute(
                    text(
                        """
                        UPDATE opportunity_documents
                        SET category = COALESCE(category, 'Documents & Reports'),
                            purpose = COALESCE(purpose, 'Project Reference'),
                            status = COALESCE(status, 'uploaded'),
                            is_available_for_proposal = COALESCE(is_available_for_proposal, true),
                            upload_date = COALESCE(upload_date, created_at),
                            uploaded_at = COALESCE(uploaded_at, created_at),
                            updated_at = COALESCE(updated_at, created_at)
                        """
                    )
                )

                if legacy_columns_present:
                    await conn.execute(
                        text(
                            """
                            UPDATE opportunity_documents
                            SET file_name = COALESCE(file_name, document_name),
                                original_name = COALESCE(original_name, document_name),
                                file_url = COALESCE(file_url, document_url),
                                file_type = COALESCE(file_type, document_type),
                                description = COALESCE(description, CONCAT('Imported legacy document: ', document_name))
                            """
                        )
                    )

            # Relax legacy NOT NULL constraints to avoid insert failures while legacy columns remain.
            try:
                await conn.execute(
                    text(
                        "ALTER TABLE opportunity_documents ALTER COLUMN document_name DROP NOT NULL"
                    )
                )
                await conn.execute(
                    text(
                        "ALTER TABLE opportunity_documents ALTER COLUMN document_type DROP NOT NULL"
                    )
                )
                await conn.execute(
                    text(
                        "ALTER TABLE opportunity_documents ALTER COLUMN file_size TYPE INTEGER USING file_size::INTEGER"
                    )
                )
            except Exception as exc:  # pragma: no cover
                logger.debug("Legacy column alteration skipped: %s", exc)

        OpportunityDocumentService._schema_ensured = True

    async def create_document(
        self,
        opportunity_id: uuid.UUID,
        document_data: OpportunityDocumentCreate,
        current_user: User,
        *,
        file_content: Optional[bytes] = None,
        content_type: Optional[str] = None,
    ) -> OpportunityDocumentResponse:
        await self._ensure_schema()
        opportunity = await self._ensure_opportunity_exists(opportunity_id)

        file_path = document_data.dict().get("file_path")
        file_url = document_data.dict().get("file_url")
        upload_timestamp = datetime.utcnow()

        if file_content is not None:
            storage_name = self._build_storage_filename(document_data.original_name)
            try:
                file_path, file_url = self._upload_file(
                    opportunity_id=opportunity.id,
                    storage_name=storage_name,
                    file_content=file_content,
                    content_type=content_type or document_data.file_type,
                )
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.error(
                    "Failed to store opportunity document %s for opportunity %s: %s",
                    document_data.original_name,
                    opportunity_id,
                    exc,
                    exc_info=True,
                )
                raise
        else:
            if not file_url:
                logger.warning(
                    "Creating opportunity document without file URL or content for opportunity %s",
                    opportunity_id,
                )

        document = OpportunityDocument(
            opportunity_id=opportunity.id,
            file_name=document_data.file_name,
            original_name=document_data.original_name,
            file_type=document_data.file_type,
            file_size=document_data.file_size,
            category=document_data.category,
            purpose=document_data.purpose,
            description=document_data.description,
            tags=document_data.tags,
            status=document_data.status or "uploaded",
            is_available_for_proposal=document_data.is_available_for_proposal,
            file_path=file_path,
            file_url=file_url,
            upload_date=upload_timestamp,
            uploaded_at=upload_timestamp,
        )

        self.db.add(document)
        await self.db.flush()
        await self.db.refresh(document)

        logger.info(
            "Opportunity document %s created for opportunity %s", document.id, opportunity_id
        )

        return OpportunityDocumentResponse.from_orm(document)

    async def get_documents(
        self,
        opportunity_id: uuid.UUID,
        current_user: User,
        page: int = 1,
        limit: int = 10,
    ) -> OpportunityDocumentListResponse:
        await self._ensure_schema()
        await self._ensure_opportunity_exists(opportunity_id)

        count_stmt = select(func.count(OpportunityDocument.id)).where(
            OpportunityDocument.opportunity_id == opportunity_id
        )
        total = (await self.db.execute(count_stmt)).scalar() or 0

        offset = (page - 1) * limit
        stmt = (
            select(OpportunityDocument)
            .where(OpportunityDocument.opportunity_id == opportunity_id)
            .order_by(OpportunityDocument.uploaded_at.desc())
            .offset(offset)
            .limit(limit)
        )
        documents = (await self.db.execute(stmt)).scalars().all()

        total_pages = (total + limit - 1) // limit if limit else 1

        return OpportunityDocumentListResponse(
            documents=[OpportunityDocumentResponse.from_orm(doc) for doc in documents],
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
        )

    async def get_document(
        self,
        opportunity_id: uuid.UUID,
        document_id: uuid.UUID,
        current_user: User,
    ) -> OpportunityDocumentResponse:
        await self._ensure_schema()
        await self._ensure_opportunity_exists(opportunity_id)
        document = await self._get_document(opportunity_id, document_id)
        return OpportunityDocumentResponse.from_orm(document)

    async def update_document(
        self,
        opportunity_id: uuid.UUID,
        document_id: uuid.UUID,
        update_data: OpportunityDocumentUpdate,
        current_user: User,
    ) -> OpportunityDocumentResponse:
        await self._ensure_opportunity_exists(opportunity_id)
        document = await self._get_document(opportunity_id, document_id)

        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(document, field, value)

        document.updated_at = datetime.utcnow()
        await self.db.flush()
        await self.db.refresh(document)

        logger.info(
            "Opportunity document %s updated for opportunity %s", document_id, opportunity_id
        )
        return OpportunityDocumentResponse.from_orm(document)

    async def delete_document(
        self,
        opportunity_id: uuid.UUID,
        document_id: uuid.UUID,
        current_user: User,
    ) -> OpportunityDocumentDeleteResponse:
        await self._ensure_schema()
        await self._ensure_opportunity_exists(opportunity_id)
        document = await self._get_document(opportunity_id, document_id)

        if document.file_path:
            self._delete_file(document.file_path)

        await self.db.delete(document)
        await self.db.flush()

        logger.info(
            "Opportunity document %s deleted for opportunity %s", document_id, opportunity_id
        )

        return OpportunityDocumentDeleteResponse(
            message="Document deleted successfully",
            document_id=document_id,
        )

    async def _ensure_opportunity_exists(self, opportunity_id: uuid.UUID) -> Opportunity:
        stmt = select(Opportunity).where(Opportunity.id == opportunity_id)
        result = await self.db.execute(stmt)
        opportunity = result.scalar_one_or_none()
        if not opportunity:
            raise ValueError("Opportunity not found")
        return opportunity

    async def _get_document(
        self, opportunity_id: uuid.UUID, document_id: uuid.UUID
    ) -> OpportunityDocument:
        stmt = select(OpportunityDocument).where(
            and_(
                OpportunityDocument.id == document_id,
                OpportunityDocument.opportunity_id == opportunity_id,
            )
        )
        result = await self.db.execute(stmt)
        document = result.scalar_one_or_none()
        if not document:
            raise ValueError("Document not found")
        return document

    def _build_storage_filename(self, original_name: str) -> str:
        base_name = os.path.basename(original_name)
        sanitized = re.sub(r"[^A-Za-z0-9_.-]", "_", base_name)
        unique_prefix = uuid.uuid4().hex
        return f"{unique_prefix}_{sanitized}"[:255]

    def _upload_file(
        self,
        *,
        opportunity_id: uuid.UUID,
        storage_name: str,
        file_content: bytes,
        content_type: Optional[str],
    ) -> tuple[str, Optional[str]]:
        if self._s3_enabled and self.s3_client:
            key = f"opportunities/{opportunity_id}/{storage_name}"
            extra_args = {"ContentType": content_type} if content_type else None
            try:
                self.s3_client.put_object(
                    Bucket=self.s3_bucket,
                    Key=key,
                    Body=file_content,
                    **(extra_args or {}),
                )
            except ClientError as exc:
                logger.error("S3 upload failed for key %s: %s", key, exc)
            else:
                region_segment = f".{self.s3_region}" if self.s3_region else ""
                url = f"https://{self.s3_bucket}.s3{region_segment}.amazonaws.com/{key}"
                return key, url

        # Local storage fallback
        opportunity_dir = os.path.join(self.upload_root, str(opportunity_id))
        os.makedirs(opportunity_dir, exist_ok=True)
        local_path = os.path.abspath(os.path.join(opportunity_dir, storage_name))

        with open(local_path, "wb") as destination:
            destination.write(file_content)

        logger.info("Stored opportunity document locally at %s", local_path)
        return local_path, None

    def _delete_file(self, file_path: str) -> None:
        if self._s3_enabled and self.s3_client and not os.path.isabs(file_path):
            try:
                self.s3_client.delete_object(Bucket=self.s3_bucket, Key=file_path)
                logger.info("Deleted opportunity document from S3: %s", file_path)
                return
            except ClientError as exc:  # pragma: no cover - defensive
                logger.warning("Failed to delete S3 object %s: %s", file_path, exc)

        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info("Deleted local opportunity document: %s", file_path)
            except OSError as exc:  # pragma: no cover - defensive
                logger.warning("Failed to delete local file %s: %s", file_path, exc)