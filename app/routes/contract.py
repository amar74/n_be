from __future__ import annotations

from typing import Optional, List, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Path, status, HTTPException, Response, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_request_transaction
from app.dependencies.user_auth import get_current_user
from app.dependencies.permissions import get_user_permission
from app.models.user import User
from app.schemas.auth import AuthUserResponse
from app.schemas.user_permission import UserPermissionResponse
from app.schemas.contract import (
    ContractCreate,
    ContractResponse,
    ContractListResponse,
    ContractUpdate,
    ContractFromProposalRequest,
    ContractAnalysisRequest,
    ContractAnalysisResponse,
    ClauseLibraryCreate,
    ClauseLibraryUpdate,
    ClauseLibraryResponse,
    ClauseLibraryListResponse,
    ClauseCategoryCreate,
    ClauseCategoryResponse,
    ContractWorkflowResponse,
)
from app.models.contract import ContractStatus, RiskLevel
from app.services.contract import ContractService, ClauseLibraryService


router = APIRouter(prefix="/contracts", tags=["Contracts"])


def _contract_service(db: AsyncSession) -> ContractService:
    return ContractService(db)


def _clause_service(db: AsyncSession) -> ClauseLibraryService:
    return ClauseLibraryService(db)


@router.post(
    "/",
    response_model=ContractResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new contract",
)
async def create_contract(
    payload: ContractCreate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: AuthUserResponse = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"contracts": ["edit"]})),
) -> ContractResponse:
    from app.utils.logger import get_logger
    logger = get_logger(__name__)
    
    try:
        logger.info(f"Creating contract with payload: {payload.model_dump_json()}")
        
        user_id_uuid = UUID(current_user.id) if isinstance(current_user.id, str) else current_user.id
        result = await db.execute(select(User).where(User.id == user_id_uuid))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        service = _contract_service(db)
        return await service.create_contract(payload, user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error creating contract: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create contract: {str(e)}"
        )


@router.get(
    "/",
    response_model=ContractListResponse,
    summary="List contracts with pagination",
)
async def list_contracts(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    status_filter: Optional[ContractStatus] = Query(None),
    risk_filter: Optional[RiskLevel] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: AuthUserResponse = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"contracts": ["view"]})),
) -> ContractListResponse:
    from app.utils.logger import get_logger
    logger = get_logger(__name__)
    
    try:
        user_id_uuid = UUID(current_user.id) if isinstance(current_user.id, str) else current_user.id
        result = await db.execute(select(User).where(User.id == user_id_uuid))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        org_id = user.org_id if hasattr(user, 'org_id') else None
        if not org_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must belong to an organization"
            )
        
        service = _contract_service(db)
        return await service.list_contracts(
            org_id=org_id,
            page=page,
            size=size,
            status_filter=status_filter,
            risk_filter=risk_filter,
            search=search,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error listing contracts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list contracts: {str(e)}"
        )


# Clause Library routes - must be defined before /{contract_id} to avoid route conflicts
@router.get(
    "/clauses",
    response_model=ClauseLibraryListResponse,
    summary="List clause library items",
)
async def list_clauses(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: AuthUserResponse = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"contracts": ["view"]})),
) -> ClauseLibraryListResponse:
    from app.utils.logger import get_logger
    logger = get_logger(__name__)
    
    try:
        user_id_uuid = UUID(current_user.id) if isinstance(current_user.id, str) else current_user.id
        result = await db.execute(select(User).where(User.id == user_id_uuid))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        org_id = user.org_id if hasattr(user, 'org_id') else None
        if not org_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must belong to an organization"
            )
        
        service = _clause_service(db)
        return await service.list_clauses(
            org_id=org_id,
            page=page,
            size=size,
            category=category,
            search=search,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error listing clauses: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list clauses: {str(e)}"
        )


@router.get(
    "/clauses/categories",
    response_model=List[ClauseCategoryResponse],
    summary="List clause categories",
)
async def list_clause_categories(
    db: AsyncSession = Depends(get_request_transaction),
    current_user: AuthUserResponse = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"contracts": ["view"]})),
) -> List[ClauseCategoryResponse]:
    from app.utils.logger import get_logger
    logger = get_logger(__name__)
    
    try:
        user_id_uuid = UUID(current_user.id) if isinstance(current_user.id, str) else current_user.id
        result = await db.execute(select(User).where(User.id == user_id_uuid))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        org_id = user.org_id if hasattr(user, 'org_id') else None
        if not org_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must belong to an organization"
            )
        
        service = _clause_service(db)
        return await service.list_categories(org_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error listing categories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list categories: {str(e)}"
        )


