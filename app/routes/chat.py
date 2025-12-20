from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uuid

from app.db.session import get_request_transaction
from app.dependencies.user_auth import get_current_user, AuthUserResponse
from app.schemas.chat import (
    ChatSessionCreate,
    ChatSessionUpdate,
    ChatSessionResponse,
    ChatSessionWithMessages,
    ChatSessionListResponse,
    ChatMessageCreate,
    ChatMessageResponse,
    AIChatRequest,
    AIChatResponse,
)
from app.services.chat_service import ChatService
from app.services.ai_chat_service import ai_chat_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/chat", tags=["Chat"])


@router.post("/sessions", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_chat_session(
    session_data: ChatSessionCreate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: AuthUserResponse = Depends(get_current_user),
):
    """Create a new chat session"""
    try:
        org_id = getattr(current_user, 'org_id', None)
        if org_id:
            org_id = uuid.UUID(str(org_id))
        
        user_id = getattr(current_user, 'user_id', None)
        if user_id:
            user_id = uuid.UUID(str(user_id))
        
        session = await ChatService.create_session(
            db=db,
            session_data=session_data,
            org_id=org_id,
            user_id=user_id
        )
        
        return ChatSessionResponse(
            id=session.id,
            org_id=session.org_id,
            created_by=session.created_by,
            title=session.title,
            description=session.description,
            template_id=session.template_id,
            selected_topics=session.selected_topics or [],
            selected_prompts=session.selected_prompts or [],
            module=session.module,
            metadata=session.session_metadata,
            status=session.status.value,
            created_at=session.created_at,
            updated_at=session.updated_at,
            last_message_at=session.last_message_at,
            message_count=0,
        )
    except Exception as e:
        logger.error(f"Error creating chat session: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create chat session: {str(e)}"
        )


@router.get("/sessions", response_model=ChatSessionListResponse)
async def list_chat_sessions(
    module: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: AuthUserResponse = Depends(get_current_user),
):
    """List chat sessions"""
    try:
        org_id = getattr(current_user, 'org_id', None)
        if org_id:
            org_id = uuid.UUID(str(org_id))
        
        user_id = getattr(current_user, 'user_id', None)
        if user_id:
            user_id = uuid.UUID(str(user_id))
        
        sessions, total = await ChatService.list_sessions(
            db=db,
            org_id=org_id,
            user_id=user_id,
            module=module,
            status=status,
            limit=limit,
            offset=offset
        )
        
        session_responses = []
        for session in sessions:
            session_responses.append(ChatSessionResponse(
                id=session.id,
                org_id=session.org_id,
                created_by=session.created_by,
                title=session.title,
                description=session.description,
                template_id=session.template_id,
                selected_topics=session.selected_topics or [],
                selected_prompts=session.selected_prompts or [],
                module=session.module,
                metadata=session.session_metadata,
                status=session.status.value,
                created_at=session.created_at,
                updated_at=session.updated_at,
                last_message_at=session.last_message_at,
                message_count=getattr(session, 'message_count', 0),
            ))
        
        return ChatSessionListResponse(sessions=session_responses, total=total)
    except Exception as e:
        logger.error(f"Error listing chat sessions: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list chat sessions: {str(e)}"
        )


@router.get("/sessions/{session_id}", response_model=ChatSessionWithMessages)
async def get_chat_session(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: AuthUserResponse = Depends(get_current_user),
):
    """Get a chat session with messages"""
    try:
        org_id = getattr(current_user, 'org_id', None)
        if org_id:
            org_id = uuid.UUID(str(org_id))
        
        session = await ChatService.get_session(
            db=db,
            session_id=session_id,
            org_id=org_id
        )
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        messages = []
        for msg in session.messages:
            messages.append(ChatMessageResponse(
                id=msg.id,
                session_id=msg.session_id,
                role=msg.role,
                content=msg.content,
                thinking_mode=msg.thinking_mode,
                metadata=msg.message_metadata,
                created_at=msg.created_at,
            ))
        
        return ChatSessionWithMessages(
            id=session.id,
            org_id=session.org_id,
            created_by=session.created_by,
            title=session.title,
            description=session.description,
            template_id=session.template_id,
            selected_topics=session.selected_topics or [],
            selected_prompts=session.selected_prompts or [],
            module=session.module,
            metadata=session.session_metadata,
            status=session.status.value,
            created_at=session.created_at,
            updated_at=session.updated_at,
            last_message_at=session.last_message_at,
            message_count=len(session.messages),
            messages=messages,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chat session: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get chat session: {str(e)}"
        )


@router.put("/sessions/{session_id}", response_model=ChatSessionResponse)
async def update_chat_session(
    session_id: uuid.UUID,
    update_data: ChatSessionUpdate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: AuthUserResponse = Depends(get_current_user),
):
    """Update a chat session"""
    try:
        org_id = getattr(current_user, 'org_id', None)
        if org_id:
            org_id = uuid.UUID(str(org_id))
        
        session = await ChatService.update_session(
            db=db,
            session_id=session_id,
            update_data=update_data,
            org_id=org_id
        )
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        # Get message count
        messages = await ChatService.get_messages(db=db, session_id=session_id)
        
        return ChatSessionResponse(
            id=session.id,
            org_id=session.org_id,
            created_by=session.created_by,
            title=session.title,
            description=session.description,
            template_id=session.template_id,
            selected_topics=session.selected_topics or [],
            selected_prompts=session.selected_prompts or [],
            module=session.module,
            metadata=session.session_metadata,
            status=session.status.value,
            created_at=session.created_at,
            updated_at=session.updated_at,
            last_message_at=session.last_message_at,
            message_count=len(messages),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating chat session: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update chat session: {str(e)}"
        )


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_session(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: AuthUserResponse = Depends(get_current_user),
):
    """Delete a chat session"""
    try:
        org_id = getattr(current_user, 'org_id', None)
        if org_id:
            org_id = uuid.UUID(str(org_id))
        
        success = await ChatService.delete_session(
            db=db,
            session_id=session_id,
            org_id=org_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting chat session: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete chat session: {str(e)}"
        )


@router.post("/sessions/{session_id}/messages", response_model=ChatMessageResponse, status_code=status.HTTP_201_CREATED)
async def add_message(
    session_id: uuid.UUID,
    message_data: ChatMessageCreate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: AuthUserResponse = Depends(get_current_user),
):
    """Add a message to a chat session"""
    try:
        message = await ChatService.add_message(
            db=db,
            session_id=session_id,
            message_data=message_data
        )
        
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found or inactive"
            )
        
        return ChatMessageResponse(
            id=message.id,
            session_id=message.session_id,
            role=message.role,
            content=message.content,
            thinking_mode=message.thinking_mode,
            metadata=message.message_metadata,
            created_at=message.created_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding message: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add message: {str(e)}"
        )


@router.post("/generate-response", response_model=AIChatResponse, operation_id="generateAIChatResponse")
async def generate_ai_response(
    request: AIChatRequest,
    current_user: AuthUserResponse = Depends(get_current_user),
):
    """
    Generate an AI-powered response for chat messages.
    Supports content enrichment, content development, suggestions, auto enhancement, ideas, and more.
    """
    try:
        response = await ai_chat_service.generate_response(
            user_message=request.user_message,
            module=request.module,
            thinking_mode=request.thinking_mode or "normal",
            conversation_history=request.conversation_history,
            system_prompt=request.system_prompt,
            use_case=request.use_case
        )
        
        return AIChatResponse(
            response=response,
            thinking_mode=request.thinking_mode or "normal",
            use_case=request.use_case
        )
    except Exception as e:
        logger.error(f"Error generating AI response: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate AI response: {str(e)}"
        )

