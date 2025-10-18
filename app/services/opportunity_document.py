from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
import uuid
import os
import shutil
from datetime import datetime

from app.models.opportunity import Opportunity
from app.models.opportunity_document import OpportunityDocument
from app.models.user import User
from app.schemas.opportunity_document import (
    OpportunityDocumentCreate,
    OpportunityDocumentUpdate,
    OpportunityDocumentResponse,
    OpportunityDocumentListResponse,
    OpportunityDocumentDeleteResponse
)
from app.utils.logger import get_logger

logger = get_logger("opportunity_document_service")

class OpportunityDocumentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.upload_dir = "uploads/opportunity_documents"

    async def create_document(
        self, 
        opportunity_id: uuid.UUID, 
        document_data: OpportunityDocumentCreate,
        current_user: User
    ) -> OpportunityDocumentResponse:
        # Verify opportunity exists and user has access
        stmt = select(Opportunity).where(Opportunity.id == opportunity_id)
        result = await self.db.execute(stmt)
        opportunity = result.scalar_one_or_none()
        
        if not opportunity:
            raise ValueError("Opportunity not found")
        
        # Create document record
        document = OpportunityDocument(
            opportunity_id=opportunity_id,
            file_name=document_data.file_name,
            original_name=document_data.original_name,
            file_type=document_data.file_type,
            file_size=document_data.file_size,
            category=document_data.category,
            purpose=document_data.purpose,
            description=document_data.description,
            tags=document_data.tags,
            status="uploaded"
        )
        
        self.db.add(document)
        await self.db.flush()  # Flush to get the ID
        await self.db.refresh(document)
        
        logger.info(f"Created document {document.id} for opportunity {opportunity_id}")
        
        return OpportunityDocumentResponse.from_orm(document)

    async def get_documents(
        self, 
        opportunity_id: uuid.UUID, 
        current_user: User,
        page: int = 1,
        limit: int = 10
    ) -> OpportunityDocumentListResponse:
        # Verify opportunity exists and user has access
        stmt = select(Opportunity).where(Opportunity.id == opportunity_id)
        result = await self.db.execute(stmt)
        opportunity = result.scalar_one_or_none()
        
        if not opportunity:
            raise ValueError("Opportunity not found")
        
        # Get total count
        count_stmt = select(func.count(OpportunityDocument.id)).where(
            OpportunityDocument.opportunity_id == opportunity_id
        )
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar()
        
        # Get documents with pagination
        offset = (page - 1) * limit
        stmt = select(OpportunityDocument).where(
            OpportunityDocument.opportunity_id == opportunity_id
        ).order_by(OpportunityDocument.uploaded_at.desc()).offset(offset).limit(limit)
        
        result = await self.db.execute(stmt)
        documents = result.scalars().all()
        
        total_pages = (total + limit - 1) // limit
        
        return OpportunityDocumentListResponse(
            documents=[OpportunityDocumentResponse.from_orm(doc) for doc in documents],
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages
        )

    async def get_document(
        self, 
        opportunity_id: uuid.UUID, 
        document_id: uuid.UUID,
        current_user: User
    ) -> OpportunityDocumentResponse:
        # Verify opportunity exists and user has access
        stmt = select(Opportunity).where(Opportunity.id == opportunity_id)
        result = await self.db.execute(stmt)
        opportunity = result.scalar_one_or_none()
        
        if not opportunity:
            raise ValueError("Opportunity not found")
        
        # Get document
        stmt = select(OpportunityDocument).where(
            and_(
                OpportunityDocument.id == document_id,
                OpportunityDocument.opportunity_id == opportunity_id
            )
        )
        result = await self.db.execute(stmt)
        document = result.scalar_one_or_none()
        
        if not document:
            raise ValueError("Document not found")
        
        return OpportunityDocumentResponse.from_orm(document)

    async def update_document(
        self, 
        opportunity_id: uuid.UUID, 
        document_id: uuid.UUID,
        update_data: OpportunityDocumentUpdate,
        current_user: User
    ) -> OpportunityDocumentResponse:
        # Verify opportunity exists and user has access
        stmt = select(Opportunity).where(Opportunity.id == opportunity_id)
        result = await self.db.execute(stmt)
        opportunity = result.scalar_one_or_none()
        
        if not opportunity:
            raise ValueError("Opportunity not found")
        
        # Get document
        stmt = select(OpportunityDocument).where(
            and_(
                OpportunityDocument.id == document_id,
                OpportunityDocument.opportunity_id == opportunity_id
            )
        )
        result = await self.db.execute(stmt)
        document = result.scalar_one_or_none()
        
        if not document:
            raise ValueError("Document not found")
        
        # Update document
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(document, field, value)
        
        await self.db.flush()
        await self.db.refresh(document)
        
        logger.info(f"Updated document {document_id} for opportunity {opportunity_id}")
        
        return OpportunityDocumentResponse.from_orm(document)

    async def delete_document(
        self, 
        opportunity_id: uuid.UUID, 
        document_id: uuid.UUID,
        current_user: User
    ) -> OpportunityDocumentDeleteResponse:
        # Verify opportunity exists and user has access
        stmt = select(Opportunity).where(Opportunity.id == opportunity_id)
        result = await self.db.execute(stmt)
        opportunity = result.scalar_one_or_none()
        
        if not opportunity:
            raise ValueError("Opportunity not found")
        
        # Get document
        stmt = select(OpportunityDocument).where(
            and_(
                OpportunityDocument.id == document_id,
                OpportunityDocument.opportunity_id == opportunity_id
            )
        )
        result = await self.db.execute(stmt)
        document = result.scalar_one_or_none()
        
        if not document:
            raise ValueError("Document not found")
        
        # Delete file if it exists
        if document.file_path and os.path.exists(document.file_path):
            try:
                os.remove(document.file_path)
            except Exception as e:
                logger.warning(f"Failed to delete file {document.file_path}: {e}")
        
        # Delete document record
        await self.db.delete(document)
        await self.db.flush()
        
        logger.info(f"Deleted document {document_id} for opportunity {opportunity_id}")
        
        return OpportunityDocumentDeleteResponse(
            message="Document deleted successfully",
            document_id=document_id
        )