from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload
import uuid
from datetime import datetime, timezone

from app.models.chat import ChatSession, ChatMessage, ChatSessionStatus
from app.schemas.chat import (
    ChatSessionCreate,
    ChatSessionUpdate,
    ChatMessageCreate,
)


class ChatService:
    @staticmethod
    async def create_session(
        db: AsyncSession,
        session_data: ChatSessionCreate,
        org_id: Optional[uuid.UUID] = None,
        user_id: Optional[uuid.UUID] = None
    ) -> ChatSession:
        """Create a new chat session"""
        session = ChatSession(
            id=uuid.uuid4(),
            org_id=org_id,
            created_by=user_id,
            title=session_data.title,
            description=session_data.description,
            template_id=session_data.template_id,
            selected_topics=session_data.selected_topics or [],
            selected_prompts=session_data.selected_prompts or [],
            module=session_data.module,
            session_metadata=session_data.metadata,
            status=ChatSessionStatus.active,
        )
        db.add(session)
        await db.flush()  # Flush to get the ID, but let middleware handle commit
        await db.refresh(session)
        return session

    @staticmethod
    async def get_session(
        db: AsyncSession,
        session_id: uuid.UUID,
        org_id: Optional[uuid.UUID] = None
    ) -> Optional[ChatSession]:
        """Get a chat session by ID with messages"""
        query = select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.status != ChatSessionStatus.deleted
        )
        
        if org_id:
            query = query.where(ChatSession.org_id == org_id)
        
        query = query.options(selectinload(ChatSession.messages))
        
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_sessions(
        db: AsyncSession,
        org_id: Optional[uuid.UUID] = None,
        user_id: Optional[uuid.UUID] = None,
        module: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> tuple[List[ChatSession], int]:
        """List chat sessions with pagination"""
        query = select(ChatSession).where(
            ChatSession.status != ChatSessionStatus.deleted
        )
        
        if org_id:
            query = query.where(ChatSession.org_id == org_id)
        
        if user_id:
            query = query.where(ChatSession.created_by == user_id)
        
        if module:
            query = query.where(ChatSession.module == module)
        
        if status:
            try:
                status_enum = ChatSessionStatus(status)
                query = query.where(ChatSession.status == status_enum)
            except ValueError:
                pass
        
        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0
        
        # Get sessions ordered by last message time
        query = query.order_by(desc(ChatSession.last_message_at), desc(ChatSession.created_at))
        query = query.limit(limit).offset(offset)
        
        result = await db.execute(query)
        sessions = list(result.scalars().all())
        
        # Get message counts for each session
        for session in sessions:
            msg_count_query = select(func.count(ChatMessage.id)).where(
                ChatMessage.session_id == session.id
            )
            msg_count_result = await db.execute(msg_count_query)
            session.message_count = msg_count_result.scalar() or 0
        
        return sessions, total

    @staticmethod
    async def update_session(
        db: AsyncSession,
        session_id: uuid.UUID,
        update_data: ChatSessionUpdate,
        org_id: Optional[uuid.UUID] = None
    ) -> Optional[ChatSession]:
        """Update a chat session"""
        query = select(ChatSession).where(ChatSession.id == session_id)
        
        if org_id:
            query = query.where(ChatSession.org_id == org_id)
        
        result = await db.execute(query)
        session = result.scalar_one_or_none()
        
        if not session:
            return None
        
        if update_data.title is not None:
            session.title = update_data.title
        if update_data.description is not None:
            session.description = update_data.description
        if update_data.status is not None:
            try:
                session.status = ChatSessionStatus(update_data.status)
            except ValueError:
                pass
        if update_data.metadata is not None:
            session.session_metadata = update_data.metadata
        
        session.updated_at = datetime.now(timezone.utc)
        
        await db.flush()  # Flush to persist changes, let middleware handle commit
        await db.refresh(session)
        return session

    @staticmethod
    async def delete_session(
        db: AsyncSession,
        session_id: uuid.UUID,
        org_id: Optional[uuid.UUID] = None
    ) -> bool:
        """Soft delete a chat session"""
        query = select(ChatSession).where(ChatSession.id == session_id)
        
        if org_id:
            query = query.where(ChatSession.org_id == org_id)
        
        result = await db.execute(query)
        session = result.scalar_one_or_none()
        
        if not session:
            return False
        
        session.status = ChatSessionStatus.deleted
        session.updated_at = datetime.now(timezone.utc)
        
        await db.flush()  # Flush to persist changes, let middleware handle commit
        return True

    @staticmethod
    async def add_message(
        db: AsyncSession,
        session_id: uuid.UUID,
        message_data: ChatMessageCreate
    ) -> Optional[ChatMessage]:
        """Add a message to a chat session"""
        # Verify session exists and is active
        session_query = select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.status != ChatSessionStatus.deleted
        )
        session_result = await db.execute(session_query)
        session = session_result.scalar_one_or_none()
        
        if not session:
            return None
        
        message = ChatMessage(
            id=uuid.uuid4(),
            session_id=session_id,
            role=message_data.role,
            content=message_data.content,
            thinking_mode=message_data.thinking_mode,
            message_metadata=message_data.metadata,
        )
        
        db.add(message)
        
        # Update session's last_message_at
        session.last_message_at = datetime.now(timezone.utc)
        session.updated_at = datetime.now(timezone.utc)
        
        await db.flush()  # Flush to persist changes, let middleware handle commit
        await db.refresh(message)
        return message

    @staticmethod
    async def get_messages(
        db: AsyncSession,
        session_id: uuid.UUID,
        limit: int = 100,
        offset: int = 0
    ) -> List[ChatMessage]:
        """Get messages for a chat session"""
        query = select(ChatMessage).where(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.created_at).limit(limit).offset(offset)
        
        result = await db.execute(query)
        return list(result.scalars().all())