@router.post(
    "/clauses/categories",
    response_model=ClauseCategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create clause category",
)
async def create_clause_category(
    payload: ClauseCategoryCreate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: AuthUserResponse = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"contracts": ["edit"]})),
) -> ClauseCategoryResponse:
    from app.utils.logger import get_logger
    logger = get_logger(__name__)
    
    try:
        user_id_uuid = UUID(current_user.id) if isinstance(current_user.id, str) else current_user.id
        result = await db.execute(select(User).where(User.id == user_id_uuid))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        service = _clause_service(db)
        return await service.create_category(payload, user)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error creating category: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create category: {str(e)}"
        )


@router.get(
    "/workflow",
    response_model=ContractWorkflowResponse,
    summary="Get contract workflow information",
)
async def get_contract_workflow(
    contract_id: Optional[UUID] = Query(None, description="Optional contract ID to get workflow for specific contract"),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: AuthUserResponse = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"contracts": ["view"]})),
) -> ContractWorkflowResponse:
    from app.utils.logger import get_logger
    logger = get_logger(__name__)
    
    try:
        user_id_uuid = UUID(current_user.id) if isinstance(current_user.id, str) else current_user.id
        result = await db.execute(select(User).where(User.id == user_id_uuid))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        org_id = user.org_id if hasattr(user, 'org_id') else None
        if not org_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must belong to an organization"
            )
        
        service = _contract_service(db)
        return await service.get_contract_workflow(org_id, contract_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting contract workflow: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get contract workflow: {str(e)}"
        )


@router.get(
    "/clauses/{clause_id}",
    response_model=ClauseLibraryResponse,
    summary="Get clause by ID",
)
async def get_clause(
    clause_id: UUID = Path(..., description="Clause ID"),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: AuthUserResponse = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"contracts": ["view"]})),
) -> ClauseLibraryResponse:
    from app.utils.logger import get_logger
    logger = get_logger(__name__)
    
    try:
        user_id_uuid = UUID(current_user.id) if isinstance(current_user.id, str) else current_user.id
        result = await db.execute(select(User).where(User.id == user_id_uuid))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        org_id = user.org_id if hasattr(user, 'org_id') else None
        if not org_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must belong to an organization"
            )
        
        service = _clause_service(db)
        return await service.get_clause(clause_id, org_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting clause: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get clause: {str(e)}"
        )


@router.post(
    "/clauses",
    response_model=ClauseLibraryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create clause library item",
)
async def create_clause(
    payload: ClauseLibraryCreate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: AuthUserResponse = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"contracts": ["edit"]})),
) -> ClauseLibraryResponse:
    from app.utils.logger import get_logger
    logger = get_logger(__name__)
    
    try:
        user_id_uuid = UUID(current_user.id) if isinstance(current_user.id, str) else current_user.id
        result = await db.execute(select(User).where(User.id == user_id_uuid))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        service = _clause_service(db)
        return await service.create_clause(payload, user)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error creating clause: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create clause: {str(e)}"
        )


@router.put(
    "/clauses/{clause_id}",
    response_model=ClauseLibraryResponse,
    summary="Update clause library item",
)
async def update_clause(
    clause_id: UUID = Path(..., description="Clause ID"),
    payload: ClauseLibraryUpdate = ...,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: AuthUserResponse = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"contracts": ["edit"]})),
) -> ClauseLibraryResponse:
    from app.utils.logger import get_logger
    logger = get_logger(__name__)
    
    try:
        user_id_uuid = UUID(current_user.id) if isinstance(current_user.id, str) else current_user.id
        result = await db.execute(select(User).where(User.id == user_id_uuid))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        org_id = user.org_id if hasattr(user, 'org_id') else None
        if not org_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must belong to an organization"
            )
        
        service = _clause_service(db)
        return await service.update_clause(clause_id, payload, org_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error updating clause: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update clause: {str(e)}"
        )


