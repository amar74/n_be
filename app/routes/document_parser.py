"""
Document Parser Routes
Provides endpoints for parsing documents and extracting structured data.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import List, Dict, Any
from pydantic import BaseModel, HttpUrl

from app.services.document_parser import parse_document, parse_multiple_documents
from app.dependencies.user_auth import get_current_user
from app.dependencies.permissions import get_user_permission
from app.models.user import User
from app.schemas.user_permission import UserPermissionResponse
from app.utils.logger import get_logger

logger = get_logger("document_parser_routes")

router = APIRouter(prefix="/documents", tags=["Document Parser"])


class ParseDocumentRequest(BaseModel):
    url: HttpUrl


class ParseMultipleDocumentsRequest(BaseModel):
    urls: List[HttpUrl]


@router.post("/parse", response_model=Dict[str, Any])
async def parse_single_document(
    request: ParseDocumentRequest,
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["view"]}))
) -> Dict[str, Any]:
    """
    Parse a single document and extract structured data.
    Supports PDF, DOCX, XLS, XLSX files.
    """
    try:
        result = await parse_document(str(request.url))
        if result.get("error"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        return result
    except Exception as e:
        logger.error(f"Error parsing document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse document: {str(e)}"
        )


@router.post("/parse-multiple", response_model=List[Dict[str, Any]])
async def parse_multiple_documents_endpoint(
    request: ParseMultipleDocumentsRequest,
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["view"]}))
) -> List[Dict[str, Any]]:
    """
    Parse multiple documents in parallel.
    Supports PDF, DOCX, XLS, XLSX files.
    """
    try:
        urls = [str(url) for url in request.urls]
        results = await parse_multiple_documents(urls)
        return results
    except Exception as e:
        logger.error(f"Error parsing documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse documents: {str(e)}"
        )

