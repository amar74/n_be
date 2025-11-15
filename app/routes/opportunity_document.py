import os

from fastapi import APIRouter, Depends, HTTPException, status, Path, Query, UploadFile, File, Form
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from app.schemas.opportunity_document import *
from app.services.opportunity_document import OpportunityDocumentService
from app.dependencies.user_auth import get_current_user
from app.dependencies.permissions import get_user_permission
from app.models.user import User
from app.schemas.user_permission import UserPermissionResponse
from app.db.session import get_request_transaction
from app.utils.logger import get_logger

logger = get_logger("opportunity_document_routes")

router = APIRouter(prefix="/opportunities", tags=["Opportunity Documents"])

@router.post("/{opportunity_id}/documents/upload", response_model=OpportunityDocumentResponse, status_code=201)
async def upload_opportunity_document(
    opportunity_id: UUID,
    file: UploadFile = File(...),
    category: str = Form(...),
    purpose: str = Form(...),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["update"]}))
):
    try:
        # Read file content
        file_content = await file.read()
        
        # Create document data
        safe_name = file.filename or "document"
        document_data = OpportunityDocumentCreate(
            file_name=safe_name,
            original_name=safe_name,
            file_type=file.content_type or "application/octet-stream",
            file_size=len(file_content),
            category=category,
            purpose=purpose,
            description=f"Uploaded file: {safe_name}",
            tags=None,
            status="uploaded",
            is_available_for_proposal=True,
        )
        
        service = OpportunityDocumentService(db)
        return await service.create_document(
            opportunity_id,
            document_data,
            current_user,
            file_content=file_content,
            content_type=file.content_type or "application/octet-stream",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error uploading document for opportunity {opportunity_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to upload document")

@router.post("/{opportunity_id}/documents", response_model=OpportunityDocumentResponse, status_code=201)
async def create_opportunity_document(
    opportunity_id: UUID,
    document_data: OpportunityDocumentCreate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["update"]}))
):
    try:
        service = OpportunityDocumentService(db)
        return await service.create_document(opportunity_id, document_data, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating document for opportunity {opportunity_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create document")

@router.get("/{opportunity_id}/documents", response_model=OpportunityDocumentListResponse)
async def get_opportunity_documents(
    opportunity_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["read"]}))
):
    try:
        service = OpportunityDocumentService(db)
        return await service.get_documents(opportunity_id, current_user, page, limit)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting documents for opportunity {opportunity_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get documents")

@router.get("/{opportunity_id}/documents/{document_id}", response_model=OpportunityDocumentResponse)
async def get_opportunity_document(
    opportunity_id: UUID,
    document_id: UUID,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["read"]}))
):
    try:
        service = OpportunityDocumentService(db)
        return await service.get_document(opportunity_id, document_id, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting document {document_id} for opportunity {opportunity_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get document")

@router.put("/{opportunity_id}/documents/{document_id}", response_model=OpportunityDocumentResponse)
async def update_opportunity_document(
    opportunity_id: UUID,
    document_id: UUID,
    update_data: OpportunityDocumentUpdate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["update"]}))
):
    try:
        service = OpportunityDocumentService(db)
        return await service.update_document(opportunity_id, document_id, update_data, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating document {document_id} for opportunity {opportunity_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update document")

@router.delete("/{opportunity_id}/documents/{document_id}", response_model=OpportunityDocumentDeleteResponse)
async def delete_opportunity_document(
    opportunity_id: UUID,
    document_id: UUID,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["update"]}))
):
    try:
        service = OpportunityDocumentService(db)
        return await service.delete_document(opportunity_id, document_id, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting document {document_id} for opportunity {opportunity_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete document")


@router.get("/{opportunity_id}/documents/{document_id}/download")
async def download_opportunity_document(
    opportunity_id: UUID,
    document_id: UUID,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["read"]}))
):
    try:
        service = OpportunityDocumentService(db)
        document = await service.get_document(opportunity_id, document_id, current_user)

        if document.file_url:
            return RedirectResponse(url=document.file_url)

        if not document.file_path or not os.path.exists(document.file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Stored file not found on server"
            )

        filename = document.original_name or document.file_name or "document"
        media_type = document.file_type or "application/octet-stream"

        return FileResponse(
            path=document.file_path,
            media_type=media_type,
            filename=filename
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading document {document_id} for opportunity {opportunity_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to download document")