@router.delete(
    "/clauses/{clause_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete clause library item",
)
async def delete_clause(
    clause_id: UUID = Path(..., description="Clause ID"),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: AuthUserResponse = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"contracts": ["edit"]})),
):
    from app.utils.logger import get_logger
    logger = get_logger(__name__)
    
    try:
        user_id_uuid = UUID(current_user.id) if isinstance(current_user.id, str) else current_user.id
        result = await db.execute(select(User).where(User.id == user_id_uuid))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        org_id = user.org_id if hasattr(user, 'org_id') else None
        if not org_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must belong to an organization"
            )
        
        service = _clause_service(db)
        await service.delete_clause(clause_id, org_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error deleting clause: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete clause: {str(e)}"
        )


@router.get(
    "/{contract_id}",
    response_model=ContractResponse,
    summary="Get contract by ID",
)
async def get_contract(
    contract_id: UUID = Path(..., description="Contract ID"),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: AuthUserResponse = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"contracts": ["view"]})),
) -> ContractResponse:
    from app.utils.logger import get_logger
    logger = get_logger(__name__)
    
    try:
        user_id_uuid = UUID(current_user.id) if isinstance(current_user.id, str) else current_user.id
        result = await db.execute(select(User).where(User.id == user_id_uuid))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        org_id = user.org_id if hasattr(user, 'org_id') else None
        if not org_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must belong to an organization"
            )
        
        service = _contract_service(db)
        return await service.get_contract(contract_id, org_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting contract: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get contract: {str(e)}"
        )


@router.put(
    "/{contract_id}",
    response_model=ContractResponse,
    summary="Update contract",
)
async def update_contract(
    contract_id: UUID = Path(..., description="Contract ID"),
    payload: ContractUpdate = ...,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: AuthUserResponse = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"contracts": ["edit"]})),
) -> ContractResponse:
    from app.utils.logger import get_logger
    logger = get_logger(__name__)
    
    try:
        user_id_uuid = UUID(current_user.id) if isinstance(current_user.id, str) else current_user.id
        result = await db.execute(select(User).where(User.id == user_id_uuid))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        org_id = user.org_id if hasattr(user, 'org_id') else None
        if not org_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must belong to an organization"
            )
        
        service = _contract_service(db)
        return await service.update_contract(contract_id, payload, org_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error updating contract: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update contract: {str(e)}"
        )


@router.delete(
    "/{contract_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete contract",
)
async def delete_contract(
    contract_id: UUID = Path(..., description="Contract ID"),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: AuthUserResponse = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"contracts": ["edit"]})),
):
    from app.utils.logger import get_logger
    logger = get_logger(__name__)
    
    try:
        user_id_uuid = UUID(current_user.id) if isinstance(current_user.id, str) else current_user.id
        result = await db.execute(select(User).where(User.id == user_id_uuid))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        org_id = user.org_id if hasattr(user, 'org_id') else None
        if not org_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must belong to an organization"
            )
        
        service = _contract_service(db)
        await service.delete_contract(contract_id, org_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error deleting contract: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete contract: {str(e)}"
        )


@router.post(
    "/extract-document",
    summary="Extract contract details from uploaded document",
)
async def extract_contract_document(
    file: UploadFile = File(..., description="Contract document file (PDF, DOC, DOCX)"),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: AuthUserResponse = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"contracts": ["edit"]})),
) -> Dict[str, Any]:
    """Extract contract details from uploaded document using AI"""
    from app.utils.logger import get_logger
    logger = get_logger(__name__)
    
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename is required"
            )
        
        # Check file type
        file_extension = file.filename.lower().split('.')[-1]
        if file_extension not in ['pdf', 'doc', 'docx']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF, DOC, and DOCX files are supported"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Check file size (10MB limit)
        if len(file_content) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File size exceeds 10MB limit"
            )
        
        # Extract contract details
        service = _contract_service(db)
        extracted_data = await service.extract_contract_details_from_file(
            file_content=file_content,
            filename=file.filename,
            content_type=file.content_type or f"application/{file_extension}",
        )
        
        return extracted_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error extracting contract details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract contract details: {str(e)}"
        )


@router.post(
    "/from-proposal",
    response_model=ContractResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create contract from proposal",
)
async def create_contract_from_proposal(
    payload: ContractFromProposalRequest,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: AuthUserResponse = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"contracts": ["edit"]})),
) -> ContractResponse:
    from app.utils.logger import get_logger
    logger = get_logger(__name__)
    
    try:
        user_id_uuid = UUID(current_user.id) if isinstance(current_user.id, str) else current_user.id
        result = await db.execute(select(User).where(User.id == user_id_uuid))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        service = _contract_service(db)
        return await service.create_from_proposal(payload, user)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error creating contract from proposal: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create contract from proposal: {str(e)}"
        )


@router.post(
    "/{contract_id}/upload-document",
    response_model=ContractResponse,
    summary="Upload document to existing contract",
)
async def upload_contract_document(
    contract_id: UUID = Path(..., description="Contract ID"),
    file: UploadFile = File(..., description="Contract document file (PDF, DOC, DOCX)"),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: AuthUserResponse = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"contracts": ["edit"]})),
) -> ContractResponse:
    """Upload and attach a document to an existing contract"""
    from app.utils.logger import get_logger
    logger = get_logger(__name__)
    
    try:
        user_id_uuid = UUID(current_user.id) if isinstance(current_user.id, str) else current_user.id
        result = await db.execute(select(User).where(User.id == user_id_uuid))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename is required"
            )
        
        # Check file type
        file_extension = file.filename.lower().split('.')[-1]
        if file_extension not in ['pdf', 'doc', 'docx']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF, DOC, and DOCX files are supported"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Check file size (10MB limit)
        if len(file_content) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File size exceeds 10MB limit"
            )
        
        user_org_id = user.org_id if hasattr(user, 'org_id') else None
        if not user_org_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must belong to an organization"
            )
        
        service = _contract_service(db)
        return await service.update_contract_file(
            contract_id=contract_id,
            org_id=user_org_id,
            file_content=file_content,
            filename=file.filename,
            content_type=file.content_type or f"application/{file_extension}",
            user_id=user_id_uuid,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error uploading contract document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload contract document: {str(e)}"
        )


@router.post(
    "/{contract_id}/analyze",
    response_model=ContractAnalysisResponse,
    summary="Analyze contract with AI",
)
async def analyze_contract(
    contract_id: UUID = Path(..., description="Contract ID"),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: AuthUserResponse = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"contracts": ["edit"]})),
) -> ContractAnalysisResponse:
    from app.utils.logger import get_logger
    logger = get_logger(__name__)
    
    try:
        user_id_uuid = UUID(current_user.id) if isinstance(current_user.id, str) else current_user.id
        result = await db.execute(select(User).where(User.id == user_id_uuid))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        service = _contract_service(db)
        # Always force re-analysis when this endpoint is called
        return await service.analyze_contract(contract_id, user, force_reanalyze=True)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error analyzing contract: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze contract: {str(e)}"
        )


@router.get(
    "/{contract_id}/analysis",
    response_model=ContractAnalysisResponse,
    summary="Get contract analysis",
)
async def get_contract_analysis(
    contract_id: UUID = Path(..., description="Contract ID"),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: AuthUserResponse = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"contracts": ["view"]})),
) -> ContractAnalysisResponse:
    from app.utils.logger import get_logger
    logger = get_logger(__name__)
    
    try:
        user_id_uuid = UUID(current_user.id) if isinstance(current_user.id, str) else current_user.id
        result = await db.execute(select(User).where(User.id == user_id_uuid))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        service = _contract_service(db)
        contract = await service.get_contract(contract_id, user.org_id)
        
        # Retrieve stored analysis from extra_metadata
        analysis_items = []
        executive_summary = None
        if contract.extra_metadata and isinstance(contract.extra_metadata, dict):
            stored_analysis = contract.extra_metadata.get('ai_analysis')
            if stored_analysis:
                if 'items' in stored_analysis:
                    from app.schemas.contract import ContractAnalysisItem
                    try:
                        analysis_items = [
                            ContractAnalysisItem(**item) for item in stored_analysis['items']
                        ]
                        logger.info(f"Retrieved {len(analysis_items)} analysis items from stored analysis for contract {contract_id}")
                    except Exception as e:
                        logger.warning(f"Error parsing stored analysis items: {e}")
                        analysis_items = []
                if 'executive_summary' in stored_analysis:
                    executive_summary = stored_analysis['executive_summary']
        
        return ContractAnalysisResponse(
            red_clauses=contract.red_clauses or 0,
            amber_clauses=contract.amber_clauses or 0,
            green_clauses=contract.green_clauses or 0,
            total_clauses=contract.total_clauses or 0,
            risk_level=contract.risk_level,
            analysis=analysis_items,
            executive_summary=executive_summary,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting contract analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get contract analysis: {str(e)}"
        )

